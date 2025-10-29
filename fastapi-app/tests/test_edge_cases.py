from fastapi.testclient import TestClient
import main  # 앱 모듈
import json

client = TestClient(main.app)

def test_create_todo_rejects_empty_title(tmp_path, monkeypatch):
    # todo 저장 경로를 임시로 바꿔서 부작용 방지
    monkeypatch.setattr(main, "TODO_FILE", tmp_path / "todo.json")
    payload = {
        "id": 1,
        "title": "   ",            # <- validator가 ValueError 발생시키며 422로 매핑됨
        "description": "desc",
        "completed": False,
    }
    r = client.post("/todos", json=payload)
    assert r.status_code == 422
    # 커버: field_validator에서 raise ValueError("must not be empty")

def test_load_todos_returns_empty_on_corrupt_file(tmp_path, monkeypatch):
    bad = tmp_path / "todo.json"
    bad.write_text("{not-a-json", encoding="utf-8")  # JSONDecodeError 유발
    monkeypatch.setattr(main, "TODO_FILE", bad)

    r = client.get("/todos")
    assert r.status_code == 200
    assert r.json() == []  # 손상 시 방어 로직 실행
    # 커버: except json.JSONDecodeError: ... return []

def test_load_todos_returns_empty_on_missing_file(tmp_path, monkeypatch):
    # 파일이 아예 없음
    monkeypatch.setattr(main, "TODO_FILE", tmp_path / "no_such.json")

    r = client.get("/todos")
    assert r.status_code == 200
    assert r.json() == []  # 파일 부재 시 빈 리스트
    # 커버: 최하단 return [] 경로

def test_root_returns_500_when_index_missing(tmp_path, monkeypatch):
    # templates/index.html 부재
    monkeypatch.setattr(main, "INDEX_HTML", tmp_path / "templates" / "index.html")

    r = client.get("/")
    assert r.status_code == 500
    assert "index.html not found" in r.text
    # 커버: if not INDEX_HTML.exists(): 와 500 응답 라인

def test_root_returns_html_when_exists(tmp_path, monkeypatch):
    # templates/index.html 존재
    tdir = tmp_path / "templates"
    tdir.mkdir()
    html_path = tdir / "index.html"
    html_path.write_text("<h1>Hello</h1>", encoding="utf-8")
    monkeypatch.setattr(main, "INDEX_HTML", html_path)

    r = client.get("/")
    assert r.status_code == 200
    assert r.text == "<h1>Hello</h1>"
    # 커버: INDEX_HTML.read_text(...) 반환 라인
