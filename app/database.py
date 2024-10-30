from sqlalchemy import create_engine, Column, Integer, String, Boolean # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker, relationship # type: ignore

DATABASE_URL = "postgresql://postgres:admin@bd-todo-flask-container:5432/todo"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()