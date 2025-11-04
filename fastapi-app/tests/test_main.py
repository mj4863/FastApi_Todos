import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
import main  # import module to allow monkeypatching attributes
import importlib
from main import app, save_todos, load_todos, TodoItem

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolate_storage(monkeypatch, tmp_path):
    # 각 테스트마다 별도 임시 todo.json을 사용해 파일 I/O 오염 방지
    tmp_file = tmp_path / "todo.json"
    monkeypatch.setattr(main, "TODO_FILE", tmp_file, raising=True)
    # 초기화
    save_todos([])
    yield
    # 정리
    save_todos([])

def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_todos_with_items():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test"
    assert data[0]["completed"] is False

def test_create_todo():
    todo = {"id": 1, "title": "Test", "description": "Test description", "completed": False}
    response = client.post("/todos", json=todo)
    # 앱이 status_code=200을 반환함
    assert response.status_code == 200
    assert response.json()["title"] == "Test"

def test_create_todo_invalid():
    # description 누락 -> 422
    todo = {"id": 1, "title": "Test"}
    response = client.post("/todos", json=todo)
    assert response.status_code == 422

def test_create_todo_duplicate_id():
    t = TodoItem(id=1, title="A", description="B", completed=False)
    save_todos([t.model_dump()])
    response = client.post("/todos", json=t.model_dump())
    assert response.status_code == 409
    assert response.json()["detail"] == "Duplicate id"

def test_update_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])
    updated_todo = {"id": 999, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    data = response.json()
    # URL의 id가 우선되므로 1로 유지
    assert data["id"] == 1
    assert data["title"] == "Updated"
    assert data["completed"] is True

def test_update_todo_not_found():
    updated_todo = {"id": 1, "title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 404
    assert response.json()["detail"] == "To-Do item not found"

def test_delete_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.model_dump()])
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"
    # 삭제 확인
    assert load_todos() == []

def test_delete_todo_not_found():
    response = client.delete("/todos/1")
    # 앱 로직: 없으면 404
    assert response.status_code == 404
    assert response.json()["detail"] == "To-Do item not found"

# ===== 선택적 보강 테스트 =====

def test_get_single_todo():
    todo = TodoItem(id=42, title="One", description="Only", completed=True)
    save_todos([todo.model_dump()])
    r = client.get("/todos/42")
    assert r.status_code == 200
    assert r.json()["title"] == "One"

def test_get_single_todo_not_found():
    r = client.get("/todos/999")
    assert r.status_code == 404
    assert r.json()["detail"] == "To-Do item not found"

def test_filter_completed_true_false():
    items = [
        TodoItem(id=1, title="A", description="a", completed=False).model_dump(),
        TodoItem(id=2, title="B", description="b", completed=True).model_dump(),
        TodoItem(id=3, title="C", description="c", completed=True).model_dump(),
    ]
    save_todos(items)

    r_all = client.get("/todos")
    assert r_all.status_code == 200
    assert len(r_all.json()) == 3

    r_true = client.get("/todos?completed=true")
    assert r_true.status_code == 200
    assert {t["id"] for t in r_true.json()} == {2, 3}

    r_false = client.get("/todos?completed=false")
    assert r_false.status_code == 200
    assert {t["id"] for t in r_false.json()} == {1}

def test_health_and_version():
    r1 = client.get("/health")
    assert r1.status_code == 200
    assert r1.json()["status"] == "ok"

    r2 = client.get("/version")
    assert r2.status_code == 200
    assert "version" in r2.json()

def test_validator_empty_title_returns_422():
    # title이 공백 → field_validator에서 ValueError → 422
    r = client.post("/todos", json={
        "id": 1,
        "title": "   ",
        "description": "desc",
        "completed": False
    })
    assert r.status_code == 422

def test_corrupted_json_returns_empty_list(monkeypatch, tmp_path):
    # 손상된 JSON 파일 준비
    bad = tmp_path / "todo.json"
    bad.write_text("{this is not valid json}", encoding="utf-8")
    # 환경변수로 main.TODO_FILE 경로 주입
    monkeypatch.setenv("TODO_FILE", str(bad))
    importlib.reload(main)  # env 반영 위해 리로드
    local_client = TestClient(main.app)

    r = local_client.get("/todos")
    assert r.status_code == 200
    assert r.json() == []  # except json.JSONDecodeError -> return []

def test_missing_file_returns_empty_list(monkeypatch, tmp_path):
    missing = tmp_path / "no_such.json"  # 존재하지 않음
    monkeypatch.setenv("TODO_FILE", str(missing))
    importlib.reload(main)
    local_client = TestClient(main.app)

    r = local_client.get("/todos")
    assert r.status_code == 200
    assert r.json() == []  # 파일 없을 때 return []

def test_root_returns_500_when_index_missing(monkeypatch, tmp_path):
    # INDEX_HTML을 임시 경로로 바꿔서 존재하지 않게 만듦
    dummy_index = tmp_path / "index.html"  # 아직 생성 안 함
    monkeypatch.setattr(main, "INDEX_HTML", dummy_index, raising=False)

    r = client.get("/")
    assert r.status_code == 500
    assert "index.html not found" in r.text

def test_root_returns_content_when_index_exists(monkeypatch, tmp_path):
    # INDEX_HTML을 임시 파일로 바꾸고 실제로 생성
    dummy_index = tmp_path / "index.html"
    dummy_index.write_text("<h1>Hello</h1>", encoding="utf-8")
    monkeypatch.setattr(main, "INDEX_HTML", dummy_index, raising=False)

    r = client.get("/")
    assert r.status_code == 200
    assert "<h1>Hello</h1>" in r.text