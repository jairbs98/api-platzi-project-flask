from .models import User, Todo  # Importa get_user desde models.py
from .database import get_db


def get_users():
    db = next(get_db())
    return db.query(User).all()


def get_user(username):
    db = next(get_db())
    return db.query(User).filter(User.username == username).first()


def create_user(user_data):
    db = next(get_db())
    db_user = User(
        username=user_data.username, email=user_data.email, password=user_data.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_todos(user_id):
    db = next(get_db())
    return db.query(Todo).filter(Todo.owner_id == user_id).all()


def create_todo(user_id, description):
    db = next(get_db())
    db_todo = Todo(description=description, owner_id=user_id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(user_id, todo_id):
    db = next(get_db())
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user_id).first()
    if todo:
        db.delete(todo)
        db.commit()


def update_todo(user_id, todo_id, done):
    db = next(get_db())
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user_id).first()
    if todo:
        todo.done = not done
        db.commit()
