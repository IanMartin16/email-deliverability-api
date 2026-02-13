"""
Quick test script to validate the email validation service
"""

import asyncio
from app.services.validator import email_validator


async def test_emails():
    """Test various email scenarios"""
    
    test_cases = [
        # Valid emails
        "john.doe@gmail.com",
        "support@microsoft.com",
        "test@example.com",
        
        # Invalid syntax
        "invalid.email",
        "missing@domain",
        "@nodomain.com",
        
        # Disposable emails
        "temp@tempmail.com",
        "test@mailinator.com",
        "throwaway@10minutemail.com",
        
        # Non-existent domains
        "user@thisdoesnotexist12345.com",
    ]
    
    print("=" * 80)
    print("EMAIL VALIDATION TESTS")
    print("=" * 80)
    
    for email in test_cases:
        print(f"\n📧 Testing: {email}")
        print("-" * 80)
        
        result = await email_validator.validate_email(email, check_smtp=False)
        
        print(f"✓ Valid: {result['is_valid']}")
        print(f"✓ Syntax Valid: {result['syntax_valid']}")
        print(f"✓ Has MX: {result['has_mx_records']}")
        print(f"✓ Disposable: {result['is_disposable']}")
        print(f"✓ Score: {result['deliverability_score']}/100")
        
        if result['mx_records']:
            print(f"✓ MX Records: {len(result['mx_records'])} found")
            for mx in result['mx_records'][:3]:  # Show first 3
                print(f"  - {mx.host} (priority: {mx.priority})")


if __name__ == "__main__":
    asyncio.run(test_emails())
