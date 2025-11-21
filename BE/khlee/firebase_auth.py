import firebase_admin
from firebase_admin import auth, credentials

# 기존 firebase_config.py에서 이미 초기화했으면 생략 가능
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

def verify_token(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        return uid
    except Exception as e:
        print("❌ 인증 실패:", e)
        return None
