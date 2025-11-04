FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# non-root
RUN addgroup --system app && adduser --system --ingroup app app

# 의존성
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 코드 복사 (컨텍스트가 fastapi-app 이므로 접두어 제거)
COPY --chown=app:app main.py /app/main.py
COPY --chown=app:app templates /app/templates

# 데이터 디렉토리(쓰기 가능) + 앱은 읽기 전용
RUN mkdir /data && chown app:app /data
ENV TODO_FILE=/data/todo.json
RUN chmod 444 /app/main.py && chmod -R 555 /app/templates

USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
