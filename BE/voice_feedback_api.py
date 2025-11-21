import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, Body, HTTPException
from openai import OpenAI
from stt_processor import analyze_voice_rhythm_and_patterns

router = APIRouter(prefix="/feedback", tags=["feedback (voice)"])

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_SITE = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_TITLE = os.getenv("OPENROUTER_TITLE", "voice-feedback")


def _get_openrouter_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=503, detail="OPENROUTER_API_KEY 미설정")
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)


def _build_prompt(stt_result: Dict[str, Any], video_meta: Optional[Dict[str, Any]] = None) -> str:
    """사용자 제공 예시 템플릿을 따라 음성 피드백을 생성하도록 지시하는 프롬프트."""
    video_meta = video_meta or {}
    template_hint = (
        "🎬 **영상 기본 정보**\n"
        "| 항목 | 값 | 설명 |\n|------|----|------|\n"
        "...\n\n"
        "👁️ **시선 분석**\n| 척도 | 값 | 기준 | 평가 | 개선점 |\n|------|----|------|------|--------|\n...\n\n"
        "📊 **종합 평가표**\n| 항목 | 점수(10점 만점) | 비고 |\n|------|----------------|------|\n...\n"
        "💬 **총평**\n...\n"
        "**개선 제안**\n1. ...\n2. ...\n3. ..."
    )

    return (
        "You are a public speaking coach. Generate a Korean Markdown report in the same structure and tone "
        "as the provided template hint. Use the STT analysis JSON strictly as evidence. "
        "Focus on 음성 전달/리듬/속도/추임새/말끝 흐림/정지 구간(WPM, pause_events, hesitation/filler 등). "
        "If video_meta is given, briefly reflect it in the first table. "
        "Keep tables concise and numbers with reasonable precision. "
        "Return pure Markdown only, no code fences.\n\n"
        f"Template hint:\n{template_hint}\n\n"
        f"video_meta (optional): {json.dumps(video_meta, ensure_ascii=False)}\n"
        f"stt_result JSON:\n{json.dumps(stt_result, ensure_ascii=False)}\n"
    )


@router.post("/voice")
def generate_voice_feedback(payload: Dict[str, Any] = Body(...)):
    """
    STT 분석 JSON(stt_result)과 선택적 video_meta를 받아
    OpenRouter LLM으로 Markdown 피드백을 생성합니다.
    """
    stt_result = payload.get("stt_result")
    video_meta = payload.get("video_meta") or {}
    output_name = payload.get("output_name")
    voice_analysis = payload.get("voice_analysis")

    if not stt_result:
        raise HTTPException(status_code=400, detail="'stt_result' 필드가 필요합니다.")

    # stt_result만 왔을 때 WPM/언어습관 분석을 생성해 보완
    if not voice_analysis:
        try:
            voice_analysis = analyze_voice_rhythm_and_patterns(stt_result)
            stt_result = dict(stt_result)
            stt_result["voice_analysis"] = voice_analysis
        except Exception as e:  # pragma: no cover - 방어적 처리
            print(f"⚠️ voice_analysis 생성 실패: {e}")

    client = _get_openrouter_client()
    prompt = _build_prompt(stt_result, video_meta)

    completion = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {"role": "system", "content": "당신은 발표 음성 피드백을 작성하는 전문가입니다."},
            {"role": "user", "content": prompt},
        ],
        extra_headers={
            "HTTP-Referer": OPENROUTER_SITE,
            "X-Title": OPENROUTER_TITLE,
        },
    )

    feedback_md = completion.choices[0].message.content

    output_dir = Path("feedback_reports")
    output_dir.mkdir(exist_ok=True)
    safe_name = output_name or f"voice_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_path = output_dir / safe_name
    output_path.write_text(feedback_md, encoding="utf-8")

    return {
        "message": "✅ 음성 피드백 생성 완료",
        "file_path": str(output_path),
        "feedback_preview": feedback_md[:400] + ("..." if len(feedback_md) > 400 else "")
    }
