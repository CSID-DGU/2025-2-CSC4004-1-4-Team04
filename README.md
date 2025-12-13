# 2025-2-CSC4004-1-4-Team04

## 🎤 SpeakFlow – AI 발표 코치

![image](https://github.com/user-attachments/assets/8ae6dfae-558a-4926-9cce-5351adb69792)

- 프론트 배포 주소: https://speakflows.vercel.app/
- 백엔드 배포 주소: https://two025-2-csc4004-1-4-team04.onrender.com/
- (docs뒤에 붙여 fastapi 확인가능) 백엔드 서버 메모리 부족 
<img width="1118" height="115" alt="image" src="https://github.com/user-attachments/assets/6f542b2c-f6ca-4555-b0a5-6e5fcbbda26a" />
영상 분석을 진행하기 위한 최소 메모리 4~8GB 비용 85$~175$ 예상 , 예산 부족으로 실제 작업 처리는 로컬에서 현재 가능, 분석 결과 확인은 가능 

<br>
<br>

## 프로젝트 소개

- SpeakFlow는 발표자의 시선, 자세, 음성, 노리 구조를 다각도로 분석하여 사용자의 개선 방향을 명확하게 제시하는 웹 기반 자동화 코칭 플랫폼입니다
- 기존의 발표 연습 서비스가 단순 녹음이나 텍스트 분석에 그치는 한계를 극복하기 위해, 본 프로젝트는 AI 기술을 활용하여 발표자의 비언어적 행동과 언어적 전달력을 통합적으로 진단합니다.
- 최종적으로 사용자에게 정량화된 데이터와 LLM 기반의 개선 피드백을 제공합니다.

<br>
<br>

## 👨‍💻 팀원 소개

<table>
  <tr>
    <td align="center" width="150px">
      <img src="https://github.com/kelly0819.png" width="100px;" style="border-radius:50%;"/><br/>
      <sub><b>한지예</b></sub><br/>
      <a href="https://github.com/kelly0819">@kelly0819</a>
    </td>
    <td align="center" width="150px">
      <img src="https://github.com/kannikii.png" width="100px;" style="border-radius:50%;"/><br/>
      <sub><b>이권형</b></sub><br/>
      <a href="https://github.com/kannikii">@kannikii</a>
    </td>
    <td align="center" width="150px">
      <img src="https://github.com/pjh21028.png" width="100px;" style="border-radius:50%;"/><br/>
      <sub><b>박중헌</b></sub><br/>
      <a href="https://github.com/pjh21028">@pjh21028</a>
    </td>
    <td align="center" width="150px">
      <img src="https://github.com/rlfqls.png" width="100px;" style="border-radius:50%;"/><br/>
      <sub><b>장길빈</b></sub><br/>
      <a href="https://github.com/rlfqls">@rlfqls</a>
    </td>
    <td align="center" width="150px">
      <img src="https://avatars.githubusercontent.com/u/0?v=4" width="100px;" style="border-radius:50%; opacity:0.4;"/><br/>
      <sub><b>스팡위</b></sub><br/>
      <span style="color: gray;">No GitHub</span>
    </td>
  </tr>
</table>
<hr/>
<br>
<br> 
<br>

## 🛠 Tech Stack
### Frontend
<p>
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=React&logoColor=blackreact"/>
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=Vite&logoColor=white"/>
  <img src="https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=TailwindCSS&logoColor=white"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=TypeScript&logoColor=white"/>
</p>


### Backend 
<p>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=Firebase&logoColor=black"/>
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=Vercel&logoColor=white"/>
</p>


### AI / ML 
<p>
  <img src="https://img.shields.io/badge/MediaPipe-FF5722?style=for-the-badge&logo=mediapipe&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenCV-EE4C2C?style=for-the-badge&logo=opencv&logoColor=white"/>
  <img src="https://img.shields.io/badge/GPT-4-FFCA28?style=for-the-badge&"/>
  <img src="https://img.shields.io/badge/OpenAI Whisper-0055FF?style=for-the-badge&logoColor=white"/>
</p>

### Infra & DB
<p>
  <img src="https://img.shields.io/badge/firebase-#2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Render-##000000?style=for-the-badge&logo=render&logoColor=white"/>
  <img src="https://img.shields.io/badge/Firebase-##DD2C00?style=for-the-badge&logo=firebase&logoColor=white"/>
</p>

<br>

## 프로젝트 구조

```
├── BE
│   ├── .python-version
│   ├── .python-version 2
│   ├── combined_feedback_generator.py
│   ├── main.py
│   ├── requirements.txt
│   ├── result_summary_api.py
│   ├── stt_processor.py
│   └── video_analyzer.py
├── FE
│   ├── node_modules
│   ├── src
│   │   ├── apis
│   │   ├── components
│   │   ├── lib
│   │   ├── mocks
│   │   ├── styles
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── env.d.ts
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── vite-env.d.ts
│   └── vite.config.ts
├── .gitignore
├── deployment.md
└── README.md
```
<br>

## ✨ Key Features
본 서비스는 3가지 핵심 분석 모듈을 통해 발표를 진단합니다.

### 1. 👁️ 영상 분석 (Vision AI)
* MediaPipe를 활용하여 발표자의 시선 처리, 자세 안정성, 제스처 사용 빈도를 프레임 단위로 분석합니다.
* 시선이 분산되거나 불안정한 자세를 취하는 구간을 히트맵과 좌표 변화로 감지합니다.

### 2. 🎙️ 음성 분석 (Audio AI)
* OpenAI Whisper 모델을 사용하여 발표 내용을 텍스트로 변환(STT)합니다.
* 발화 속도(WPM), 무음 구간(Pause), 불필요한 추임새(Filler words)를 탐지하여 전달력을 평가합니다.

### 3. 🧠 내용 및 논리 분석 (Logic AI)
* GPT API를 활용하여 발표 대본과 실제 발화 내용의 일치도를 분석합니다.
* 발표의 논리적 구조(서론-본론-결론)를 파악하고 설득력을 강화할 수 있는 피드백을 생성합니다.

<br> 

## 구현
본 시스템은 대용량 영상 데이터를 효율적으로 처리하기 위해 비동기 파이프라인
(Asynchronous Pipeline) 구조를 채택하였다. 전체 분석 과정은 크게 영상 처리, 음성 처리, 그리고 피드백 생성의 3단계로 병렬 수행되며, 그 상세 흐름은 다음 그림과 같다.
<img width="914" height="980" alt="image" src="https://github.com/user-attachments/assets/ceb34c95-f1cb-4b5f-a41b-428aa2196501" />

## 🚀 실행 방법 (로컬)
1) 코드 받기  
```bash
git clone <repo-url>
cd 2025-2-CSC4004-1-4-Team04
```

2) 백엔드 준비  
```bash
cd BE
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# 환경변수: FIREBASE_CRED_PATH, FIREBASE_PROJECT_ID, OPENAI_API_KEY 등 .env에 설정
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3) 프론트 준비  
```bash
cd FE
npm install
# vite용 .env에 VITE_API_URL=http://localhost:8000 등 설정
npm run dev -- --host 0.0.0.0 --port 5173
```

4) 브라우저 접속  
- 백엔드 Swagger: http://localhost:8000/docs  
- 프론트: http://localhost:5173

프론트로 접속해서 테스트 가능
