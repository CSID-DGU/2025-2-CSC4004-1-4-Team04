from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.responses import StreamingResponse
import os, asyncio, json, shutil

from video_analyzer import analyze_video, set_progress, get_progress
from stt_processor import extract_audio, whisper_transcribe
from feedback_generator import generate_feedback_from_analysis

#Firebase (RTOB)
import firebase_admin
from firebase_admin import credentials, db

FIREBASE_DATABASE_URL = "https://csc4004-1-4-team04-default-rtdb.firebaseio.com/"
cred = credentials.Certificate("serviceAccountKey.json") 

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})
    
app = FastAPI()


@app.get("/")
def root():
    return {"message": "🎥 Video Analysis API with Progress Stream"}


@app.post("/analyze/video")
async def analyze_video_api(
    user_id: str = Form(...),  # 로그인된 user ID를 받음
    file: UploadFile = File(...)):
    """
    업로드된 영상 파일을 분석하여 시선,자세 분석과 음성 분석을 실행하고, 
    진행률은 /analyze/progress 에서 실시간 스트리밍됩니다.
    결과는 RTDB에 저장합니다.
    """
    base_name = os.path.splitext(file.filename)[0]
    temp_dir = f"temp_{user_id}_{base_name}"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_video_path = os.path.join(temp_dir, file.filename)
    temp_audio_path = os.path.join(temp_dir, f"{base_name}.wav")
    
    contents = await file.read()
    with open(temp_video_path, "wb") as f:
        f.write(contents)

    # 비동기로 분석 실행
    loop = asyncio.get_event_loop()
    
    try:
        # 분석 병렬 실행
        # 시선/자세 분석
        gaze_task = loop.run_in_executor(None, analyze_video, temp_video_path)
        # 음성 STT 분석
        await loop.run_in_executor(None, extract_audio, temp_video_path, temp_audio_path)
        stt_task = loop.run_in_executor(None, whisper_transcribe, temp_audio_path)
            
        gaze_results = await gaze_task
        stt_results = await stt_task

        # RTDB에 통합 저장
        file_db_path = f'users/{user_id}/presentations/{base_name}'
        
        # STT 결과 저장
        db.reference(f'{file_db_path}/stt_analysis').set(stt_results)
        
        # 시선/자세 결과 저장
        db.reference(f'{file_db_path}/vision_analysis').set(gaze_results)
        
        return {
            "message": "시선/자세 및 STT 분석 완료. RTDB 저장 성공.",
            "user_id": user_id,
            "presentation_id": base_name # 이 ID로 /feedback/full 호출
        }

    except Exception as e:
        return {"message": f"분석/저장 실패: {str(e)}"}
    
    finally:
        # 임시 폴더 및 파일 삭제
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir) # 폴더 통째로 삭제
        

@app.get("/analyze/progress")
async def get_progress_stream():
    """
    실시간 진행률을 SSE(Server-Sent Events)로 스트리밍합니다.
    """
    async def event_generator():
        while True:
            progress = get_progress()
            data = json.dumps({"progress": progress})
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)
            if progress >= 100:
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# RTOB 기반 feedback/full API 수정
@app.post("/feedback/full")
def feedback_full_api(data: dict = Body(...)):
    """
    user_id와 presentation_id를 받아 RTDB에서 모든 분석 데이터를 조회,
    LLM 레포트를 생성한 뒤, 다시 RTDB에 업데이트합니다.
    """
    try:
        user_id = data.get("user_id")
        presentation_id = data.get("presentation_id")
        
        if not (user_id and presentation_id):
            return {"message": "❌ 'user_id'와 'presentation_id'가 필요합니다."}

        db_path = f'users/{user_id}/presentations/{presentation_id}'
        
        # --- 1. RTDB에서 모든 분석 결과 조회 ---
        gaze_data = db.reference(f'{db_path}/vision_analysis').get()
        stt_data = db.reference(f'{db_path}/stt_analysis').get()
        
        if not gaze_data:
            return {"message": "❌ 시선/자세 분석 데이터를 찾을 수 없습니다."}

        # 추후 stt_data도 함께 받아서
        # 통합 레포트를 생성하도록 수정 필요

        # LLM 레포트 생성 (API 키 필요)
        analysis_data_for_llm = {"result": gaze_data}
        feedback_report = generate_feedback_from_analysis(analysis_data_for_llm)

        # RTDB에 레포트 저장 
        db.reference(f'{db_path}/final_report').set(feedback_report)

        return {
            "message": "✅ Feedback report successfully generated and saved to RTDB.",
            "document_id": f"{user_id}/{presentation_id}",
            "feedback_preview": feedback_report[:300] + "..."
        }
    except Exception as e:
        return {"message": f"레포트 생성/저장 실패: {str(e)}"}