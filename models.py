
from sqlalchemy import Column, Integer, String, DateTime, func

from database import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    title = Column(
        String(120),
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
