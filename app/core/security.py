"""
Security utilities for API key generation and validation
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.database import ApiKey, User


class SecurityManager:
    """
    Maneja la generación y validación de API keys
    """
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Genera una API key segura
        
        Formato: ev_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (32 chars random)
        Prefijo 'ev' = Email Validator
        """
        random_part = secrets.token_urlsafe(24)  # 32 caracteres base64
        return f"ev_live_{random_part}"
    
    @staticmethod
    def generate_test_api_key() -> str:
        """
        Genera una API key de testing
        
        Formato: ev_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        """
        random_part = secrets.token_urlsafe(24)
        return f"ev_test_{random_part}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash de API key para almacenamiento seguro
        
        Nota: Por simplicidad, guardamos la key en texto plano
        En producción seria, hashearla con bcrypt o argon2
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """
        Valida el formato de la API key
        
        Debe empezar con ev_live_ o ev_test_ y tener longitud apropiada
        """
        if not api_key:
            return False
        
        if api_key.startswith("ev_live_") or api_key.startswith("ev_test_"):
            # Verificar longitud mínima
            return len(api_key) >= 40
        
        return False
    
    @staticmethod
    def is_test_key(api_key: str) -> bool:
        """
        Determina si es una key de testing
        """
        return api_key.startswith("ev_test_")


class ApiKeyManager:
    """
    Gestión de API keys en la base de datos
    """
    
    @staticmethod
    def create_api_key(
        db: Session,
        user_id: int,
        name: str = "Default Key",
        expires_days: Optional[int] = None
    ) -> Tuple[ApiKey, str]:
        """
        Crea una nueva API key para un usuario
        
        Args:
            db: Database session
            user_id: ID del usuario
            name: Nombre descriptivo de la key
            expires_days: Días hasta expiración (None = nunca)
            
        Returns:
            (ApiKey object, plain_text_key)
        """
        # Generar key
        plain_key = SecurityManager.generate_api_key()
        
        # Calcular expiración
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        # Crear registro
        api_key = ApiKey(
            key=plain_key,  # En producción, guardar hasheada
            name=name,
            user_id=user_id,
            is_active=True,
            expires_at=expires_at
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        return api_key, plain_key
    
    @staticmethod
    def get_api_key(db: Session, key: str) -> Optional[ApiKey]:
        """
        Obtiene una API key de la base de datos
        
        Args:
            db: Database session
            key: API key (plain text)
            
        Returns:
            ApiKey object o None
        """
        return db.query(ApiKey).filter(
            ApiKey.key == key,
            ApiKey.is_active == True
        ).first()
    
    @staticmethod
    def validate_api_key(db: Session, key: str) -> Tuple[bool, Optional[ApiKey], Optional[User]]:
        """
        Valida una API key completa
        
        Args:
            db: Database session
            key: API key a validar
            
        Returns:
            (is_valid, api_key_object, user_object)
        """
        # Validar formato
        if not SecurityManager.validate_api_key_format(key):
            return False, None, None
        
        # Buscar en DB
        api_key = ApiKeyManager.get_api_key(db, key)
        
        if not api_key:
            return False, None, None
        
        # Verificar expiración
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return False, api_key, None
        
        # Obtener usuario
        user = db.query(User).filter(User.id == api_key.user_id).first()
        
        if not user or not user.is_active:
            return False, api_key, None
        
        # Actualizar último uso
        api_key.last_used_at = datetime.utcnow()
        api_key.total_requests += 1
        db.commit()
        
        return True, api_key, user
    
    @staticmethod
    def revoke_api_key(db: Session, key_id: int) -> bool:
        """
        Revoca (desactiva) una API key
        
        Args:
            db: Database session
            key_id: ID de la key
            
        Returns:
            True si se revocó, False si no existe
        """
        api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
        
        if not api_key:
            return False
        
        api_key.is_active = False
        db.commit()
        
        return True
    
    @staticmethod
    def list_user_keys(db: Session, user_id: int) -> list[ApiKey]:
        """
        Lista todas las API keys de un usuario
        
        Args:
            db: Database session
            user_id: ID del usuario
            
        Returns:
            Lista de ApiKey objects
        """
        return db.query(ApiKey).filter(
            ApiKey.user_id == user_id
        ).order_by(ApiKey.created_at.desc()).all()


# Singleton instances
security_manager = SecurityManager()
api_key_manager = ApiKeyManager()
