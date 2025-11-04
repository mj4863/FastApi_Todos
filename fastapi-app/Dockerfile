FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 비루트 사용자 추가
RUN addgroup --system app && adduser --system --ingroup app app

# 의존성 먼저 캐시
COPY fastapi-app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 필요한 파일만 복사 (권장: 서비스 디렉토리만)
COPY --chown=app:app fastapi-app/main.py /app/main.py
COPY --chown=app:app fastapi-app/templates /app/templates
# 초기 todo.json이 꼭 필요하다면:
# COPY --chown=app:app fastapi-app/todo.json /app/todo.json

USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]