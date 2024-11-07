from flask_login import UserMixin  # type: ignore
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from ..database import Base


class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    todos = relationship("Todo", back_populates="owner")
