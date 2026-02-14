"""
Service for logging email validations to database
"""

from sqlalchemy.orm import Session
from app.models.database import ValidationLog, UsageStats
from datetime import datetime
from typing import Optional


class ValidationLogger:
    """
    Maneja el logging de validaciones en la base de datos
    """
    
    @staticmethod
    def log_validation(
        db: Session,
        email: str,
        validation_result: dict,
        processing_time_ms: float,
        user_id: Optional[int] = None,
        api_key_id: Optional[int] = None
    ) -> ValidationLog:
        """
        Guarda un registro de validación en la base de datos
        
        Args:
            db: Database session
            email: Email validado
            validation_result: Resultado de la validación
            processing_time_ms: Tiempo de procesamiento en ms
            user_id: ID del usuario (opcional)
            api_key_id: ID de la API key (opcional)
            
        Returns:
            ValidationLog object
        """
        log_entry = ValidationLog(
            email=email,
            domain=validation_result.get("domain"),
            is_valid=validation_result.get("is_valid", False),
            syntax_valid=validation_result.get("syntax_valid", False),
            has_mx_records=validation_result.get("has_mx_records", False),
            is_disposable=validation_result.get("is_disposable", False),
            smtp_check_performed=validation_result.get("smtp_check_performed", False),
            mailbox_exists=validation_result.get("mailbox_exists"),
            smtp_response=validation_result.get("smtp_response"),
            is_catch_all=validation_result.get("is_catch_all"),
            deliverability_score=validation_result.get("deliverability_score", 0.0),
            processing_time_ms=processing_time_ms,
            user_id=user_id,
            api_key_id=api_key_id
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        return log_entry
    
    @staticmethod
    def get_user_validation_count(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None
    ) -> int:
        """
        Obtiene el número de validaciones de un usuario
        
        Args:
            db: Database session
            user_id: ID del usuario
            start_date: Fecha de inicio (opcional)
            
        Returns:
            Número de validaciones
        """
        query = db.query(ValidationLog).filter(ValidationLog.user_id == user_id)
        
        if start_date:
            query = query.filter(ValidationLog.created_at >= start_date)
        
        return query.count()
    
    @staticmethod
    def get_stats_by_user(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Obtiene estadísticas de validación para un usuario
        
        Args:
            db: Database session
            user_id: ID del usuario
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            Diccionario con estadísticas
        """
        query = db.query(ValidationLog).filter(ValidationLog.user_id == user_id)
        
        if start_date:
            query = query.filter(ValidationLog.created_at >= start_date)
        if end_date:
            query = query.filter(ValidationLog.created_at <= end_date)
        
        logs = query.all()
        
        if not logs:
            return {
                "total_validations": 0,
                "valid_count": 0,
                "invalid_count": 0,
                "disposable_count": 0,
                "smtp_checks": 0,
                "avg_score": 0.0,
                "avg_processing_time_ms": 0.0
            }
        
        total = len(logs)
        valid_count = sum(1 for log in logs if log.is_valid)
        disposable_count = sum(1 for log in logs if log.is_disposable)
        smtp_checks = sum(1 for log in logs if log.smtp_check_performed)
        
        avg_score = sum(log.deliverability_score for log in logs) / total
        avg_time = sum(log.processing_time_ms for log in logs if log.processing_time_ms) / total
        
        return {
            "total_validations": total,
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "disposable_count": disposable_count,
            "smtp_checks": smtp_checks,
            "avg_score": round(avg_score, 2),
            "avg_processing_time_ms": round(avg_time, 2)
        }


# Singleton instance
validation_logger = ValidationLogger()
