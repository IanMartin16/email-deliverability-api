"""
Authentication middleware for API key validation
"""

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import SessionLocal
from app.core.security import api_key_manager
from app.models.database import User, ApiKey


class ApiKeyAuth(HTTPBearer):
    """
    Autenticación mediante API Key en el header
    
    Acepta:
    - Header: Authorization: Bearer ev_live_xxxxx
    - Header: X-API-Key: ev_live_xxxxx
    """
    
    def __init__(self, auto_error: bool = True):
        super(ApiKeyAuth, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[dict]:
        """
        Valida la API key del request
        
        Returns:
            dict con user y api_key si válido, None si inválido
        """
        # Obtener API key del header
        api_key = self._extract_api_key(request)
        
        if not api_key:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key missing. Provide in 'Authorization: Bearer <key>' or 'X-API-Key: <key>' header",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        
        # Validar API key
        db = SessionLocal()
        try:
            is_valid, api_key_obj, user = api_key_manager.validate_api_key(db, api_key)
            
            if not is_valid:
                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired API key",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return None
            
            # Hacer refresh de los objetos antes de cerrar la sesión
            # Esto carga todos los atributos en memoria
            db.refresh(user)
            db.refresh(api_key_obj)
            
            # Expunge los objetos de la sesión para que puedan usarse fuera
            db.expunge(user)
            db.expunge(api_key_obj)
            
            # Retornar información del usuario autenticado
            return {
                "user": user,
                "api_key": api_key_obj,
                "key_string": api_key
            }
            
        finally:
            db.close()
    
    def _extract_api_key(self, request: Request) -> Optional[str]:
        """
        Extrae la API key del request
        
        Busca en:
        1. Header Authorization: Bearer <key>
        2. Header X-API-Key: <key>
        3. Query param ?api_key=<key> (menos seguro, pero útil para testing)
        """
        # Opción 1: Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "")
        
        # Opción 2: X-API-Key header (más común en APIs)
        x_api_key = request.headers.get("X-API-Key")
        if x_api_key:
            return x_api_key
        
        # Opción 3: Query parameter (solo para testing/desarrollo)
        api_key_param = request.query_params.get("api_key")
        if api_key_param:
            return api_key_param
        
        return None


class OptionalApiKeyAuth(ApiKeyAuth):
    """
    Autenticación opcional - no arroja error si falta API key
    
    Útil para endpoints que pueden funcionar con o sin autenticación
    """
    
    def __init__(self):
        super(OptionalApiKeyAuth, self).__init__(auto_error=False)


# Instancias para usar en los endpoints
require_api_key = ApiKeyAuth(auto_error=True)
optional_api_key = OptionalApiKeyAuth()


async def get_current_user(auth: dict = Depends(require_api_key)) -> User:
    """
    Dependency para obtener el usuario actual autenticado
    
    Usage:
        @router.get("/me")
        async def get_me(user: User = Depends(get_current_user)):
            return {"email": user.email}
    """
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return auth["user"]


async def get_current_api_key(auth: dict = Depends(require_api_key)) -> ApiKey:
    """
    Dependency para obtener la API key actual
    
    Usage:
        @router.get("/key-info")
        async def key_info(api_key: ApiKey = Depends(get_current_api_key)):
            return {"key_name": api_key.name}
    """
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return auth["api_key"]
