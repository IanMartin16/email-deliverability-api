"""
Checker SMTP. Envuelve el smtp_validator existente (app/services/smtp_validator.py)
SIN modificarlo.

El cambio clave vs. el diseno anterior: timeout/error se traduce a INCONCLUSIVE,
no a FAIL. Un servidor que no responde no significa que el buzon no exista.
"""

from app.checkers.base import Checker, CheckContext
from app.core.results import CheckResult, CheckStatus
from app.services.smtp_validator import smtp_validator


class SMTPChecker(Checker):
    name = "smtp"
    weight = 30
    cost = "slow"
    deferrable = True  # candidato natural para el modo async futuro

    async def run(self, ctx: CheckContext) -> CheckResult:
        mx_records = ctx.shared.get("mx_records")
        if not mx_records:
            return CheckResult(
                name=self.name,
                status=CheckStatus.SKIPPED,
                weight=self.weight,
                note="Sin registros MX; no se intento verificacion SMTP",
            )

        exists, response, is_catch_all = await smtp_validator.verify_with_fallback(
            ctx.email, mx_records
        )
        low = (response or "").lower()

        if "timeout" in low or "error" in low or "could not resolve" in low:
            return CheckResult(
                name=self.name,
                status=CheckStatus.INCONCLUSIVE,
                weight=self.weight,
                detail={"smtp_response": response},
                note="El servidor no respondio a tiempo; el email podria ser valido",
            )

        if is_catch_all:
            return CheckResult(
                name=self.name,
                status=CheckStatus.INCONCLUSIVE,
                weight=self.weight,
                detail={"smtp_response": response, "is_catch_all": True},
                note="Dominio catch-all: acepta cualquier direccion, no verificable",
            )

        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS if exists else CheckStatus.FAIL,
            weight=self.weight,
            detail={"smtp_response": response, "is_catch_all": False},
            note=None if exists else "El servidor rechazo explicitamente la direccion",
        )
