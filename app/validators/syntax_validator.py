import re
from email_validator import validate_email, EmailNotValidError


def validate_syntax(email: str) -> dict:
    """
    Validates email syntax using regex and email_validator library.
    
    Returns:
        dict: {
            'is_valid': bool,
            'normalized_email': str or None,
            'domain': str or None,
            'error': str or None
        }
    """
    result = {
        'is_valid': False,
        'normalized_email': None,
        'domain': None,
        'error': None
    }
    
    # Basic regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        result['error'] = "Invalid email format"
        return result
    
    try:
        # Use email_validator library for more robust validation
        validated = validate_email(email, check_deliverability=False)
        result['is_valid'] = True
        result['normalized_email'] = validated.normalized
        result['domain'] = validated.domain
    except EmailNotValidError as e:
        result['error'] = str(e)
    
    return result
