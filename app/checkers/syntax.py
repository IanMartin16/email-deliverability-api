"""
Checker de sintaxis. Envuelve la logica existente de validate_syntax()
en EmailValidatorService (email-validator, RFC-compliant).
"""

from email_validator import validate_email, EmailNotValidError

from app.checkers.base import Checker, CheckContext
from app.core.results import CheckResult, CheckStatus


class SyntaxChecker(Checker):
    name = "syntax"
    weight = 20
    cost = "fast"

    async def run(self, ctx: CheckContext) -> CheckResult:
        try:
            validated = validate_email(ctx.email, check_deliverability=False)
            return CheckResult(
                name=self.name,
                status=CheckStatus.PASS,
                weight=self.weight,
                detail={"normalized": validated.normalized},
            )
        except EmailNotValidError as e:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                weight=self.weight,
                note=str(e),
            )
