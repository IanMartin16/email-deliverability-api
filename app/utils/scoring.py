"""
Deliverability Score Calculation
Scores emails from 0-100 based on validation results
"""


def calculate_deliverability_score(
    is_valid_syntax: bool,
    has_mx_records: bool,
    is_disposable: bool,
    smtp_valid: bool = None,
    disposable_confidence: str = 'high'
) -> float:
    """
    Calculate deliverability score based on validation results.
    
    Scoring breakdown:
    - Valid syntax: 20 points (base requirement)
    - Has MX records: 30 points (critical for delivery)
    - Not disposable: 25 points
    - SMTP verification: 25 points (if available)
    
    Args:
        is_valid_syntax: Email has valid syntax
        has_mx_records: Domain has MX records
        is_disposable: Email is from disposable provider
        smtp_valid: SMTP verification result (None if not checked)
        disposable_confidence: Confidence level of disposable detection
    
    Returns:
        float: Score from 0-100
    """
    score = 0.0
    
    # 1. Syntax validation (20 points)
    if is_valid_syntax:
        score += 20
    else:
        # If syntax is invalid, score is 0
        return 0.0
    
    # 2. MX Records (30 points)
    if has_mx_records:
        score += 30
    
    # 3. Disposable email check (25 points)
    if not is_disposable:
        score += 25
    elif disposable_confidence == 'medium':
        # Give partial credit for medium confidence
        score += 10
    
    # 4. SMTP Verification (25 points)
    if smtp_valid is True:
        score += 25
    elif smtp_valid is False:
        score += 0
    elif smtp_valid is None:
        # If SMTP check wasn't performed or was inconclusive,
        # give partial credit based on other factors
        if has_mx_records and not is_disposable:
            score += 15
        else:
            score += 5
    
    return round(score, 2)


def get_score_category(score: float) -> str:
    """
    Categorize the deliverability score.
    
    Returns:
        str: Category name (Excellent, Good, Fair, Poor, Invalid)
    """
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    elif score > 0:
        return "Poor"
    else:
        return "Invalid"


def get_risk_level(score: float) -> str:
    """
    Determine risk level for email delivery.
    
    Returns:
        str: Risk level (Low, Medium, High, Very High)
    """
    if score >= 80:
        return "Low"
    elif score >= 60:
        return "Medium"
    elif score >= 40:
        return "High"
    else:
        return "Very High"


def get_recommendations(
    score: float,
    is_valid_syntax: bool,
    has_mx_records: bool,
    is_disposable: bool,
    smtp_valid: bool = None
) -> list:
    """
    Generate recommendations based on validation results.
    
    Returns:
        list: List of recommendation strings
    """
    recommendations = []
    
    if not is_valid_syntax:
        recommendations.append("Email syntax is invalid. Verify the email format.")
    
    if not has_mx_records:
        recommendations.append("Domain has no MX records. Email delivery will fail.")
    
    if is_disposable:
        recommendations.append("This is a disposable/temporary email. Consider blocking for important communications.")
    
    if smtp_valid is False:
        recommendations.append("Mailbox does not exist or is not accepting mail.")
    elif smtp_valid is None and has_mx_records:
        recommendations.append("Could not verify mailbox existence. Server may block verification attempts.")
    
    if score >= 90:
        recommendations.append("Email appears highly deliverable.")
    elif score >= 70:
        recommendations.append("Email should be deliverable with low risk.")
    elif score >= 50:
        recommendations.append("Email may be deliverable but has some concerns.")
    elif score < 50 and score > 0:
        recommendations.append("Email has significant deliverability issues.")
    
    return recommendations
