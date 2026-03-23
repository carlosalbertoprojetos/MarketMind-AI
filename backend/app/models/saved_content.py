"""Modelo para conteudos gerados salvos pelo usuario."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class SavedContent(Base):
    __tablename__ = "saved_contents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    source_type = Column(String(32), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    theme = Column(String(255), nullable=True)
    objective = Column(String(64), nullable=True)
    audience = Column(String(255), nullable=True)
    style = Column(String(64), nullable=True)
    platforms_json = Column(Text, nullable=True)
    request_payload = Column(Text, nullable=True)
    result_payload = Column(Text, nullable=False)
    publish_results_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
