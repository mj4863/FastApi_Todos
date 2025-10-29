# Python 3.9 슬림 이미지
FROM python:3.9-slim

# 앱용 비루트 사용자 생성
RUN useradd -m appuser

# 작업 디렉토리 설정
WORKDIR /app

# 1️⃣ 의존성 설치 및 권한 설정을 한 줄로 묶기
COPY --chown=appuser:appuser requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt && chmod 444 requirements.txt

# 2️⃣ 앱 복사 (.dockerignore로 안전하게)
COPY --chown=appuser:appuser . .

# 3️⃣ 비루트 사용자로 전환
USER appuser

# FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
