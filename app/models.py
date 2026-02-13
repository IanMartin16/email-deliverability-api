from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from .database import Base


class EmailValidation(Base):
    __tablename__ = "email_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    
    # Validation Results
    is_valid_syntax = Column(Boolean, default=False)
    has_mx_records = Column(Boolean, default=False)
    is_disposable = Column(Boolean, default=False)
    smtp_valid = Column(Boolean, nullable=True)
    
    # Deliverability Score (0-100)
    deliverability_score = Column(Float, nullable=False)
    
    # Additional Info
    domain = Column(String, nullable=True)
    mx_records = Column(String, nullable=True)  # JSON string
    
    # API Usage Tracking
    api_user = Column(String, nullable=True)
    subscription_tier = Column(String, default="free")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<EmailValidation {self.email} - Score: {self.deliverability_score}>"
