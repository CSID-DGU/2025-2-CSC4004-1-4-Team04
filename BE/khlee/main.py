from fastapi import FastAPI, UploadFile, File, Body
import os
from video_analyzer import analyze_video
# from feedback_generator import generate_feedback_from_analysis

# FireBase 모듈 가져오기
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json") 
firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

@app.get("/")
def root():
    return {"message": "🎥 Video Analysis API by khlee"}

@app.post("/analyze/video")
async def analyze_video_api(file: UploadFile = File(...)):
    """
    업로드된 영상 파일을 임시 저장 후 분석하고 DB에 저장한 뒤 결과를 반환합니다.
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
    
    try:
        # 'analysis_results' 폴더에 새 문서 작성
        doc_ref = db.collection(u'analysis_results').document() 
        doc_ref.set({
            u'filename': file.filename,
            u'analysis_data': result, # video_analyzer가 만든 결과
            u'created_at': firestore.SERVER_TIMESTAMP
        })
        # DB에 저장된 고유 ID를 결과에 포함시켜 반환
        result['document_id'] = doc_ref.id
    except Exception as e:
        result['db_error'] = f"DB 저장 실패: {str(e)}"

    return {"filename": file.filename, "result": result}


# @app.post("/feedback/full")
# def feedback_full_api(analysis_data: dict = Body(...)):
#     """
#     video_analyzer 결과(JSON 전체)를 입력받아 GPT 피드백 생성 및 FireBase DB에 업데이트
#     """
#     feedback = generate_feedback_from_analysis(analysis_data)

#     # analyze/video에서 보낸 'result' 객체 안의 'document_id'를 찾음
#     doc_id = analysis_data.get('result', {}).get('document_id')

#     try:
#         if doc_id:
#             # ID가 있다면, 해당 문서를 찾아서 피드백 내용을 업데이트
#             doc_ref = db.collection(u'analysis_results').document(doc_id)
#             doc_ref.update({
#                 u'feedback_markdown': feedback, 
#                 u'feedback_generated_at': firestore.SERVER_TIMESTAMP
#             })
#             return {
#                 "message": "✅ Feedback generated and saved to DB.",
#                 "document_id": doc_id
#             }
#         else:
#             # ID가 없는 예외 상황 처리
#             return {
#                 "message": "⚠️ Feedback generated, but document_id was missing. Not saved to DB."
#             }
            
#     except Exception as e:
#         return {"message": f"DB 저장 실패: {str(e)}"}
