"""
Test script for SMTP email validation

Tests the new SMTP verification functionality
"""

import asyncio
from app.services.validator import email_validator


async def test_smtp_validation():
    """Test SMTP validation with various email providers"""
    
    test_cases = [
        # Gmail - should work
        {
            "email": "test@gmail.com",
            "description": "Gmail (popular provider)",
            "check_smtp": True
        },
        # Yahoo - should work
        {
            "email": "test@yahoo.com",
            "description": "Yahoo Mail",
            "check_smtp": True
        },
        # Outlook - should work
        {
            "email": "test@outlook.com",
            "description": "Outlook/Hotmail",
            "check_smtp": True
        },
        # Non-existent email
        {
            "email": "thisemaildefin itelydoesnotexist12345@gmail.com",
            "description": "Non-existent Gmail address",
            "check_smtp": True
        },
        # Disposable email
        {
            "email": "test@tempmail.com",
            "description": "Disposable email (TempMail)",
            "check_smtp": False
        },
        # Invalid domain
        {
            "email": "test@thisdoesnotexist987654321.com",
            "description": "Non-existent domain",
            "check_smtp": False
        }
    ]
    
    print("=" * 100)
    print("SMTP EMAIL VALIDATION TESTS - PHASE 2")
    print("=" * 100)
    print("\n⚠️  NOTE: SMTP checks may take 2-10 seconds per email")
    print("⚠️  Some mail servers may block or timeout - this is normal\n")
    
    for idx, test_case in enumerate(test_cases, 1):
        email = test_case["email"]
        description = test_case["description"]
        check_smtp = test_case["check_smtp"]
        
        print(f"\n[{idx}/{len(test_cases)}] Testing: {email}")
        print(f"Description: {description}")
        print(f"SMTP Check: {'Yes ✓' if check_smtp else 'No ✗'}")
        print("-" * 100)
        
        try:
            result = await email_validator.validate_email(
                email=email,
                check_smtp=check_smtp
            )
            
            # Display results
            print(f"✅ Valid: {result['is_valid']}")
            print(f"📝 Syntax Valid: {result['syntax_valid']}")
            print(f"🌐 Domain: {result['domain']}")
            print(f"📬 Has MX: {result['has_mx_records']}")
            print(f"🚫 Disposable: {result['is_disposable']}")
            
            if check_smtp:
                print(f"\n📨 SMTP Verification:")
                print(f"   Performed: {result['smtp_check_performed']}")
                if result['smtp_check_performed']:
                    print(f"   Mailbox Exists: {result['mailbox_exists']}")
                    print(f"   Response: {result['smtp_response']}")
                    if result.get('is_catch_all'):
                        print(f"   ⚠️  Catch-All Domain: {result['is_catch_all']}")
            
            # Score
            score = result['deliverability_score']
            if score >= 90:
                emoji = "🟢"
            elif score >= 70:
                emoji = "🟡"
            else:
                emoji = "🔴"
            
            print(f"\n{emoji} Deliverability Score: {score}/100")
            
            # MX Records (if available)
            if result['mx_records']:
                print(f"\n📧 MX Records ({len(result['mx_records'])} found):")
                for mx in result['mx_records'][:3]:
                    print(f"   - {mx.host} (priority: {mx.priority})")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 100)
    print("TESTS COMPLETED")
    print("=" * 100)
    print("\n💡 TIP: For production, cache SMTP results to avoid hitting rate limits")
    print("💡 TIP: Not all mail servers allow SMTP verification (security policy)")


async def test_single_email_detailed():
    """
    Test a single email with detailed output
    """
    print("\n" + "=" * 100)
    print("DETAILED SINGLE EMAIL TEST")
    print("=" * 100)
    
    # You can change this to test your own email
    test_email = "support@google.com"
    
    print(f"\nTesting: {test_email}")
    print("Performing full validation with SMTP check...\n")
    
    result = await email_validator.validate_email(
        email=test_email,
        check_smtp=True
    )
    
    import json
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    print("\n🚀 Starting SMTP Validation Tests...")
    print("This will test the new Phase 2 features\n")
    
    # Run tests
    asyncio.run(test_smtp_validation())
    
    # Uncomment to test a specific email in detail
    # asyncio.run(test_single_email_detailed())
