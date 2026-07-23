"""
Checker de dominios desechables. Envuelve la lista existente de
EmailValidatorService.DISPOSABLE_DOMAINS.

Semantica: PASS = NO es desechable (senal positiva).
           FAIL = es desechable.

Nota futura: cargar/expandir desde la tabla DisposableDomain de la DB.
"""

from app.checkers.base import Checker, CheckContext
from app.core.results import CheckResult, CheckStatus


class DisposableChecker(Checker):
    name = "disposable"
    weight = 20
    cost = "fast"

    # Misma lista curada del validator.py original
    DISPOSABLE_DOMAINS: set[str] = {
        "tempmail.com", "throwaway.email", "guerrillamail.com",
        "10minutemail.com", "mailinator.com", "maildrop.cc",
        "temp-mail.org", "getnada.com", "trashmail.com",
        "yopmail.com", "sharklasers.com", "guerrillamail.info",
        "grr.la", "guerrillamail.biz", "guerrillamail.de",
        "spam4.me", "getairmail.com", "fakeinbox.com",
    }

    async def run(self, ctx: CheckContext) -> CheckResult:
        if ctx.domain in self.DISPOSABLE_DOMAINS:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                weight=self.weight,
                note="Dominio de email temporal/desechable",
            )
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            weight=self.weight,
        )
