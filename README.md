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
| Category | Stack |
| :--- | :--- |
| **Frontend** | React, TypeScript, Tailwind CSS, Vite |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **AI / ML** | OpenAI Whisper, MediaPipe, OpenCV, GPT-4 |
| **Infra & DB** | Docker, Render, Firebase Firestore |
| **Tools** | FFmpeg, GitHub, Git |

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
- 프론트: http://localhost:5173(프론트로 접속해서 테스트 가능)

## 페이지별 설명
###[메인 홈]
![image](https://github.com/user-attachments/assets/8ae6dfae-558a-4926-9cce-5351adb69792)

<br>

###[발표 스크립트 선택]
<img width="1105" height="588" alt="image" src="https://github.com/user-attachments/assets/f6a7f141-27e3-421b-b414-b55ce99dbed1" />

<br>

###[발표 영상 녹화 영상 업로드]
<img width="1214" height="613" alt="image" src="https://github.com/user-attachments/assets/8cbc523c-1641-460d-95eb-7edac2288cac" />

<br>

###[분석 결과]
- 본 시스템은 음성, 영상, 내용/논리 분석 결과를 종합하여 발표에 대한 종합 점수(100점 만점)를 산출한다.
<img width="798" height="339" alt="image" src="https://github.com/user-attachments/assets/244fe82d-1486-4d96-bd12-6cc75a54043c" />

<br>
- 1) 불필요한 음성
의미: 발표 중 반복적으로 등장하는 추임새 예 음 어 그니까 등 의 ( : “ ”, “ ”, “ ” ) 사용 횟수
산출 방법: STT (stt_analysis.full_text) 결과 텍스트 에서 사전에 정의된 추임새 패턴 목록과 일치하는 단어를 탐지하여 단순 횟수로 집계
표시 방식: 총 발생 횟수 (회)

- 2) 말하기 속도 (WPM)
의미: (Words Per Minute) 분당 발화 단어 수
산출 방법: WPM = ( / 총 단어 수 전체 발화 시간 ( )) * 60 초(stt_analysis.word_count, stt_analysis.duration_sec ) 활용
평가 기준: 140~160 WPM: , 권장 범위 과도하게 느리거나 빠른 경우 전달력 저하로 판단

-3) 말 사이 공백 (침묵)
의미: 발화 중 일정 시간 이상 이어지는 무음 구간
산출 방법:연속된 단어 간 시간 차 가 (end start) ( 2 ) → 임계값 기본 초 이상인 경우를 긴 침묵 이벤트로 기록
표시 방식: 긴 침묵 발생 횟수 (회)

4) 말끝 흐림
의미: 문장을 명확하게 끝내지 못하고 흐리는 발화 습관
산출 방법: GPT 기반 언어 패턴 분석 또는 정규식 기반 백업 로직을 통해 말끝 흐림 표현 탐지
표시 방식: 총 발생 횟수 (회)

<img width="852" height="422" alt="image" src="https://github.com/user-attachments/assets/3128906c-fca2-400f-a78c-9a181cd95712" />

