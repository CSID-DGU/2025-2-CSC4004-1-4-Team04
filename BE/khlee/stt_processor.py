import os
import json
import whisper
from moviepy.editor import VideoFileClip
from firebase_admin import credentials, db
import firebase_admin
import warnings
warnings.filterwarnings("ignore")

# -----------------------------------------------------------------
# 📌 프로젝트별 설정값 (수정 필수)
# -----------------------------------------------------------------
FIREBASE_DATABASE_URL = "https://csc4004-1-4-team04-default-rtdb.firebaseio.com/" 
USER_ID = "2021111985_JungHyeon"
CREDENTIAL_PATH = "/content/drive/MyDrive/AI_Coach_Data/Firebase_Keys/csc4004-1-4-team04-adminsdk.json" 
INPUT_VIDEO_DIR = "/content/drive/MyDrive/AI_Coach_Data/videos"
OUTPUT_AUDIO_DIR = "/content/drive/MyDrive/AI_Coach_Data/results/audio_wav"
OUTPUT_JSON_DIR = "/content/drive/MyDrive/AI_Coach_Data/results/stt_json"
WHISPER_MODEL_SIZE = "small" 
PAUSE_THRESHOLD_SEC = 2.0  # 2초 이상 무음은 끊김으로 기록

# -----------------------------------------------------------------
# 1. WPM 및 무음 구간 분석 로직 (2주차 핵심 기능)
# -----------------------------------------------------------------
def analyze_voice_rhythm(stt_result_data: dict) -> dict:
    """
    STT 전사 결과(단어별 타임스탬프)를 기반으로 WPM 및 무음 구간을 분석합니다.
    """
    words = stt_result_data.get('words', [])
    total_duration = stt_result_data.get('duration_sec', 0.0)
    word_count = len(words)

    if not words or total_duration == 0:
         return {
            "wpm": 0, "pause_events": [], "avg_pause_duration": 0.0, "long_pause_count": 0,
            "full_text": stt_result_data.get('full_text', '') 
        }

    # WPM 계산
    wpm = round((word_count / total_duration) * 60) if total_duration > 0 else 0

    pause_events = []
    all_pause_durations = []
    
    for i in range(len(words) - 1):
        current_word_end = words[i].get('end', 0.0)
        next_word_start = words[i+1].get('start', 0.0)
        gap_duration = next_word_start - current_word_end
        
        if gap_duration > 0:
            all_pause_durations.append(gap_duration)
        
        # 2초 이상 지속되는 무음 구간을 '끊김'으로 기록
        if gap_duration >= PAUSE_THRESHOLD_SEC:
            pause_events.append({
                "start_sec": round(current_word_end, 2),
                "end_sec": round(next_word_start, 2),
                "duration": round(gap_duration, 2)
            })

    total_pause_duration = sum(all_pause_durations)
    total_pause_count = len(all_pause_durations)
    
    avg_pause_duration = round(total_pause_duration / total_pause_count, 2) if total_pause_count > 0 else 0.0
    long_pause_count = len(pause_events)

    # 📌 API 명세서의 voice_analysis 구조에 맞게 반환
    return {
        "wpm": wpm,
        "pause_events": pause_events,
        "avg_pause_duration": avg_pause_duration,
        "long_pause_count": long_pause_count,
        "full_text": stt_result_data.get('full_text', '') # 3주차 GPT 분석을 위해 텍스트 포함
    }


# -----------------------------------------------------------------
# 2. Firebase 및 기타 보조 함수 (이전 답변과 동일)
# -----------------------------------------------------------------
def initialize_firebase():
    """Firebase Admin SDK를 초기화합니다."""
    try:
        if not firebase_admin._apps: 
            cred = credentials.Certificate(CREDENTIAL_PATH)
            firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})
        print("✅ Firebase Admin SDK 초기화 완료.")
        return True
    except Exception as e:
        print(f"❌ Firebase 초기화 실패: 오류: {e}")
        return False

def upload_to_firebase_analysis(user_id, file_name, analysis_result):
    """WPM 분석 결과만 Firebase의 analysis_result 경로에 업로드합니다."""
    # 분석 결과가 저장될 경로
    ref_path_analysis = f'users/{user_id}/presentations/{file_name}/voice_analysis' 

    try:
        # 📌 full_text는 제외하고 분석 결과만 저장
        analysis_data_to_save = analysis_result.copy()
        analysis_data_to_save.pop('full_text', None) 
        
        db.reference(ref_path_analysis).set(analysis_data_to_save)
        print(f"    -> [DB] WPM 분석 결과 업로드 완료.")
        
    except Exception as e:
        print(f"    -> [DB] Firebase 업로드 실패. 오류: {e}")

def extract_audio(video_path, output_audio_path):
    # (오디오 추출 로직은 이전 답변과 동일)
    try:
        with VideoFileClip(video_path) as video_clip:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(
                output_audio_path, codec='pcm_s16le', fps=16000, verbose=False, logger=None
            )
        return True
    except Exception as e:
        print(f"  ❌ 오디오 추출 실패: {e}")
        return False

def whisper_transcribe(audio_path):
    # (Whisper STT 전사 로직은 이전 답변과 동일)
    print(f"  -> [STT] Whisper {WHISPER_MODEL_SIZE} 모델 로딩 및 전사 중...")
    try:
        model = whisper.load_model(WHISPER_MODEL_SIZE)
        result = model.transcribe(audio_path, language="ko", word_timestamps=True)
        
        full_text = result.get('text', '').strip()
        word_timestamps = []
        for segment in result.get('segments', []):
            if 'words' in segment:
                word_timestamps.extend(segment['words'])
                
        duration_sec = word_timestamps[-1].get('end', 0.0) if word_timestamps else 0.0
            
        return {
            "full_text": full_text, "words": word_timestamps,
            "duration_sec": duration_sec, "word_count": len(word_timestamps)   
        }

    except Exception as e:
        print(f"  ❌ Whisper 전사 실패: {e}")
        return None


# -----------------------------------------------------------------
# 3. 통합 배치 처리 함수 (메인 로직) - 분석 통합
# -----------------------------------------------------------------
def process_multiple_videos(input_dir, output_dir_audio, output_dir_json, user_id):
    
    is_firebase_ok = initialize_firebase()
    
    os.makedirs(output_dir_audio, exist_ok=True)
    os.makedirs(output_dir_json, exist_ok=True)
    video_files = [f for f in os.listdir(input_dir) if f.endswith('.mp4')]
    
    if not video_files:
        print(f"경고: '{input_dir}'에서 처리할 MP4 영상 파일을 찾을 수 없습니다.")
        return

    print(f"총 {len(video_files)}개의 영상을 처리합니다. 사용자 ID: {user_id}")
    
    for i, video_file in enumerate(video_files):
        print(f"\n--- [{i+1}/{len(video_files)}] {video_file} 처리 시작 ---")
        
        video_path = os.path.join(input_dir, video_file)
        base_name = os.path.splitext(video_file)[0]
        audio_path = os.path.join(output_dir_audio, f"{base_name}.wav")
        json_path = os.path.join(output_dir_json, f"{base_name}_analysis_data.json")

        # 1. 오디오 추출
        if not extract_audio(video_path, audio_path):
             continue

        # 2. Whisper STT 전사
        stt_data = whisper_transcribe(audio_path)
        
        if stt_data:
            # 3. WPM 및 무음 구간 분석 수행 (2주차 통합)
            print("  [Step 3/4] WPM 및 무음 구간 분석 수행 중...")
            voice_analysis_result = analyze_voice_rhythm(stt_data)

            # 4. 로컬 JSON 파일 저장 (WPM 분석 결과 포함)
            # JSON 파일에 STT 데이터와 WPM 분석 결과를 모두 포함
            final_analysis_data = {
                "stt_raw": stt_data,
                "voice_analysis": voice_analysis_result
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(final_analysis_data, f, ensure_ascii=False, indent=4)
            print(f"  ✅ 최종 분석 자료 JSON 저장 완료: {json_path}")
            
            # 5. Firebase DB에 WPM 분석 결과 업로드
            if is_firebase_ok:
                print("  [Step 5/5] Firebase DB에 분석 결과 업로드 중...")
                upload_to_firebase_analysis(user_id, base_name, voice_analysis_result)
            
# --- 최종 실행 ---
process_multiple_videos(INPUT_VIDEO_DIR, OUTPUT_AUDIO_DIR, OUTPUT_JSON_DIR, USER_ID)
