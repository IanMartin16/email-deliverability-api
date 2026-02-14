"""
Database models for SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class ValidationLog(Base):
    """
    Registro de cada validación de email realizada
    """
    __tablename__ = "validation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Email validation data
    email = Column(String(255), index=True, nullable=False)
    domain = Column(String(255), index=True)
    
    # Validation results
    is_valid = Column(Boolean, default=False)
    syntax_valid = Column(Boolean, default=False)
    has_mx_records = Column(Boolean, default=False)
    is_disposable = Column(Boolean, default=False)
    
    # SMTP results
    smtp_check_performed = Column(Boolean, default=False)
    mailbox_exists = Column(Boolean, nullable=True)
    smtp_response = Column(Text, nullable=True)
    is_catch_all = Column(Boolean, nullable=True)
    
    # Score
    deliverability_score = Column(Float, default=0.0)
    
    # Processing info
    processing_time_ms = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="validation_logs")
    api_key = relationship("ApiKey", back_populates="validation_logs")


class User(Base):
    """
    Usuario del sistema
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True)
    
    # Plan information
    plan = Column(String(50), default="free")  # free, basic, pro
    monthly_quota = Column(Integer, default=100)
    validations_used = Column(Integer, default=0)
    
    # Reset tracking
    quota_reset_at = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    validation_logs = relationship("ValidationLog", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")


class ApiKey(Base):
    """
    API Keys para autenticación
    """
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100))  # Nombre descriptivo de la key
    
    # Association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True))
    total_requests = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    validation_logs = relationship("ValidationLog", back_populates="api_key")


class DisposableDomain(Base):
    """
    Lista de dominios de emails desechables/temporales
    
    Esta tabla permite agregar dominios dinámicamente
    """
    __tablename__ = "disposable_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, index=True, nullable=False)
    
    # Metadata
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    verified = Column(Boolean, default=False)  # Si ha sido verificado manualmente
    
    # Source tracking
    source = Column(String(100))  # De dónde vino este dominio (manual, api, etc.)


class UsageStats(Base):
    """
    Estadísticas agregadas de uso por día
    """
    __tablename__ = "usage_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), index=True, nullable=False)
    
    # User stats
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Validation counts
    total_validations = Column(Integer, default=0)
    valid_emails = Column(Integer, default=0)
    invalid_emails = Column(Integer, default=0)
    disposable_detected = Column(Integer, default=0)
    smtp_checks_performed = Column(Integer, default=0)
    
    # Performance
    avg_processing_time_ms = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
