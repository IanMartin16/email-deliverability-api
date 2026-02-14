import re
import dns.resolver
import asyncio
from typing import Optional, List
from email_validator import validate_email, EmailNotValidError
from app.models.schemas import MXRecord
from app.core.config import settings
from app.services.smtp_validator import smtp_validator


class EmailValidatorService:
    """
    Core email validation service with multiple validation strategies
    """
    
    # Common disposable email domains (subset - will expand)
    DISPOSABLE_DOMAINS = {
        "tempmail.com", "throwaway.email", "guerrillamail.com",
        "10minutemail.com", "mailinator.com", "maildrop.cc",
        "temp-mail.org", "getnada.com", "trashmail.com",
        "yopmail.com", "sharklasers.com", "guerrillamail.info",
        "grr.la", "guerrillamail.biz", "guerrillamail.de",
        "spam4.me", "getairmail.com", "fakeinbox.com"
    }
    
    def __init__(self):
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 5
    
    def validate_syntax(self, email: str) -> tuple[bool, Optional[str]]:
        """
        Validate email syntax using email-validator library
        
        Returns:
            (is_valid, normalized_email or None)
        """
        try:
            validated = validate_email(email, check_deliverability=False)
            return True, validated.normalized
        except EmailNotValidError as e:
            return False, None
    
    def extract_domain(self, email: str) -> Optional[str]:
        """Extract domain from email address"""
        try:
            return email.split('@')[1].lower()
        except (IndexError, AttributeError):
            return None
    
    def is_disposable_email(self, email: str) -> bool:
        """
        Check if email is from a disposable/temporary email provider
        """
        domain = self.extract_domain(email)
        if not domain:
            return False
        
        return domain in self.DISPOSABLE_DOMAINS
    
    async def check_mx_records(self, domain: str) -> tuple[bool, List[MXRecord]]:
        """
        Check if domain has valid MX records
        
        Returns:
            (has_mx, list of MX records)
        """
        mx_records = []
        
        try:
            # Run DNS query in executor to avoid blocking
            loop = asyncio.get_event_loop()
            answers = await loop.run_in_executor(
                None,
                lambda: self.dns_resolver.resolve(domain, 'MX')
            )
            
            for rdata in answers:
                mx_records.append(
                    MXRecord(
                        host=str(rdata.exchange).rstrip('.'),
                        priority=rdata.preference
                    )
                )
            
            # Sort by priority (lower is higher priority)
            mx_records.sort(key=lambda x: x.priority)
            
            return len(mx_records) > 0, mx_records
            
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return False, []
        except Exception as e:
            print(f"MX lookup error for {domain}: {e}")
            return False, []
    
    def calculate_deliverability_score(
        self,
        syntax_valid: bool,
        has_mx: bool,
        is_disposable: bool,
        mailbox_exists: Optional[bool]
    ) -> float:
        """
        Calculate overall deliverability score (0-100)
        
        Scoring breakdown:
        - Syntax valid: 20 points
        - Has MX records: 30 points
        - Not disposable: 20 points
        - Mailbox exists: 30 points
        """
        score = 0.0
        
        if syntax_valid:
            score += 20
        
        if has_mx:
            score += 30
        
        if not is_disposable:
            score += 20
        
        if mailbox_exists is True:
            score += 30
        elif mailbox_exists is None:
            # SMTP check not performed, give partial credit
            score += 15
        
        return round(score, 2)
    
    async def validate_email(
        self,
        email: str,
        check_smtp: bool = True
    ) -> dict:
        """
        Perform comprehensive email validation
        
        Args:
            email: Email address to validate
            check_smtp: Whether to perform SMTP verification
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "email": email,
            "syntax_valid": False,
            "domain": None,
            "has_mx_records": False,
            "mx_records": None,
            "is_disposable": False,
            "smtp_check_performed": False,
            "mailbox_exists": None,
            "smtp_response": None,
        }
        
        # Step 1: Syntax validation
        syntax_valid, normalized_email = self.validate_syntax(email)
        result["syntax_valid"] = syntax_valid
        
        if not syntax_valid:
            result["deliverability_score"] = 0.0
            result["is_valid"] = False
            return result
        
        # Use normalized email for further checks
        email = normalized_email
        result["email"] = email
        
        # Step 2: Extract domain
        domain = self.extract_domain(email)
        result["domain"] = domain
        
        if not domain:
            result["deliverability_score"] = 0.0
            result["is_valid"] = False
            return result
        
        # Step 3: Check if disposable
        result["is_disposable"] = self.is_disposable_email(email)
        
        # Step 4: Check MX records
        has_mx, mx_records = await self.check_mx_records(domain)
        result["has_mx_records"] = has_mx
        result["mx_records"] = mx_records
        
        # Step 5: SMTP verification (if requested and MX records exist)
        if check_smtp and has_mx and mx_records:
            try:
                result["smtp_check_performed"] = True
                
                # Verificar con fallback a múltiples MX servers
                mailbox_exists, smtp_response, is_catch_all = await smtp_validator.verify_with_fallback(
                    email, 
                    mx_records
                )
                
                result["mailbox_exists"] = mailbox_exists
                result["smtp_response"] = smtp_response
                result["is_catch_all"] = is_catch_all
                
                # Si es catch-all, reducir confianza
                if is_catch_all:
                    result["smtp_response"] += " (Warning: Catch-all domain detected)"
                    
            except Exception as e:
                result["smtp_check_performed"] = False
                result["mailbox_exists"] = None
                result["smtp_response"] = f"SMTP check failed: {str(e)}"
        
        # Calculate final score
        result["deliverability_score"] = self.calculate_deliverability_score(
            syntax_valid=result["syntax_valid"],
            has_mx=result["has_mx_records"],
            is_disposable=result["is_disposable"],
            mailbox_exists=result["mailbox_exists"]
        )
        
        # Overall validity
        result["is_valid"] = (
            result["syntax_valid"] and
            result["has_mx_records"] and
            not result["is_disposable"]
        )
        
        return result


# Singleton instance
email_validator = EmailValidatorService()
