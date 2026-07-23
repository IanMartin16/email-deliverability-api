"""
Checker de cuentas de rol (nuevo).

Detecta buzones genericos (admin@, info@, no-reply@...) que suelen tener
peor entregabilidad en campanas: no son personas y muchos ESP los penalizan.

Semantica: PASS = parece cuenta personal (senal positiva, aporta peso).
           FAIL no se usa aqui -> una cuenta de rol es senal debil, no invalida.
           Se reporta como PASS con detail o INCONCLUSIVE segun severidad? No:
           se usa PASS/FAIL con peso bajo para mantener el modelo simple:
             - no-rol  -> PASS (suma weight)
             - rol     -> FAIL (no suma; nota explicativa; el verdict no se
                          vuelve REJECT porque "role_account" no es critico)
"""

from app.checkers.base import Checker, CheckContext
from app.core.results import CheckResult, CheckStatus


class RoleAccountChecker(Checker):
    name = "role_account"
    weight = 10
    cost = "fast"

    ROLE_LOCALPARTS: set[str] = {
        "admin", "administrator", "info", "contact", "contacto",
        "support", "soporte", "help", "sales", "ventas",
        "noreply", "no-reply", "no_reply", "donotreply",
        "postmaster", "webmaster", "hostmaster", "abuse",
        "billing", "marketing", "office", "hr", "jobs", "careers",
        "hello", "hola", "team", "mail", "email", "newsletter",
    }

    async def run(self, ctx: CheckContext) -> CheckResult:
        local = ctx.email.split("@")[0].lower()
        if local in self.ROLE_LOCALPARTS:
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                weight=self.weight,
                note="Cuenta de rol/generica: entregabilidad reducida en campanas",
            )
        return CheckResult(
            name=self.name,
            status=CheckStatus.PASS,
            weight=self.weight,
        )
