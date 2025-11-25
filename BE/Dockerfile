# Python 3.10 슬림 버전 사용 (bookworm로 내려 패키지 호환 확보)
FROM python:3.10-slim-bookworm

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (OpenCV, MediaPipe 실행에 필요)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출 (Railway/Render는 환경변수 PORT를 사용하지만, 명시적으로 8000을 문서화)
EXPOSE 8000

# 서버 실행
# 호스트 0.0.0.0으로 설정하여 외부 접속 허용
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
