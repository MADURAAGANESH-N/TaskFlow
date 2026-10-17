from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from auth import get_current_user, router as auth_router
from database import Base, engine, get_db
from models import TaskModel, UserModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TaskFlow API",
    description="A task management API using FastAPI and MySQL",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)


# Request model for creating a task
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be blank")

        return value


# Request model for updating a task
class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )
    status: Literal["pending", "completed"] | None = None


# Response model: converts SQLAlchemy objects to API responses
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: Literal["pending", "completed"]


@app.get("/")
def home():
    return {"message": "Welcome to TaskFlow API!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}



# Get all tasks with filtering, sorting, and pagination

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    status: Literal["pending", "completed"] | None = None,
    sort: Literal["asc", "desc"] = "asc",
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # Retrieve only this user's tasks
    query = db.query(TaskModel).filter(
        TaskModel.user_id == current_user.id
    )

    if status is not None:
        query = query.filter(TaskModel.status == status)

    if sort == "desc":
        query = query.order_by(TaskModel.id.desc())
    else:
        query = query.order_by(TaskModel.id.asc())

    return query.offset(offset).limit(limit).all()



# Get one task by ID

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = (
        db.query(TaskModel)
        .filter(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task




# Create and save a task in MySQL

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = TaskModel(
        title=data.title,
        status="pending",
        user_id=current_user.id,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task



# Update a task in MySQL

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = (
        db.query(TaskModel)
        .filter(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="Provide a title or status to update",
        )

    if "title" in changes:
        new_title = changes["title"]

        if new_title is None or not new_title.strip():
            raise HTTPException(
                status_code=422,
                detail="Title cannot be blank",
            )

        changes["title"] = new_title.strip()

    if "status" in changes and changes["status"] is None:
        raise HTTPException(
            status_code=422,
            detail="Status cannot be null",
        )

    for field, value in changes.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


# Delete a task from MySQL

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = (
        db.query(TaskModel)
        .filter(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return None
