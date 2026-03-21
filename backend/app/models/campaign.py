"""
Modelo de campanha: título, conteúdo, plataforma e agendamento.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    platform = Column(String(64), nullable=True)  # instagram, facebook, linkedin, etc.
    schedule = Column(DateTime(timezone=True), nullable=True)  # data/hora agendada
    reminder_sent_at = Column(DateTime(timezone=True), nullable=True)  # último lembrete enviado
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
