# ✨ Todo App – FastAPI + Frontend SPA  
**버전: 8.0.0**  
- 빠른 일정 관리, 직관적인 UI, 강력한 캘린더 기능을 갖춘 Todo 앱입니다.  
- FastAPI 백엔드 + HTML/CSS/JS 프론트엔드 구조로 구현되었으며, Prometheus 모니터링 및 Jenkins 파이프라인을 완벽 지원합니다.

---

## 🚀 주요 기능

### ✅ 1. CRUD + 날짜 기반 Todo 관리
- Title / Description / Completed 관리  
- 날짜(date) 기반 필터링  
- 날짜 클릭 시 해당 날짜 Todo 자동 로드  
- JSON 파일(todo.json) 기반 스토리지  

---

### ✏️ 2. Inline Edit 기능
- 팝업 없이 리스트 요소 자체에서 바로 수정  
- Title / Description / Date 변경 가능  
- Enter = 저장, ESC = 취소  
- 수정 중 체크박스 비활성화  

---

### 🗓️ 3. 달력(Calendar) 시스템
- **일요일(Sun) 시작**  
- **연·월 빠른 이동 기능**  
- 팝오버로 연도/월 선택  
- Today 버튼으로 즉시 오늘 날짜로 이동  
- 오늘 날짜 강조(`outline`, `bold`)  

---

### 📦 4. Move To 기능
- 각 Todo에 Move 버튼 추가  
- 날짜 입력 후 해당 날짜로 이동  
- 서버 `PATCH /todos/{id}/date` 엔드포인트와 연동  

---

### ⏳ 5. D-Day 기능 (v8.0.0)
- 각 Todo의 *마감일까지 남은 일수* 배지 표시  
- 기한 상태별 색상:
  - 🔴 지남  
  - 🟠 오늘  
  - 🟡 임박 (1~3일)  
  - 🔵 여유 (4일 이상)  
- 다크 모드 자동 대비 적용  

---

### 📊 6. 프로그레스 바
- 완료율을 시각적으로 표시  
- `"5/10 (50%)"` 형태  
- 툴바 상단에 표시  

---

### 🎨 7. UI/UX 강화 (v7.0.0)
- Inter 폰트 적용  
- 그라디언트 배경 (라이트/다크 개별 적용)  
- 슬라이드/페이드/쉐이크 등 애니메이션 추가  
- 카드 디자인 강화  
- 에러 메시지 쉐이크 애니메이션  

---

### 🌙 8. 라이트/다크 모드 토글
- CSS Design Token 기반  
- 다크 모드에서도 D-Day 배지 & 달력 버튼 자동 색상 조정  

---

### 📈 9. Prometheus 모니터링
- `/metrics` 자동 노출  
- FastAPI 요청/응답 메트릭  
- Grafana 대시보드 구성 용이  

---

## 📂 프로젝트 구조
```
FastApi_Todos/
├── fastapi-app/
│   ├── templates/
│   │   └── index.html
│   ├── tests/
│   │   └── test_main.py
│   ├── venv/                     # (Git 관리 제외: .gitignore 처리됨)
│   ├── .dockerignore
│   ├── Dockerfile                # FastAPI 앱용 Dockerfile
│   ├── main.py                   # FastAPI 메인 엔트리포인트
│   ├── requirements.txt          # FastAPI 패키지 리스트
│   ├── sonar-project.properties  # SonarQube 설정
│   └── todo.json                 # 로컬 Todo 데이터 저장소
│
├── jmeter/
│   ├── Dockerfile                # JMeter 테스트 이미지
│   └── fastapi_test_plan.jmx     # JMeter 부하 테스트 플랜
│
├── prometheus/
│   ├── prometheus.yml            # Prometheus 설정
│
├── .gitignore                    # venv, 로그, __pycache__ 등 제외
├── docker-compose.yml            # FastAPI + Prometheus + Grafana + JMeter 통합 실행
└── promtail-config.yaml          # Loki + Promtail 로그 수집 설정
```

---

## ▶️ 로컬 실행

### 1) 가상환경 생성 & 실행
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 2) 패키지 설치
```bash
pip install -r requirements.txt
```

### 3) 서버 실행
```bash
uvicorn main:app --reload
```

### 4) 웹 접속
```bash
http://127.0.0.1:8000/
```

---

## 🐳 Docker 실행
### 빌드
```bash
docker build -t todo-app .
```

### 실행
```bash
docker run -p 8000:8000 todo-app
```

### 또는 docker-compose
```bash
docker-compose up --build
```

---

## 📌 API 요약
|Method|	Endpoint|	기능
|:---|:---|:---|
|GET|	/todos	|Todo 목록 조회
|POST|	/todos	|Todo 생성
|PUT|	/todos/{id}	|Todo 전체 수정
|PATCH|	/todos/{id}/date	|날짜만 변경
|DELETE|	/todos/{id}	|Todo 삭제
|GET|	/version	|버전 반환
|GET|	/metrics	|Prometheus 메트릭

---

## 📝 Release Notes
### ✔ Version 7.0.0
- 디자인 시스템 대규모 개편
- Due Date 입력 추가
- Inter 폰트 & 그라디언트 배경
- 애니메이션 다수 추가

### ✔ Version 8.0.0
- D-Day 기능
- 프로그레스 바
- Todo 마감일 강조 스타일
- 다크 모드 자동 조정

---

## 🙋‍♂️ Author
### 민준 (mj4863)
FastAPI · Docker · Jenkins · Full-Stack Developer
문의 · 제안 환영합니다!
