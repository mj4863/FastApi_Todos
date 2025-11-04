FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# 비루트 유저
RUN addgroup --system app && adduser --system --ingroup app app

# 의존성
COPY fastapi-app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 코드 복사(읽기 전용으로 만들 예정)
COPY --chown=app:app fastapi-app/main.py /app/main.py
COPY --chown=app:app fastapi-app/templates /app/templates

# 데이터 디렉토리(쓰기 가능)
RUN mkdir /data && chown app:app /data
ENV TODO_FILE=/data/todo.json

# 코드 리소스는 쓰기권한 제거
RUN chmod 444 /app/main.py && chmod -R 555 /app/templates

USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
