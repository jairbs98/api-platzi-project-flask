from flask_login import UserMixin  # type: ignore
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base, get_db  # Importa get_db


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    done = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")


class UserData:
    def __init__(self, username, password, email):  # Agregar email
        self.username = username
        self.password = password
        self.email = email  # Nuevo campo


class UserModel(UserMixin):
    def __init__(self, user_data):
        """
        :param user_data: UserData
        """
        self.id = user_data.username
        self.password = user_data.password
        self.email = user_data.email  # Nuevo campo

    @staticmethod
    def query(user_id):
        user_doc = get_user(user_id)  # Llama a la función get_user local
        user_data = UserData(
            username=user_doc.username,  # Accede al atributo username
            password=user_doc.password,  # Accede al atributo password
            email=user_doc.email,  # Accede al atributo email
        )

        return UserModel(user_data)


def get_user(username, db=None):  # Agrega el argumento db
    if db is None:
        db = next(get_db())  # Crea una nueva sesión solo si no se proporciona
    return db.query(User).filter(User.username == username).first()
