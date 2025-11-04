import os
from openai import OpenAI
from dotenv import load_dotenv

# .env 로드
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("❌ OPENROUTER_API_KEY가 설정되어 있지 않습니다. .env를 확인하세요.")

# OpenRouter 클라이언트
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def generate_feedback_from_analysis(analysis_data: dict) -> str:
    """
    video_analyzer 결과(JSON 전체)를 기반으로
    시선·자세·프레임 정보를 분석 리포트 형식으로 생성
    """
    try:
        meta = analysis_data["result"]["metadata"]
        gaze = analysis_data["result"]["gaze"]
        posture = analysis_data["result"]["posture"]

        prompt = f"""
        당신은 발표 분석 전문가입니다.
        아래는 발표 영상 분석 데이터입니다.

        --- 데이터 ---
        • FPS: {meta['fps']}
        • Duration: {meta['duration_sec']:.2f}초
        • Resolution: {meta['resolution']}
        • Frame count: {meta['frame_count']}

        • Gaze Center Ratio: {gaze['center_ratio']}
        • Gaze Distribution: {gaze.get('distribution', {})}
        • Movement Rate per sec: {gaze.get('movement_rate_per_sec', 'N/A')}

        • Posture Stability: {posture['stability']}
        • Shoulder σx, σy: {posture['sigma']['x']}, {posture['sigma']['y']}
        • Roll Mean: {posture['roll_mean']}

        --- 작성 규칙 ---
        1. 아래 형식의 “리포트 문서”를 작성하세요.
        2. 표는 Markdown 표 형식을 사용하세요.
        3. 수치 해석, 기준값, 요약 코멘트 모두 포함하세요.
        4. 한국어로, 전문가 보고서 어조로 작성하세요.

        --- 리포트 템플릿 ---
        🎬 영상 기본 정보  
        (FPS, 길이, 해상도 등 표로 정리)

        👁️ 시선(Gaze) 분석  
        (center_ratio, distribution, movement_rate 해석 포함)

        🧍 자세(Posture) 분석  
        (stability, σx, σy, roll_mean 설명 포함)

        📈 요약 평가표  
        (항목별 수치·레벨·간단 해석)

        💬 요약 코멘트  
        (3~4문장 요약: 발표자의 강점과 개선점)

        --- 출력 예시 ---
        🎬 영상 기본 정보
        | 항목 | 값 | 설명 |
        |------|----|------|
        | FPS | 29.97 | 정상 인식 |
        ...
        """

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Presentation Coach",
            },
            messages=[
                {"role": "system", "content": "당신은 발표 영상 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ 리포트 생성 중 오류 발생: {e}"
