# Python 3.9 슬림 이미지
FROM python:3.9-slim

# 비루트 사용자 생성
RUN useradd -m appuser

WORKDIR /app

# 1️⃣ requirements.txt 복사 후 읽기 전용 설정
COPY --chown=appuser:appuser requirements.txt .
RUN chmod 444 requirements.txt && pip install --no-cache-dir -r requirements.txt

# 2️⃣ 앱 복사 (.dockerignore로 민감 데이터 제외)
COPY --chown=appuser:appuser . .

# 3️⃣ 비루트 사용자로 전환
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
