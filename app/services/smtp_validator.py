"""
SMTP Validator Service

Verifica la existencia de buzones de correo usando el protocolo SMTP.
Implementa verificación RCPT TO sin enviar emails reales.
"""

import smtplib
import socket
import asyncio
from typing import Tuple, Optional
from app.core.config import settings


class SMTPValidator:
    """
    Validador SMTP para verificar existencia de buzones de correo
    """
    
    def __init__(self):
        self.timeout = settings.SMTP_TIMEOUT
        self.from_email = settings.SMTP_FROM_EMAIL
    
    async def verify_mailbox(
        self, 
        email: str, 
        mx_host: str
    ) -> Tuple[Optional[bool], str, bool]:
        """
        Verifica si un mailbox existe usando SMTP RCPT TO
        
        Args:
            email: Email address to verify
            mx_host: MX server hostname
            
        Returns:
            Tuple of (exists: bool, response: str, is_catch_all: bool)
        """
        try:
            # Ejecutar verificación SMTP en executor para evitar bloquear
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._smtp_verify_sync, 
                email, 
                mx_host
            )
            return result
            
        except Exception as e:
            return False, f"Error: {str(e)}", False
    
    def _smtp_verify_sync(
        self, 
        email: str, 
        mx_host: str
    ) -> Tuple[Optional[bool], str, bool]:
        """
        Verificación SMTP síncrona (se ejecuta en thread pool)
        
        Proceso:
        1. Conectar al servidor MX
        2. HELO/EHLO
        3. MAIL FROM
        4. RCPT TO (aquí se verifica el mailbox)
        5. Analizar respuesta
        """
        smtp = None
        
        try:
            # Conectar al servidor MX en el puerto 25
            smtp = smtplib.SMTP(timeout=self.timeout)
            smtp.set_debuglevel(0)  # 0 = sin debug, 1 = con debug
            
            # Conectar
            code, message = smtp.connect(mx_host, 25)
            
            if code != 220:
                return False, f"Connection failed: {code} {message.decode()}", False
            
            # HELO/EHLO
            smtp.helo(self._get_local_hostname())
            
            # MAIL FROM (usar un email genérico)
            code, message = smtp.mail(self.from_email)
            
            if code not in (250, 251):
                return False, f"MAIL FROM rejected: {code}", False
            
            # RCPT TO - Este es el comando crítico
            code, message = smtp.rcpt(email)
            response_text = message.decode() if isinstance(message, bytes) else str(message)
            
            # Analizar respuesta
            exists = self._analyze_smtp_response(code, response_text)
            
            # Detectar catch-all (algunos servidores aceptan TODO)
            is_catch_all = self._is_catch_all_domain(smtp, email)
            
            # QUIT
            smtp.quit()
            
            return exists, f"{code} {response_text}", is_catch_all
            
        except smtplib.SMTPServerDisconnected:
            return None, "SMTP verification inconclusive: mail server closed the connection unexpectedly", False

        except smtplib.SMTPConnectError:
            return None, "SMTP verification inconclusive: could not establish connection to the mail server", False

        except socket.timeout:
            return None, "SMTP verification inconclusive: mail server did not respond before timeout", False

        except socket.gaierror:
            return None, "SMTP verification inconclusive: MX host could not be resolved", False

        except OSError as e:
            if "Network is unreachable" in str(e):
                return None, "SMTP verification inconclusive: network access to the mail server is unavailable", False
            return None, "SMTP verification inconclusive: network-related error during mailbox verification", False

        except Exception:
            return None, "SMTP verification inconclusive: temporary technical error during mailbox verification", False
            
        finally:
            if smtp:
                try:
                    smtp.quit()
                except:
                    pass
    
    def _analyze_smtp_response(self, code: int, message: str) -> bool:
        """
        Analiza el código de respuesta SMTP
        
        Códigos comunes:
        - 250: Mailbox existe y es accesible
        - 251: Usuario no local, será reenviado
        - 450-451: Buzón temporal no disponible (cuenta como existe)
        - 550: Mailbox no existe
        - 551: Usuario no local
        - 552: Buzón lleno (cuenta como existe)
        - 553: Mailbox name not allowed
        """
        # Códigos que indican que el mailbox existe
        exists_codes = {250, 251, 450, 451, 452}
        
        # Códigos que indican que NO existe
        not_exists_codes = {550, 551, 553}
        
        # Palabras clave en el mensaje que indican no existencia
        not_exists_keywords = [
            'does not exist',
            'not found',
            'no such user',
            'unknown user',
            'invalid recipient',
            'recipient rejected',
            'user unknown',
            'mailbox not found',
            'mailbox unavailable'
        ]
        
        if code in exists_codes:
            return True
        
        if code in not_exists_codes:
            return False
        
        # Analizar el mensaje para palabras clave
        message_lower = message.lower()
        for keyword in not_exists_keywords:
            if keyword in message_lower:
                return False
        
        # Por defecto, si el código es 2xx consideramos que existe
        return 200 <= code < 300
    
    def _is_catch_all_domain(self, smtp: smtplib.SMTP, email: str) -> bool:
        """
        Detecta si el dominio acepta todos los emails (catch-all)
        
        Prueba con un email aleatorio. Si lo acepta, probablemente es catch-all.
        """
        try:
            domain = email.split('@')[1]
            # Usar un email obviamente inválido
            test_email = f"nonexistent-test-12345@{domain}"
            
            code, message = smtp.rcpt(test_email)
            
            # Si acepta este email obviamente falso, es catch-all
            if code in (250, 251):
                return True
            
            return False
            
        except Exception:
            # Si hay error, asumir que no es catch-all
            return False
    
    def _get_local_hostname(self) -> str:
        """
        Obtiene el hostname local para el comando HELO
        """
        try:
            return socket.getfqdn()
        except:
            return "localhost"
    
    async def verify_with_fallback(
        self,
        email: str,
        mx_records: list
    ) -> Tuple[Optional[bool], str, bool]:
        if not mx_records:
            return None, "SMTP verification skipped: no MX records found", False

        last_result = (None, "SMTP verification inconclusive: no reacheable mail server responded", False)

        for mx_record in mx_records[:3]:
            if not getattr(mx_record, "host", None):
                continue

            exists, response, is_catch_all = await self.verify_mailbox(
                email,
                mx_record.host
            )

            last_result = (exists, response, is_catch_all)

            response_lower = response.lower()

            non_conclusive_markers = [
                "timeout",
                "error",
                "could not resolve",
                "connection failed",
                "server disconnected",
                "connection error",
            ]

            if exists is True:
                return exists, response, is_catch_all
            
            if exists is False and not any(marker in response_lower for marker in non_conclusive_markers):
                return exists, response, is_catch_all

        return last_result

# Singleton instance
smtp_validator = SMTPValidator()
