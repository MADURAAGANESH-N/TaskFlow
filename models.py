
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)

from database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    password_hash = Column(String(255), nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    title = Column(String(120), nullable=False)

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
