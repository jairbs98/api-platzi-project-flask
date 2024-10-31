from flask_login import UserMixin  # type: ignore
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from .database import Base, get_db


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    done = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")


class UserData:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


class UserModel(UserMixin):
    def __init__(self, user_data):
        """
        :param user_data: UserData
        """
        self.id = user_data.username
        self.password = user_data.password
        self.email = user_data.email

    @staticmethod
    def query(user_id):
        user_doc = get_user(user_id)
        user_data = UserData(
            username=user_doc.username,
            password=user_doc.password,
            email=user_doc.email,
        )

        return UserModel(user_data)


def get_user(username, db=None):
    if db is None:
        db = next(get_db())
    return db.query(User).filter(User.username == username).first()
