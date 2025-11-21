import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import torch
import whisper
from moviepy.editor import VideoFileClip
from firebase_admin import credentials, db
import firebase_admin
from dotenv import load_dotenv

try:
    from faster_whisper import WhisperModel as FasterWhisperModel
except ImportError:  # pragma: no cover - optional dep
    FasterWhisperModel = None

load_dotenv()

# ------------------------------------
# 📌 프로젝트별 설정값
# ------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CRED_PATH = BASE_DIR / "serviceAccountKey.json"

FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
FIREBASE_USER_ID = os.getenv("FIREBASE_USER_ID", "default_user")
INPUT_VIDEO_DIR = Path(os.getenv("STT_INPUT_VIDEO_DIR", BASE_DIR / "videos"))
OUTPUT_AUDIO_DIR = Path(os.getenv("STT_OUTPUT_AUDIO_DIR", BASE_DIR / "results/audio_wav"))
OUTPUT_JSON_DIR = Path(os.getenv("STT_OUTPUT_JSON_DIR", BASE_DIR / "results/stt_json"))
CREDENTIAL_PATH = Path(os.getenv("FIREBASE_CRED_PATH", DEFAULT_CRED_PATH))
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")  # 'base', 'small', 'medium' 등 선택
WHISPER_VERBOSE = os.getenv("WHISPER_VERBOSE", "false").lower() in {"1", "true", "yes", "on"}
STT_ENGINE = os.getenv("STT_ENGINE", "faster").lower()
if STT_ENGINE not in {"faster", "openai"}:
    STT_ENGINE = "faster"
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "auto").lower()
FASTER_WHISPER_COMPUTE_TYPE = os.getenv("FASTER_WHISPER_COMPUTE_TYPE", "int8")

_WHISPER_MODEL = None
_FASTER_WHISPER_MODEL = None
_stt_progress = {"progress": 0, "stage": "idle"}
_stt_last_logged = {"progress": -1, "stage": ""}


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def _resolve_device() -> str:
    if WHISPER_DEVICE != "auto":
        return WHISPER_DEVICE
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def set_stt_progress(progress: Optional[int] = None, stage: Optional[str] = None):
    global _stt_last_logged
    if progress is not None:
        _stt_progress["progress"] = _clamp(progress)
    if stage:
        _stt_progress["stage"] = stage

    if (
        _stt_progress["progress"] != _stt_last_logged["progress"]
        or _stt_progress["stage"] != _stt_last_logged["stage"]
    ):
        print(f"[STT] { _stt_progress['progress']:>3}% - {_stt_progress['stage']}")
        _stt_last_logged = dict(_stt_progress)


def get_stt_progress():
    return dict(_stt_progress)


def reset_stt_progress():
    set_stt_progress(0, "idle")

# ------------------------------------
# 1. Firebase 초기화 및 DB 함수
# ------------------------------------
def initialize_firebase() -> bool:
    """Firebase Admin SDK를 초기화합니다."""
    try:
        if firebase_admin._apps:
            return True

        if not FIREBASE_DATABASE_URL:
            print("⚠️ FIREBASE_DATABASE_URL 환경변수가 설정되지 않았습니다.")
            return False

        if not CREDENTIAL_PATH.exists():
            print(f"⚠️ Firebase 서비스 키를 찾을 수 없습니다: {CREDENTIAL_PATH}")
            return False

        cred = credentials.Certificate(str(CREDENTIAL_PATH))
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})
        print("✅ Firebase Admin SDK 초기화 완료.")
        return True
    except Exception as e:
        print(f"❌ Firebase 초기화 실패: 오류: {e}")
        return False

def upload_to_firebase_text(user_id: str, file_name: str, stt_data: dict):
    """STT 전사 결과 중 'full_text'만 DB의 stt_raw 경로에 업로드합니다."""
    ref_path_text = f'users/{user_id}/presentations/{file_name}/stt_raw/full_text'
    ref_path_timestamps = f'users/{user_id}/presentations/{file_name}/stt_raw/timestamps'

    try:
        # 1. full_text 저장
        db.reference(ref_path_text).set(stt_data['full_text'])
        # 2. 단어별 타임스탬프 저장
        db.reference(ref_path_timestamps).set(stt_data['words'])
        print(f"    -> [DB] 텍스트 및 타임스탬프 업로드 완료.")
        
    except Exception as e:
        print(f"    -> [DB] Firebase 업로드 실패. 오류: {e}")

# ------------------------------------
# 2. 오디오 추출 함수
# ------------------------------------
def extract_audio(video_path: Path, output_audio_path: Path) -> bool:
    try:
        with VideoFileClip(str(video_path)) as video_clip:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(
                str(output_audio_path),
                codec='pcm_s16le',
                fps=16000,
                verbose=False,
                logger=None
            )
        return True
    except Exception as e:
        print(f"  ❌ 오디오 추출 실패: {e}")
        return False

# ------------------------------------
# 3. Whisper STT 전사 및 분석 자료 생성 함수
# ------------------------------------
def get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        print(f"  -> [STT] Whisper {WHISPER_MODEL_SIZE} 모델 로딩 중...")
        _WHISPER_MODEL = whisper.load_model(WHISPER_MODEL_SIZE)
    return _WHISPER_MODEL


def get_faster_whisper_model():
    global _FASTER_WHISPER_MODEL
    if FasterWhisperModel is None:
        raise RuntimeError("faster-whisper 패키지가 설치되어 있지 않습니다. pip install faster-whisper")
    if _FASTER_WHISPER_MODEL is None:
        device = _resolve_device()
        if device == "mps":
            print("⚠️ faster-whisper는 MPS를 지원하지 않아 CPU로 대체합니다. (.env에서 WHISPER_DEVICE=cpu 지정 가능)")
            device = "cpu"
        print(f"  -> [STT] faster-whisper {WHISPER_MODEL_SIZE} 모델 로딩 중... (device={device}, compute={FASTER_WHISPER_COMPUTE_TYPE})")
        _FASTER_WHISPER_MODEL = FasterWhisperModel(
            WHISPER_MODEL_SIZE,
            device=device,
            compute_type=FASTER_WHISPER_COMPUTE_TYPE,
        )
    return _FASTER_WHISPER_MODEL


def transcribe_with_openai(audio_path: Path):
    print(f"  -> [STT] Whisper {WHISPER_MODEL_SIZE} (openai) 모델 로딩 및 전사 중...")
    try:
        model = get_whisper_model()
        set_stt_progress(50, "Whisper 추론 중")
        result = model.transcribe(
            str(audio_path),
            language="ko",
            word_timestamps=True,
            verbose=WHISPER_VERBOSE
        )

        full_text = result.get('text', '').strip()
        word_timestamps = []
        duration_sec = 0.0

        for segment in result.get('segments', []):
            if 'words' in segment:
                word_timestamps.extend(segment['words'])

        if word_timestamps:
            duration_sec = word_timestamps[-1].get('end', 0.0)

        analysis_data = {
            "full_text": full_text,
            "words": word_timestamps,
            "duration_sec": duration_sec,
            "word_count": len(word_timestamps)
        }

        print("  ✅ STT 전사 완료.")
        set_stt_progress(65, "STT 결과 정리")
        return analysis_data

    except Exception as e:
        print(f"  ❌ Whisper 전사 실패: {e}")
        set_stt_progress(50, "Whisper 오류")
        return None

# ------------------------------------
# 4. 통합 배치 처리 함수
# ------------------------------------
def process_single_video(
    video_path: Path,
    user_id: Optional[str] = None,
    output_audio_dir: Optional[Path] = None,
    output_json_dir: Optional[Path] = None,
    upload_to_firebase: bool = True,
    output_basename: Optional[str] = None,
):
    """단일 영상 파일에 대한 STT 분석 및 결과 저장."""
    set_stt_progress(0, "파일 검증")
    video_path = Path(video_path)
    if not video_path.exists():
        set_stt_progress(0, "파일 없음")
        raise FileNotFoundError(f"영상 파일을 찾을 수 없습니다: {video_path}")

    user_id = user_id or FIREBASE_USER_ID
    output_audio_dir = Path(output_audio_dir or OUTPUT_AUDIO_DIR)
    output_json_dir = Path(output_json_dir or OUTPUT_JSON_DIR)

    output_audio_dir.mkdir(parents=True, exist_ok=True)
    output_json_dir.mkdir(parents=True, exist_ok=True)

    base_name = output_basename or video_path.stem
    audio_path = output_audio_dir / f"{base_name}.wav"
    txt_path = output_json_dir / f"{base_name}_text.txt"
    json_path = output_json_dir / f"{base_name}_analysis.json"

    set_stt_progress(5, "오디오 추출")
    if not extract_audio(video_path, audio_path):
        set_stt_progress(5, "오디오 추출 실패")
        raise RuntimeError("오디오 추출에 실패했습니다.")

    set_stt_progress(30, "Whisper 로딩")
    stt_result = whisper_transcribe(audio_path)
    if not stt_result:
        set_stt_progress(30, "STT 실패")
        raise RuntimeError("STT 전사에 실패했습니다.")

    set_stt_progress(70, "결과 저장")
    try:
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(stt_result['full_text'])
        print(f"  ✅ 텍스트 파일 저장 완료: {txt_path}")
    except Exception as e:
        print(f"  ❌ TXT 파일 저장 실패: {e}")

    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(stt_result, f, ensure_ascii=False, indent=4)
        print(f"  ✅ 분석 자료 JSON 저장 완료: {json_path}")
    except Exception as e:
        print(f"  ❌ JSON 파일 저장 실패: {e}")

    stt_result["file_paths"] = {
        "audio": str(audio_path),
        "text": str(txt_path),
        "json": str(json_path),
    }
    stt_result["base_name"] = base_name

    if upload_to_firebase:
        set_stt_progress(85, "Firebase 업로드 준비")
        is_firebase_ok = initialize_firebase()
        if is_firebase_ok:
            print("  [Step 4/4] Firebase DB에 텍스트 업로드 중...")
            upload_to_firebase_text(user_id, base_name, stt_result)
        else:
            print("  ⚠️ Firebase 설정이 올바르지 않아 업로드를 건너뜁니다.")

    set_stt_progress(100, "완료")
    return stt_result


def process_multiple_videos(input_dir, output_dir_audio, output_dir_json, user_id):
    input_dir = Path(input_dir)
    video_files = [f for f in input_dir.glob("*.mp4")]

    if not video_files:
        print(f"경고: '{input_dir}'에서 처리할 MP4 영상 파일을 찾을 수 없습니다.")
        return

    print(f"총 {len(video_files)}개의 영상을 처리합니다. 사용자 ID: {user_id}")

    for i, video_file in enumerate(video_files, start=1):
        print(f"\n--- [{i}/{len(video_files)}] {video_file.name} 처리 시작 ---")
        try:
            process_single_video(
                video_file,
                user_id=user_id,
                output_audio_dir=output_dir_audio,
                output_json_dir=output_dir_json,
            )
        except Exception as exc:
            print(f"  ❌ {video_file.name} 처리 실패: {exc}")

def transcribe_with_faster(audio_path: Path):
    try:
        model = get_faster_whisper_model()
        set_stt_progress(45, "faster-whisper 추론 준비")
        segments, info = model.transcribe(
            str(audio_path),
            language="ko",
            beam_size=5,
            word_timestamps=True
        )
        collected_segments: List[Any] = list(segments)
        set_stt_progress(55, "faster-whisper 추론 중")

        full_text = " ".join(seg.text.strip() for seg in collected_segments).strip()
        word_timestamps: List[Dict[str, Any]] = []
        for seg in collected_segments:
            if seg.words:
                for word in seg.words:
                    word_timestamps.append({
                        "word": word.word.strip(),
                        "start": float(word.start) if word.start is not None else None,
                        "end": float(word.end) if word.end is not None else None,
                        "probability": float(getattr(word, "probability", 0.0))
                    })

        duration_sec = float(info.duration) if info and info.duration else 0.0
        if not duration_sec and word_timestamps:
            duration_sec = float(word_timestamps[-1].get("end") or 0.0)

        analysis_data = {
            "full_text": full_text,
            "words": word_timestamps,
            "duration_sec": duration_sec,
            "word_count": len(word_timestamps)
        }

        set_stt_progress(65, "STT 결과 정리")
        return analysis_data
    except Exception as e:
        print(f"  ❌ faster-whisper 전사 실패: {e}")
        set_stt_progress(50, "Whisper 오류")
        return None


def whisper_transcribe(audio_path: Path):
    if STT_ENGINE == "openai":
        return transcribe_with_openai(audio_path)
    result = transcribe_with_faster(audio_path)
    if result is None:
        print("⚠️ faster-whisper 실패, 기본 Whisper로 재시도합니다.")
        return transcribe_with_openai(audio_path)
    return result


if __name__ == "__main__":
    process_multiple_videos(INPUT_VIDEO_DIR, OUTPUT_AUDIO_DIR, OUTPUT_JSON_DIR, FIREBASE_USER_ID)
