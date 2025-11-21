from firebase_config import db
import datetime

def test_save():
    # 예시 데이터 (간단한 문서)
    data = {
        "test_field": "Hello Firestore!",
        "timestamp": datetime.datetime.now().isoformat()
    }
    db.collection("TestCollection").add(data)
    print("✅ 데이터 저장 완료!")

if __name__ == "__main__":
    test_save()
