"""
Authentication and API key management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import api_key_manager
from app.models.database import User, ApiKey
from app.middleware.auth import get_current_user, get_current_api_key
from app.services.rate_limiter import rate_limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Pydantic models for requests/responses
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    plan: str = Field(default="free", pattern="^(free|basic|pro)$")


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    plan: str
    monthly_quota: int
    validations_used: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    name: str = Field(default="Default Key", max_length=100)
    expires_days: Optional[int] = Field(default=None, ge=1, le=365)


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key: str  # Only shown on creation
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    total_requests: int
    
    class Config:
        from_attributes = True


class ApiKeyListResponse(BaseModel):
    id: int
    name: str
    key_preview: str  # Partial key for security
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    total_requests: int


class QuotaResponse(BaseModel):
    user_id: int
    plan: str
    quota_limit: int
    quota_used: int
    quota_remaining: int
    percentage_used: float
    reset_at: Optional[str]


# ==================== USER ENDPOINTS ====================

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario
    
    Para desarrollo/testing. En producción, esto estaría protegido
    o se haría mediante un flujo de registro más complejo.
    """
    # Verificar si el email ya existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verificar si el username ya existe
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Crear usuario
    user = User(
        email=user_data.email,
        username=user_data.username,
        plan=user_data.plan,
        monthly_quota=rate_limiter.PLAN_LIMITS.get(user_data.plan, 100),
        validations_used=0,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """
    Obtener información del usuario actual autenticado
    """
    return user


# ==================== API KEY ENDPOINTS ====================

@router.post("/keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva API key para el usuario actual
    
    **IMPORTANTE:** La key completa solo se muestra una vez.
    Guárdala en un lugar seguro.
    """
    api_key_obj, plain_key = api_key_manager.create_api_key(
        db=db,
        user_id=user.id,
        name=key_data.name,
        expires_days=key_data.expires_days
    )
    
    # Retornar con la key completa (solo esta vez)
    response = ApiKeyResponse.from_orm(api_key_obj)
    response.key = plain_key  # Mostrar key completa
    
    return response


@router.get("/keys", response_model=List[ApiKeyListResponse])
async def list_api_keys(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Listar todas las API keys del usuario actual
    
    Las keys se muestran parcialmente por seguridad (ev_live_xxx...xxx)
    """
    keys = api_key_manager.list_user_keys(db, user.id)
    
    result = []
    for key in keys:
        # Mostrar solo preview de la key
        key_preview = f"{key.key[:15]}...{key.key[-4:]}" if len(key.key) > 20 else key.key
        
        result.append(ApiKeyListResponse(
            id=key.id,
            name=key.name,
            key_preview=key_preview,
            is_active=key.is_active,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
            total_requests=key.total_requests
        ))
    
    return result


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revocar (desactivar) una API key
    
    La key dejará de funcionar inmediatamente.
    """
    # Verificar que la key pertenece al usuario
    key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == user.id
    ).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    success = api_key_manager.revoke_api_key(db, key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke key"
        )
    
    return None


@router.get("/keys/current", response_model=ApiKeyListResponse)
async def get_current_key_info(api_key: ApiKey = Depends(get_current_api_key)):
    """
    Obtener información sobre la API key actual en uso
    """
    key_preview = f"{api_key.key[:15]}...{api_key.key[-4:]}"
    
    return ApiKeyListResponse(
        id=api_key.id,
        name=api_key.name,
        key_preview=key_preview,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        total_requests=api_key.total_requests
    )


# ==================== QUOTA ENDPOINTS ====================

@router.get("/quota", response_model=QuotaResponse)
async def get_quota_info(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener información de cuota y límites del usuario actual
    """
    quota_info = rate_limiter.get_user_quota_info(db, user.id)
    
    if "error" in quota_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=quota_info["error"]
        )
    
    return quota_info


@router.post("/quota/reset", status_code=status.HTTP_200_OK)
async def reset_quota(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resetear manualmente la cuota del usuario
    
    Solo para desarrollo/testing. En producción esto sería
    un endpoint de admin o se haría automáticamente cada mes.
    """
    success = rate_limiter.reset_user_quota(db, user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset quota"
        )
    
    return {"message": "Quota reset successfully"}


@router.get("/usage/stats")
async def get_usage_statistics(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de uso del usuario
    
    Query params:
    - days: Número de días hacia atrás (default: 30)
    """
    stats = rate_limiter.get_usage_stats(db, user.id, days)
    return stats
