"""
Modelo de resultado normalizado.

Un solo esquema interno que sirve para validacion sincrona, async y bulk.
La distincion INCONCLUSIVE vs SKIPPED vs FAIL es lo que arregla el score
injusto de Outlook: un timeout ya no cuenta como "mailbox no existe".
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class CheckStatus(str, Enum):
    PASS = "pass"                  # senal positiva confirmada
    FAIL = "fail"                  # senal negativa confirmada
    INCONCLUSIVE = "inconclusive"  # se intento, sin respuesta clara (ej. SMTP timeout)
    SKIPPED = "skipped"            # no se ejecuto por politica (proveedor bloqueador, modo quick)


@dataclass
class CheckResult:
    name: str                      # "syntax", "mx", "smtp", ...
    status: CheckStatus
    weight: float                  # aporte al score si PASS
    detail: dict[str, Any] = field(default_factory=dict)  # mx_records, smtp_response...
    note: Optional[str] = None     # mensaje legible para el usuario


@dataclass
class EmailAssessment:
    email: str
    domain: Optional[str] = None
    checks: list[CheckResult] = field(default_factory=list)
    confidence_score: float = 0.0
    verdict: str = "UNKNOWN"       # ACCEPT / REJECT / RISKY / UNKNOWN
    processing_time_ms: float = 0.0

    def get(self, name: str) -> Optional[CheckResult]:
        """Busca un CheckResult por nombre. None si no corrio."""
        return next((c for c in self.checks if c.name == name), None)
