from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
from datetime import date as _date
import json
import os
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator

APP_VERSION = "6.0.0"
NOT_FOUND_MSG = "To-Do item not found"
TODAY = _date.today().isoformat()

app = FastAPI(title="Todo App", version=APP_VERSION)

# Prometheus 메트릭스 엔드포인트 (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Paths (절대경로 안전화) ---
BASE_DIR = Path(__file__).resolve().parent
TODO_FILE = Path(os.getenv("TODO_FILE", str(BASE_DIR / "todo.json")))
INDEX_HTML = BASE_DIR / "templates" / "index.html"

# --- Model & Validation ---
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False
    date: str = Field(default_factory=lambda: _date.today().isoformat())

    @field_validator("title", "description")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v.strip()
    
    @field_validator("date")
    @classmethod
    def valid_date(cls, v: str) -> str:
        # YYYY-MM-DD 형식 검증
        try:
            y, m, d = map(int, v.split("-"))
            _ = _date(y, m, d)
        except Exception:
            raise ValueError("date must be YYYY-MM-DD")
        return v
    
class DateOnly(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")

    @field_validator("date")
    @classmethod
    def valid_date(cls, v: str) -> str:
        try:
            y, m, d = map(int, v.split("-"))
            _ = _date(y, m, d)
        except Exception:
            raise ValueError("date must be YYYY-MM-DD")
        return v

# --- Storage helpers ---
def load_todos() -> list[dict]:
    if TODO_FILE.exists():
        try:
            with TODO_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 손상된 파일 방어
            return []
    return []

def save_todos(todos: list[dict]) -> None:
    with TODO_FILE.open("w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=4)

# --- Health/Version ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": APP_VERSION}

# --- CRUD + 필터 ---
@app.get("/todos", response_model=List[TodoItem])
def get_todos(
    completed: Optional[bool] = Query(default=None, description="완료 여부 필터"),
    date: Optional[str] = Query(default=None, description="YYYY-MM-DD 특정 날짜 필터")
):
    todos = load_todos()
    
    # 날짜 없는 기존 항목은 TODAY로 간주해서 동작 일관성 확보
    for t in todos:
        if "date" not in t:
            t["date"] = TODAY

    if completed is not None:
        todos = [t for t in todos if bool(t.get("completed", False)) == completed]
    if date is not None:
        todos = [t for t in todos if t.get("date") == date]
    return todos

@app.post("/todos", response_model=TodoItem, status_code=200)
def create_todo(todo: TodoItem):
    todos = load_todos()
    # 중복 id 방지
    if any(t["id"] == todo.id for t in todos):
        raise HTTPException(status_code=409, detail="Duplicate id")
    todos.append(todo.model_dump())
    save_todos(todos)
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            merged = updated_todo.model_dump()
            merged["id"] = todo_id  # URL 우선
            # date 필드 누락 방지(구버전 클라이언트 호환)
            if not merged.get("date"):
                merged["date"] = t.get("date", TODAY)
            todos[i] = merged
            save_todos(todos)
            return merged
    raise HTTPException(status_code=404, detail=NOT_FOUND_MSG)

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    new_todos = [t for t in todos if t["id"] != todo_id]
    if len(new_todos) == len(todos):
        raise HTTPException(status_code=404, detail=NOT_FOUND_MSG)
    save_todos(new_todos)
    return {"message": "To-Do item deleted"}

# 단건 조회: 구데이터도 date 보장
@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int):
    for t in load_todos():
        if t["id"] == todo_id:
            if "date" not in t:
                t["date"] = TODAY
            return t
    raise HTTPException(status_code=404, detail=NOT_FOUND_MSG)

# --- HTML ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    if not INDEX_HTML.exists():
        return HTMLResponse("<h1>index.html not found</h1>", status_code=500)
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))

@app.middleware("http")
async def add_version_header(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-App-Version"] = APP_VERSION
    return resp

# --- Date ---
@app.patch("/todos/{todo_id}/date", response_model=TodoItem)
def update_todo_date(todo_id: int, payload: DateOnly):
    todos = load_todos()
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            # 구데이터 호환: 기본 필드 보존
            if "date" not in t:
                t["date"] = TODAY
            t["date"] = payload.date
            save_todos(todos)
            # 응답도 TodoItem 스키마에 맞춰 반환
            return t
    raise HTTPException(status_code=404, detail=NOT_FOUND_MSG)