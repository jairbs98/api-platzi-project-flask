from sqlalchemy import Column, Integer, String, Boolean, ForeignKey  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from ..database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    done = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")
