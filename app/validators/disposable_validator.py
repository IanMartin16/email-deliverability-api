"""
Disposable/Temporary Email Detector
Uses a curated list of known disposable email providers
"""

# Lista de dominios de email temporales/desechables más comunes
DISPOSABLE_DOMAINS = {
    # Servicios temporales populares
    "tempmail.com", "10minutemail.com", "guerrillamail.com", "mailinator.com",
    "throwaway.email", "temp-mail.org", "fakeinbox.com", "trashmail.com",
    "maildrop.cc", "mintemail.com", "mytemp.email", "sharklasers.com",
    "yopmail.com", "getnada.com", "emailondeck.com", "spamgourmet.com",
    
    # Variantes y servicios adicionales
    "guerrillamailblock.com", "mailnesia.com", "temp-mail.io", "tempail.com",
    "mohmal.com", "emailtemporanea.net", "throwawaymail.com", "dispostable.com",
    "mailcatch.com", "tempr.email", "getairmail.com", "inboxbear.com",
    "tmpmail.net", "tmpmail.org", "emailfake.com", "mailinator2.com",
    
    # Servicios catch-all
    "disposableaddress.com", "spambog.com", "spambox.us", "spamobox.com",
    "spam4.me", "tempinbox.com", "anonymbox.com", "boxformail.in",
    
    # Servicios internacionales
    "correo-temporal.com", "sogetthis.com", "jetable.org", "wegwerfmail.de",
    "trashmail.de", "trashmail.net", "trashemail.de", "discardmail.com",
    
    # Otros servicios conocidos
    "mailexpire.com", "mailforspam.com", "mailfreeonline.com", "mailin8r.com",
    "mailmoat.com", "mailnull.com", "mailtothis.com", "meltmail.com",
    "mintemail.com", "mt2009.com", "mt2014.com", "mytrashmail.com",
    "no-spam.ws", "nospam.ze.tc", "nospamfor.us", "nowmymail.com",
    "objectmail.com", "obobbo.com", "oneoffemail.com", "onewaymail.com",
    "opayq.com", "pookmail.com", "reallymymail.com", "recursor.net",
    "recode.me", "rmqkr.net", "safe-mail.net", "saynotospams.com",
    "selfdestructingmail.com", "sendspamhere.com", "sharklasers.com",
    "shiftmail.com", "slaskpost.se", "slopsbox.com", "smellfear.com",
    "snakemail.com", "sneakemail.com", "sofort-mail.de", "solvemail.info",
    "spam.la", "spamavert.com", "spambox.info", "spamcorptastic.com",
    "spamcowboy.com", "spamcowboy.net", "spamcowboy.org", "spamdecoy.net",
    "spamex.com", "spamfree24.com", "spamfree24.de", "spamfree24.eu",
    "spamfree24.info", "spamfree24.net", "spamfree24.org", "spamgourmet.com",
    "spamgourmet.net", "spamgourmet.org", "spamhole.com", "spamify.com"
}


def is_disposable(domain: str) -> dict:
    """
    Check if email domain is from a disposable/temporary email service.
    
    Args:
        domain: Email domain to check
    
    Returns:
        dict: {
            'is_disposable': bool,
            'provider': str or None,
            'confidence': str
        }
    """
    domain_lower = domain.lower().strip()
    
    result = {
        'is_disposable': False,
        'provider': None,
        'confidence': 'high'
    }
    
    # Direct match
    if domain_lower in DISPOSABLE_DOMAINS:
        result['is_disposable'] = True
        result['provider'] = domain_lower
        return result
    
    # Check for subdomain matches (e.g., user.mailinator.com)
    for disposable_domain in DISPOSABLE_DOMAINS:
        if domain_lower.endswith(f".{disposable_domain}"):
            result['is_disposable'] = True
            result['provider'] = disposable_domain
            return result
    
    # Heuristic checks for suspicious patterns
    suspicious_patterns = [
        "temp", "trash", "spam", "fake", "disposable", "throwaway",
        "guerrilla", "temporary", "mailinator", "yopmail"
    ]
    
    for pattern in suspicious_patterns:
        if pattern in domain_lower:
            result['is_disposable'] = True
            result['provider'] = domain_lower
            result['confidence'] = 'medium'
            return result
    
    return result


def add_custom_disposable_domain(domain: str):
    """
    Add a custom domain to the disposable list (for future extensions)
    """
    DISPOSABLE_DOMAINS.add(domain.lower().strip())


def get_disposable_domains_count() -> int:
    """Return the total number of known disposable domains"""
    return len(DISPOSABLE_DOMAINS)
