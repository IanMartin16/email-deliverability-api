from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class EmailValidationRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to validate")
    check_smtp: bool = Field(default=True, description="Perform SMTP mailbox verification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "check_smtp": True
            }
        }


class MXRecord(BaseModel):
    host: str
    priority: int


class EmailValidationResponse(BaseModel):
    email: str
    is_valid: bool
    
    # Syntax validation
    syntax_valid: bool
    
    # Domain validation
    domain: str
    has_mx_records: bool
    mx_records: Optional[list[MXRecord]] = None
    
    # Disposable email detection
    is_disposable: bool
    
    # SMTP validation
    smtp_check_performed: bool = False
    mailbox_exists: Optional[bool] = None
    smtp_response: Optional[str] = None
    is_catch_all: Optional[bool] = None
    
    # Overall score
    deliverability_score: float = Field(
        ..., 
        ge=0, 
        le=100,
        description="Overall deliverability score (0-100)"
    )
    
    # Metadata
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "is_valid": True,
                "syntax_valid": True,
                "domain": "example.com",
                "has_mx_records": True,
                "mx_records": [
                    {"host": "mail.example.com", "priority": 10}
                ],
                "is_disposable": False,
                "smtp_check_performed": True,
                "mailbox_exists": True,
                "smtp_response": "250 OK",
                "deliverability_score": 95.0,
                "checked_at": "2024-02-12T10:30:00Z",
                "processing_time_ms": 1234.56
            }
        }


class BulkValidationRequest(BaseModel):
    emails: list[EmailStr] = Field(..., max_length=100, description="List of emails to validate (max 100)")
    check_smtp: bool = Field(default=False, description="Perform SMTP checks (slower)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "emails": ["user1@example.com", "user2@example.com"],
                "check_smtp": False
            }
        }


class BulkValidationResponse(BaseModel):
    total_checked: int
    results: list[EmailValidationResponse]
    processing_time_ms: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_checked": 2,
                "results": [],
                "processing_time_ms": 2500.0
            }
        }


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
