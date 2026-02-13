from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import json

from ..database import get_db
from ..models import EmailValidation
from ..config import get_settings
from ..validators import (
    validate_syntax,
    check_mx_records,
    is_disposable,
    verify_smtp
)
from ..utils import (
    calculate_deliverability_score,
    get_score_category,
    get_risk_level,
    get_recommendations
)

router = APIRouter(prefix="/email", tags=["Email Validation"])
settings = get_settings()


# Pydantic Models
class EmailCheckRequest(BaseModel):
    email: EmailStr
    check_smtp: Optional[bool] = Field(
        default=True,
        description="Enable SMTP mailbox verification (slower but more accurate)"
    )


class EmailCheckResponse(BaseModel):
    email: str
    is_valid: bool
    
    # Validation Details
    syntax_valid: bool
    has_mx_records: bool
    is_disposable: bool
    smtp_verified: Optional[bool]
    
    # Deliverability
    deliverability_score: float
    score_category: str
    risk_level: str
    
    # Additional Info
    domain: Optional[str]
    mx_records: Optional[List[str]]
    recommendations: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "is_valid": True,
                "syntax_valid": True,
                "has_mx_records": True,
                "is_disposable": False,
                "smtp_verified": True,
                "deliverability_score": 95.0,
                "score_category": "Excellent",
                "risk_level": "Low",
                "domain": "example.com",
                "mx_records": ["mail.example.com"],
                "recommendations": ["Email appears highly deliverable."]
            }
        }


class BatchEmailCheckRequest(BaseModel):
    emails: List[EmailStr] = Field(..., max_items=100, description="List of emails to validate (max 100)")
    check_smtp: Optional[bool] = Field(default=False, description="Enable SMTP verification for batch")


class BatchEmailCheckResponse(BaseModel):
    total_checked: int
    results: List[EmailCheckResponse]


@router.post("/validate", response_model=EmailCheckResponse, summary="Validate a single email")
async def validate_email(
    request: EmailCheckRequest,
    db: Session = Depends(get_db),
    x_rapidapi_user: Optional[str] = Header(None, alias="X-RapidAPI-User"),
    x_rapidapi_subscription: Optional[str] = Header(None, alias="X-RapidAPI-Subscription")
):
    """
    Comprehensive email validation with deliverability scoring.
    
    **Checks performed:**
    - ✅ Syntax validation
    - ✅ MX record verification
    - ✅ Disposable email detection
    - ✅ SMTP mailbox verification (optional, slower)
    
    **Returns:**
    - Deliverability score (0-100)
    - Risk assessment
    - Detailed validation results
    - Actionable recommendations
    """
    
    # 1. Syntax Validation
    syntax_result = validate_syntax(request.email)
    
    if not syntax_result['is_valid']:
        return EmailCheckResponse(
            email=request.email,
            is_valid=False,
            syntax_valid=False,
            has_mx_records=False,
            is_disposable=False,
            smtp_verified=None,
            deliverability_score=0.0,
            score_category="Invalid",
            risk_level="Very High",
            domain=None,
            mx_records=None,
            recommendations=["Email syntax is invalid. Verify the email format."]
        )
    
    domain = syntax_result['domain']
    
    # 2. MX Record Check
    mx_result = check_mx_records(domain)
    has_mx = mx_result['has_mx']
    mx_records = mx_result['mx_records'] if has_mx else None
    
    # 3. Disposable Email Check
    disposable_result = is_disposable(domain)
    is_disposable_email = disposable_result['is_disposable']
    disposable_confidence = disposable_result['confidence']
    
    # 4. SMTP Verification (optional)
    smtp_valid = None
    if request.check_smtp and has_mx and mx_records:
        smtp_result = verify_smtp(request.email, mx_records[0], timeout=settings.SMTP_TIMEOUT)
        smtp_valid = smtp_result['smtp_valid']
    
    # 5. Calculate Deliverability Score
    score = calculate_deliverability_score(
        is_valid_syntax=True,
        has_mx_records=has_mx,
        is_disposable=is_disposable_email,
        smtp_valid=smtp_valid,
        disposable_confidence=disposable_confidence
    )
    
    category = get_score_category(score)
    risk = get_risk_level(score)
    recommendations = get_recommendations(
        score=score,
        is_valid_syntax=True,
        has_mx_records=has_mx,
        is_disposable=is_disposable_email,
        smtp_valid=smtp_valid
    )
    
    # 6. Save to database
    validation = EmailValidation(
        email=request.email,
        is_valid_syntax=True,
        has_mx_records=has_mx,
        is_disposable=is_disposable_email,
        smtp_valid=smtp_valid,
        deliverability_score=score,
        domain=domain,
        mx_records=json.dumps(mx_records) if mx_records else None,
        api_user=x_rapidapi_user or "anonymous",
        subscription_tier=x_rapidapi_subscription or "free"
    )
    db.add(validation)
    db.commit()
    
    # 7. Return response
    return EmailCheckResponse(
        email=request.email,
        is_valid=score > 0,
        syntax_valid=True,
        has_mx_records=has_mx,
        is_disposable=is_disposable_email,
        smtp_verified=smtp_valid,
        deliverability_score=score,
        score_category=category,
        risk_level=risk,
        domain=domain,
        mx_records=mx_records,
        recommendations=recommendations
    )


@router.post("/validate/batch", response_model=BatchEmailCheckResponse, summary="Validate multiple emails")
async def validate_batch(
    request: BatchEmailCheckRequest,
    db: Session = Depends(get_db),
    x_rapidapi_user: Optional[str] = Header(None, alias="X-RapidAPI-User")
):
    """
    Validate up to 100 emails in a single request.
    
    **Note:** SMTP verification is disabled by default for batch requests to improve speed.
    Set `check_smtp: true` to enable (will be slower).
    """
    
    results = []
    
    for email in request.emails:
        try:
            # Create individual request
            single_request = EmailCheckRequest(email=email, check_smtp=request.check_smtp)
            
            # Validate
            result = await validate_email(
                request=single_request,
                db=db,
                x_rapidapi_user=x_rapidapi_user
            )
            results.append(result)
            
        except Exception as e:
            # If validation fails, add error result
            results.append(EmailCheckResponse(
                email=str(email),
                is_valid=False,
                syntax_valid=False,
                has_mx_records=False,
                is_disposable=False,
                smtp_verified=None,
                deliverability_score=0.0,
                score_category="Invalid",
                risk_level="Very High",
                domain=None,
                mx_records=None,
                recommendations=[f"Error: {str(e)}"]
            ))
    
    return BatchEmailCheckResponse(
        total_checked=len(results),
        results=results
    )


@router.get("/stats", summary="Get validation statistics")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get overall validation statistics.
    """
    total_validations = db.query(EmailValidation).count()
    valid_emails = db.query(EmailValidation).filter(EmailValidation.deliverability_score > 70).count()
    disposable_emails = db.query(EmailValidation).filter(EmailValidation.is_disposable == True).count()
    
    avg_score = db.query(EmailValidation).with_entities(
        db.func.avg(EmailValidation.deliverability_score)
    ).scalar() or 0
    
    return {
        "total_validations": total_validations,
        "valid_emails": valid_emails,
        "disposable_emails": disposable_emails,
        "average_score": round(float(avg_score), 2)
    }
