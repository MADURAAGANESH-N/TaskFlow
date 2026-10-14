
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

# Load database settings from .env
load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

if not db_user or db_password is None:
    raise RuntimeError(
        "Set DB_USER and DB_PASSWORD in your .env file."
    )

# Build the connection URL safely, including special characters
# in the username or password.
database_url = URL.create(
    drivername="mysql+pymysql",
    username=db_user,
    password=db_password,
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "taskflow_db"),
)

# Create the database engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

# Create database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Base class for our database models
Base = declarative_base()


# Provide a session to API endpoints
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
