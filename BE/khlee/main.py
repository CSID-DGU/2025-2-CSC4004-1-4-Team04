from fastapi import FastAPI, UploadFile, File, Body
import os
from video_analyzer import analyze_video
from feedback_generator import generate_feedback_from_analysis

app = FastAPI()

@app.get("/")
def root():
    return {"message": "🎥 Video Analysis API by khlee"}

@app.post("/analyze/video")
async def analyze_video_api(file: UploadFile = File(...)):
    """
    업로드된 영상 파일을 임시 저장 후 분석하고 결과를 반환합니다.
    """
    temp_path = f"temp_{file.filename}"
    contents = await file.read()

    # 파일 임시 저장
    with open(temp_path, "wb") as f:
        f.write(contents)

    # 영상 분석 실행
    result = analyze_video(temp_path)

    # 임시 파일 삭제
    os.remove(temp_path)

    return {"filename": file.filename, "result": result}


@app.post("/feedback/full")
def feedback_full_api(analysis_data: dict = Body(...)):
    """
    video_analyzer 결과(JSON 전체)를 입력받아 GPT 피드백 생성 및 Markdown 저장
    """
    feedback = generate_feedback_from_analysis(analysis_data)

    # ✅ Markdown 파일로 저장
    output_dir = "feedback_reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "feedback.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(feedback)

    return {
        "message": "✅ Feedback report successfully generated.",
        "file_path": output_path,
        "feedback_preview": feedback[:300] + "..."  # 미리보기
    }
