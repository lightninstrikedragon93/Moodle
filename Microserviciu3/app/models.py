from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum

from database import Base

class User(Base):
    __tablename__ = "users"

    uid = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(SQLAlchemyEnum('student', 'profesor', 'admin', name='user_roles'))