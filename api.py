
from typing import Literal

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="TaskFlow API",
    description="A task management API built with Python",
    version="1.0.0",
)


# The data required when creating a task
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be blank")

        return value


# Fields that can be updated
class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None, min_length=1, max_length=120
    )
    status: Literal["pending", "completed"] | None = None


# The task returned by the API
class Task(BaseModel):
    id: int
    title: str
    status: Literal["pending", "completed"] = "pending"


# Temporary in-memory storage
tasks: dict[int, Task] = {}
next_task_id = 1


@app.get("/")
def home():
    return {"message": "Welcome to TaskFlow API!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Read all tasks
@app.get("/tasks", response_model=list[Task])
def get_tasks():
    return list(tasks.values())


# Read one task
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


# Create a task
@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
)
def create_task(data: TaskCreate):
    global next_task_id

    task = Task(
        id=next_task_id,
        title=data.title,
        status="pending",
    )

    tasks[next_task_id] = task
    next_task_id += 1

    return task


# Update a task
@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, data: TaskUpdate):
    task = tasks.get(task_id)

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

    updated_data = task.model_dump()
    updated_data.update(changes)

    updated_task = Task(**updated_data)
    tasks[task_id] = updated_task

    return updated_task


# Delete a task
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    del tasks[task_id]
    return None
