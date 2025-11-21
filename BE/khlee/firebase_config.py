import firebase_admin
from firebase_admin import credentials, firestore

# 1️⃣ 서비스 계정 키 로드
cred = credentials.Certificate("serviceAccountKey.json")

# 2️⃣ Firebase 앱 초기화
firebase_admin.initialize_app(cred)

# 3️⃣ Firestore 클라이언트 생성
db = firestore.client()
