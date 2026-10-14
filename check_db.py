
from sqlalchemy import text

from database import engine


def check_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT DATABASE(), VERSION()")
        ).one()

        print("MySQL connection successful!")
        print(f"Database: {result[0]}")
        print(f"MySQL version: {result[1]}")


if __name__ == "__main__":
    try:
        check_connection()
    except Exception as exc:
        print("Database connection failed.")
        print(f"Error type: {type(exc).__name__}")
        print(str(exc))
