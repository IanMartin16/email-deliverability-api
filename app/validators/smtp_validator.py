import smtplib
import socket
from typing import Dict


def verify_smtp(email: str, mx_host: str, timeout: int = 10) -> Dict:
    """
    Verify if email mailbox exists via SMTP.
    
    This is a best-effort check. Many mail servers don't allow SMTP verification
    to prevent email enumeration attacks.
    
    Args:
        email: Email address to verify
        mx_host: MX server hostname
        timeout: Connection timeout in seconds
    
    Returns:
        dict: {
            'smtp_valid': bool or None,
            'smtp_response': str,
            'smtp_code': int or None,
            'error': str or None
        }
    """
    result = {
        'smtp_valid': None,
        'smtp_response': '',
        'smtp_code': None,
        'error': None
    }
    
    try:
        # Connect to SMTP server
        with smtplib.SMTP(timeout=timeout) as smtp:
            smtp.connect(mx_host)
            
            # HELO command
            smtp.helo('mail.example.com')
            
            # MAIL FROM
            smtp.mail('verify@example.com')
            
            # RCPT TO - this is where we check if mailbox exists
            code, response = smtp.rcpt(email)
            
            result['smtp_code'] = code
            result['smtp_response'] = response.decode() if isinstance(response, bytes) else str(response)
            
            # SMTP codes:
            # 250 = OK, mailbox exists
            # 550 = Mailbox unavailable
            # 551 = User not local
            # 552 = Exceeded storage
            # 553 = Mailbox name not allowed
            # 450-451 = Temporary failure
            
            if code == 250:
                result['smtp_valid'] = True
            elif code in [550, 551, 553]:
                result['smtp_valid'] = False
            else:
                # Uncertain - server doesn't allow verification
                result['smtp_valid'] = None
                result['error'] = f"Server response unclear (code {code})"
    
    except smtplib.SMTPServerDisconnected:
        result['error'] = "SMTP server disconnected"
    except smtplib.SMTPResponseException as e:
        result['smtp_code'] = e.smtp_code
        result['smtp_response'] = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
        result['error'] = f"SMTP error: {e.smtp_code}"
    except socket.timeout:
        result['error'] = "Connection timeout"
    except socket.gaierror:
        result['error'] = "Could not resolve MX hostname"
    except ConnectionRefusedError:
        result['error'] = "Connection refused by mail server"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    
    return result


def batch_verify_smtp(emails: list, mx_host: str, timeout: int = 10) -> Dict[str, Dict]:
    """
    Verify multiple emails against the same MX server.
    More efficient for bulk checking.
    """
    results = {}
    
    try:
        with smtplib.SMTP(timeout=timeout) as smtp:
            smtp.connect(mx_host)
            smtp.helo('mail.example.com')
            smtp.mail('verify@example.com')
            
            for email in emails:
                try:
                    code, response = smtp.rcpt(email)
                    results[email] = {
                        'smtp_valid': code == 250,
                        'smtp_code': code,
                        'smtp_response': response.decode() if isinstance(response, bytes) else str(response)
                    }
                except Exception as e:
                    results[email] = {
                        'smtp_valid': None,
                        'error': str(e)
                    }
    
    except Exception as e:
        # If connection fails, mark all as uncertain
        for email in emails:
            results[email] = {
                'smtp_valid': None,
                'error': f"Connection error: {str(e)}"
            }
    
    return results
