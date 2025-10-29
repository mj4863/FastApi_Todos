# Python 3.9 슬림 버전 사용 (용량↓, 보안↑)
FROM python:3.9-slim

# 환경 변수 설정 (로그 버퍼링 방지 + pyc 캐시 비활성화)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 비루트 사용자 생성
RUN adduser --disabled-password --gecos "" appuser \
 && mkdir -p /app \
 && chown -R appuser:appuser /app

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 먼저 복사 후 설치 (캐시 효율)
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 파일 복사 (dockerignore로 민감/불필요 파일 제외)
COPY --chown=appuser:appuser . .

# 비루트 사용자로 실행
USER appuser

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
