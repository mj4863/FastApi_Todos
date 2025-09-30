from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from pydantic import BaseModel, field_validator
from typing import List, Optional
import json
import os
from pathlib import Path

APP_VERSION = "3.0.0"

app = FastAPI(title="Todo App", version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Paths (절대경로 안전화) ---
BASE_DIR = Path(__file__).resolve().parent
TODO_FILE = BASE_DIR / "todo.json"
INDEX_HTML = BASE_DIR / "templates" / "index.html"

# --- Model & Validation ---
class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False

    @field_validator("title", "description")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v.strip()

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
def get_todos(completed: Optional[bool] = Query(default=None, description="완료 여부 필터")):
    todos = load_todos()
    if completed is None:
        return todos
    return [t for t in todos if bool(t.get("completed", False)) == completed]

@app.post("/todos", response_model=TodoItem, status_code=201)
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
            # id 불변 원칙: URL의 todo_id로 고정
            merged = updated_todo.model_dump()
            merged["id"] = todo_id
            todos[i] = merged
            save_todos(todos)
            return merged
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todos = load_todos()
    new_todos = [t for t in todos if t["id"] != todo_id]
    if len(new_todos) == len(todos):
        # 없던 항목 삭제 요청
        raise HTTPException(status_code=404, detail="To-Do item not found")
    save_todos(new_todos)
    return {"message": "To-Do item deleted"}

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

@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int):
    for t in load_todos():
        if t["id"] == todo_id:
            return t
    raise HTTPException(status_code=404, detail="To-Do item not found")