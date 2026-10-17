
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import app
from database import Base, get_db


# Use an isolated database for automated tests.
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


# Replace the production database dependency.
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def prepare_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# Create an account and return its JWT authorization header.
def register_and_login(username, password="StrongTestPass123!"):
    registered = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
        },
    )
    assert registered.status_code == 201

    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers():
    return register_and_login("test_user")


def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_register_duplicate_username():
    payload = {
        "username": "duplicate_user",
        "password": "StrongTestPass123!",
    }

    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_invalid_password():
    client.post(
        "/auth/register",
        json={
            "username": "login_user",
            "password": "StrongTestPass123!",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login_user",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_tasks_require_authentication():
    response = client.get("/tasks")
    assert response.status_code == 401


def test_create_task(auth_headers):
    response = client.post(
        "/tasks",
        json={"title": "Learn automated testing"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Learn automated testing"
    assert response.json()["status"] == "pending"


def test_get_missing_task(auth_headers):
    response = client.get("/tasks/999", headers=auth_headers)

    assert response.status_code == 404


def test_complete_task(auth_headers):
    created = client.post(
        "/tasks",
        json={"title": "Practice API testing"},
        headers=auth_headers,
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "completed"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_delete_task(auth_headers):
    created = client.post(
        "/tasks",
        json={"title": "Temporary task"},
        headers=auth_headers,
    )
    task_id = created.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    follow_up = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers,
    )
    assert follow_up.status_code == 404


def test_filter_and_sort_tasks(auth_headers):
    first = client.post(
        "/tasks",
        json={"title": "First task"},
        headers=auth_headers,
    ).json()

    client.post(
        "/tasks",
        json={"title": "Second task"},
        headers=auth_headers,
    )

    client.patch(
        f"/tasks/{first['id']}",
        json={"status": "completed"},
        headers=auth_headers,
    )

    response = client.get(
        "/tasks",
        params={"status": "completed", "sort": "desc"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert result[0]["id"] == first["id"]


def test_pagination(auth_headers):
    for title in ["Task A", "Task B", "Task C"]:
        response = client.post(
            "/tasks",
            json={"title": title},
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get(
        "/tasks",
        params={"limit": 2, "offset": 0, "sort": "asc"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    result = response.json()

    assert len(result) == 2
    assert result[0]["id"] < result[1]["id"]


def test_blank_title_is_rejected(auth_headers):
    response = client.post(
        "/tasks",
        json={"title": "   "},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_users_cannot_access_each_others_tasks():
    # User A creates a task.
    user_a_headers = register_and_login("user_a")

    created = client.post(
        "/tasks",
        json={"title": "Private task for User A"},
        headers=user_a_headers,
    )
    assert created.status_code == 201

    task_id = created.json()["id"]

    # User B logs in using a separate account.
    user_b_headers = register_and_login("user_b")

    # User B must not see User A's task.
    response = client.get("/tasks", headers=user_b_headers)
    assert response.status_code == 200
    assert response.json() == []

    # Direct access, updating, and deleting should all be rejected.
    response = client.get(
        f"/tasks/{task_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 404

    response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "completed"},
        headers=user_b_headers,
    )
    assert response.status_code == 404

    response = client.delete(
        f"/tasks/{task_id}",
        headers=user_b_headers,
    )
    assert response.status_code == 404

    # User A's task must remain unchanged.
    response = client.get(
        f"/tasks/{task_id}",
        headers=user_a_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
