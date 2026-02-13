import dns.resolver
from typing import List, Dict


def check_mx_records(domain: str) -> Dict:
    """
    Check if domain has valid MX records.
    
    Returns:
        dict: {
            'has_mx': bool,
            'mx_records': List[str],
            'error': str or None
        }
    """
    result = {
        'has_mx': False,
        'mx_records': [],
        'error': None
    }
    
    try:
        # Query MX records
        mx_records = dns.resolver.resolve(domain, 'MX')
        
        if mx_records:
            result['has_mx'] = True
            # Sort by preference (lower is higher priority)
            sorted_mx = sorted(mx_records, key=lambda x: x.preference)
            result['mx_records'] = [str(mx.exchange).rstrip('.') for mx in sorted_mx]
    
    except dns.resolver.NXDOMAIN:
        result['error'] = "Domain does not exist"
    except dns.resolver.NoAnswer:
        result['error'] = "No MX records found"
    except dns.resolver.Timeout:
        result['error'] = "DNS query timeout"
    except Exception as e:
        result['error'] = f"DNS error: {str(e)}"
    
    return result
