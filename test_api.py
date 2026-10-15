
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import app
from database import Base, get_db


# Create a separate, in-memory test database.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


# Replace the real MySQL dependency during testing.
def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# Create a clean database for each test.
@pytest.fixture(autouse=True)
def prepare_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to TaskFlow API!"


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Learn automated testing"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Learn automated testing"
    assert response.json()["status"] == "pending"
    assert isinstance(response.json()["id"], int)


def test_get_missing_task():
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_complete_task():
    created = client.post(
        "/tasks",
        json={"title": "Practice API testing"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "completed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_delete_task():
    created = client.post(
        "/tasks",
        json={"title": "Temporary task"},
    )
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_filter_and_sort_tasks():
    first = client.post(
        "/tasks",
        json={"title": "First task"},
    ).json()

    second = client.post(
        "/tasks",
        json={"title": "Second task"},
    ).json()

    client.patch(
        f"/tasks/{first['id']}",
        json={"status": "completed"},
    )

    response = client.get(
        "/tasks",
        params={"status": "completed", "sort": "desc"},
    )

    assert response.status_code == 200

    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] == first["id"]
    assert result[0]["status"] == "completed"


def test_pagination():
    for title in ["Task A", "Task B", "Task C"]:
        response = client.post("/tasks", json={"title": title})
        assert response.status_code == 201

    response = client.get(
        "/tasks",
        params={"limit": 2, "offset": 0, "sort": "asc"},
    )

    assert response.status_code == 200

    result = response.json()
    assert len(result) == 2
    assert result[0]["id"] < result[1]["id"]


def test_blank_title_is_rejected():
    response = client.post(
        "/tasks",
        json={"title": "   "},
    )

    assert response.status_code == 422
