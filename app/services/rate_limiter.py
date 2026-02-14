"""
Rate limiting service for quota management
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import User, ValidationLog
from app.core.config import settings
from typing import Tuple


class RateLimiter:
    """
    Gestiona rate limiting y cuotas por plan
    """
    
    # Límites por plan (validaciones por mes)
    PLAN_LIMITS = {
        "free": settings.RATE_LIMIT_FREE,      # 100
        "basic": settings.RATE_LIMIT_BASIC,    # 5,000
        "pro": settings.RATE_LIMIT_PRO,        # 50,000
    }
    
    @staticmethod
    def get_user_quota_info(db: Session, user_id: int) -> dict:
        """
        Obtiene información de cuota del usuario
        
        Args:
            db: Database session
            user_id: ID del usuario
            
        Returns:
            dict con información de cuota
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {
                "error": "User not found"
            }
        
        # Calcular inicio del periodo actual
        now = datetime.utcnow()
        
        # Si es el primer día del mes o no hay reset date, establecer inicio de mes
        if not user.quota_reset_at or user.quota_reset_at <= now:
            # Calcular próximo reset (primer día del siguiente mes)
            if now.month == 12:
                next_reset = datetime(now.year + 1, 1, 1)
            else:
                next_reset = datetime(now.year, now.month + 1, 1)
            
            # Reset de contador si es nuevo periodo
            if not user.quota_reset_at or user.quota_reset_at <= now:
                user.validations_used = 0
                user.quota_reset_at = next_reset
                db.commit()
        
        # Obtener límite del plan
        plan_limit = RateLimiter.PLAN_LIMITS.get(user.plan, 100)
        
        # Calcular uso
        remaining = max(0, plan_limit - user.validations_used)
        percentage_used = (user.validations_used / plan_limit * 100) if plan_limit > 0 else 0
        
        return {
            "user_id": user.id,
            "plan": user.plan,
            "quota_limit": plan_limit,
            "quota_used": user.validations_used,
            "quota_remaining": remaining,
            "percentage_used": round(percentage_used, 2),
            "reset_at": user.quota_reset_at.isoformat() if user.quota_reset_at else None
        }
    
    @staticmethod
    def check_rate_limit(db: Session, user_id: int) -> Tuple[bool, dict]:
        """
        Verifica si el usuario puede hacer otra validación
        
        Args:
            db: Database session
            user_id: ID del usuario
            
        Returns:
            (can_proceed: bool, quota_info: dict)
        """
        quota_info = RateLimiter.get_user_quota_info(db, user_id)
        
        if "error" in quota_info:
            return False, quota_info
        
        # Verificar si tiene cuota disponible
        can_proceed = quota_info["quota_remaining"] > 0
        
        return can_proceed, quota_info
    
    @staticmethod
    def increment_usage(db: Session, user_id: int, count: int = 1) -> bool:
        """
        Incrementa el contador de uso del usuario
        
        Args:
            db: Database session
            user_id: ID del usuario
            count: Cantidad a incrementar (para bulk operations)
            
        Returns:
            True si se incrementó exitosamente
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        user.validations_used += count
        db.commit()
        
        return True
    
    @staticmethod
    def reset_user_quota(db: Session, user_id: int) -> bool:
        """
        Resetea manualmente la cuota de un usuario
        
        Útil para testing o ajustes administrativos
        
        Args:
            db: Database session
            user_id: ID del usuario
            
        Returns:
            True si se reseteó exitosamente
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        user.validations_used = 0
        
        # Establecer próximo reset
        now = datetime.utcnow()
        if now.month == 12:
            next_reset = datetime(now.year + 1, 1, 1)
        else:
            next_reset = datetime(now.year, now.month + 1, 1)
        
        user.quota_reset_at = next_reset
        db.commit()
        
        return True
    
    @staticmethod
    def upgrade_user_plan(db: Session, user_id: int, new_plan: str) -> bool:
        """
        Cambia el plan de un usuario
        
        Args:
            db: Database session
            user_id: ID del usuario
            new_plan: Nuevo plan (free, basic, pro)
            
        Returns:
            True si se actualizó exitosamente
        """
        if new_plan not in RateLimiter.PLAN_LIMITS:
            return False
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        old_plan = user.plan
        user.plan = new_plan
        user.monthly_quota = RateLimiter.PLAN_LIMITS[new_plan]
        
        # Si es upgrade, no resetear contador (mantener validaciones del mes)
        # Si es downgrade y excede el nuevo límite, ajustar
        if user.validations_used > user.monthly_quota:
            user.validations_used = user.monthly_quota
        
        db.commit()
        
        return True
    
    @staticmethod
    def get_usage_stats(db: Session, user_id: int, days: int = 30) -> dict:
        """
        Obtiene estadísticas de uso del usuario
        
        Args:
            db: Database session
            user_id: ID del usuario
            days: Días hacia atrás para analizar
            
        Returns:
            dict con estadísticas
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        logs = db.query(ValidationLog).filter(
            ValidationLog.user_id == user_id,
            ValidationLog.created_at >= start_date
        ).all()
        
        if not logs:
            return {
                "period_days": days,
                "total_validations": 0,
                "valid_emails": 0,
                "invalid_emails": 0,
                "avg_score": 0.0
            }
        
        total = len(logs)
        valid = sum(1 for log in logs if log.is_valid)
        avg_score = sum(log.deliverability_score for log in logs) / total
        
        return {
            "period_days": days,
            "total_validations": total,
            "valid_emails": valid,
            "invalid_emails": total - valid,
            "avg_score": round(avg_score, 2),
            "smtp_checks": sum(1 for log in logs if log.smtp_check_performed)
        }


# Singleton instance
rate_limiter = RateLimiter()
