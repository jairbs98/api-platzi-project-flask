class Config:
    SECRET_KEY = "SUPER SECRET"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:admin@bd-todo-flask-container:5432/todo"
    )
