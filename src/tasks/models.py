from sqlalchemy import (
    Integer,
    String,
    Column,
    ForeignKey,
    Boolean
)

from src.database import Base


class Task(Base):
    __tablename__= "task"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)