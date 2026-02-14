from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.schemas import (
    EmailValidationRequest,
    EmailValidationResponse,
    BulkValidationRequest,
    BulkValidationResponse,
    HealthResponse
)
from app.services.validator import email_validator
from app.services.logger import validation_logger
from app.core.config import settings
from app.core.database import get_db
import time
from datetime import datetime
from typing import Optional

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


@router.post("/validate", response_model=EmailValidationResponse)
async def validate_email(
    request: EmailValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate a single email address
    
    This endpoint performs comprehensive email validation including:
    - Syntax validation
    - MX record verification
    - Disposable email detection
    - Optional SMTP mailbox verification
    
    Returns a deliverability score from 0-100.
    """
    start_time = time.time()
    
    try:
        # Perform validation
        result = await email_validator.validate_email(
            email=request.email,
            check_smtp=request.check_smtp
        )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Build response
        response = EmailValidationResponse(
            email=result["email"],
            is_valid=result["is_valid"],
            syntax_valid=result["syntax_valid"],
            domain=result["domain"] or "",
            has_mx_records=result["has_mx_records"],
            mx_records=result["mx_records"],
            is_disposable=result["is_disposable"],
            smtp_check_performed=result["smtp_check_performed"],
            mailbox_exists=result["mailbox_exists"],
            smtp_response=result["smtp_response"],
            is_catch_all=result.get("is_catch_all"),
            deliverability_score=result["deliverability_score"],
            processing_time_ms=round(processing_time, 2)
        )
        
        # Log validation to database (optional, no error if DB not available)
        try:
            validation_logger.log_validation(
                db=db,
                email=request.email,
                validation_result=result,
                processing_time_ms=processing_time
            )
        except Exception as log_error:
            # Silently fail if logging doesn't work (DB not configured)
            pass
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )


@router.post("/validate/bulk", response_model=BulkValidationResponse)
async def validate_bulk(request: BulkValidationRequest):
    """
    Validate multiple email addresses
    
    **Limitations:**
    - Maximum 100 emails per request
    - SMTP checks disabled by default for performance
    
    **Use cases:**
    - Batch email list cleaning
    - Import validation
    - Database cleanup
    """
    start_time = time.time()
    
    if len(request.emails) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 emails allowed per bulk request"
        )
    
    results = []
    
    try:
        # Validate each email
        for email in request.emails:
            result = await email_validator.validate_email(
                email=email,
                check_smtp=request.check_smtp
            )
            
            response = EmailValidationResponse(
                email=result["email"],
                is_valid=result["is_valid"],
                syntax_valid=result["syntax_valid"],
                domain=result["domain"] or "",
                has_mx_records=result["has_mx_records"],
                mx_records=result["mx_records"],
                is_disposable=result["is_disposable"],
                smtp_check_performed=result["smtp_check_performed"],
                mailbox_exists=result["mailbox_exists"],
                smtp_response=result["smtp_response"],
                deliverability_score=result["deliverability_score"],
                processing_time_ms=0  # Individual timing not tracked in bulk
            )
            
            results.append(response)
        
        # Calculate total processing time
        total_processing_time = (time.time() - start_time) * 1000
        
        return BulkValidationResponse(
            total_checked=len(results),
            results=results,
            processing_time_ms=round(total_processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk validation error: {str(e)}"
        )


@router.get("/stats")
async def get_stats():
    """
    Get API statistics and usage information
    
    TODO: Implement after database setup
    """
    return {
        "message": "Statistics endpoint - Coming soon",
        "info": "Will track validation counts, success rates, etc."
    }
