from sqlalchemy import Column, DateTime, Integer, String, Text, func
from .database import Base


class WorkflowItem(Base):
    __tablename__ = "workflow_items"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, default="manual")
    title = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
