"""
Checker de registros MX. Envuelve la logica existente de check_mx_records()
en EmailValidatorService (dnspython en executor para no bloquear).
"""

import asyncio

import dns.resolver

from app.checkers.base import Checker, CheckContext
from app.core.results import CheckResult, CheckStatus
from app.models.schemas import MXRecord


class MXChecker(Checker):
    name = "mx"
    weight = 30
    cost = "fast"

    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5
        self.resolver.lifetime = 5

    async def run(self, ctx: CheckContext) -> CheckResult:
        try:
            loop = asyncio.get_event_loop()
            answers = await loop.run_in_executor(
                None,
                lambda: self.resolver.resolve(ctx.domain, "MX"),
            )
            records = sorted(
                (
                    MXRecord(
                        host=str(r.exchange).rstrip("."),
                        priority=r.preference,
                    )
                    for r in answers
                ),
                key=lambda x: x.priority,
            )
            if records:
                # Compartir para que el checker SMTP no repita la consulta
                ctx.shared["mx_records"] = records
                return CheckResult(
                    name=self.name,
                    status=CheckStatus.PASS,
                    weight=self.weight,
                    detail={"records": records},
                )
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                weight=self.weight,
                note="El dominio no tiene registros MX",
            )
        except (
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
        ):
            return CheckResult(
                name=self.name,
                status=CheckStatus.FAIL,
                weight=self.weight,
                note="Dominio inexistente o sin servidores de correo",
            )
        except Exception as e:
            # Error de red/DNS transitorio: no castigar como FAIL definitivo
            return CheckResult(
                name=self.name,
                status=CheckStatus.INCONCLUSIVE,
                weight=self.weight,
                note=f"Consulta MX fallo: {e}",
            )
