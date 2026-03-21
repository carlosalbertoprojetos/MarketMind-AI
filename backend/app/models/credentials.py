"""
Modelo de credenciais para login em URLs externas (sites que exigem autenticação no scraping).
Armazena referência ao usuário e dados criptografados de login.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Credentials(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    site_name = Column(String(255), nullable=False)  # rótulo ex: "Meu Site"
    login_url = Column(String(2048), nullable=True)   # URL da página de login
    username_encrypted = Column(String(512), nullable=True)
    password_encrypted = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # user = relationship("User", back_populates="credentials")
