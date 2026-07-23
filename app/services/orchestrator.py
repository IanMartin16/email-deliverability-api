"""
Orquestador: reemplaza al EmailValidatorService.validate_email() monolitico.

No sabe COMO se hace un check; solo decide orden, politica, cache y
short-circuits. Incluye to_response() que mapea EmailAssessment al
contrato actual de EmailValidationResponse (RapidAPI intacto) mas los
campos nuevos opcionales (verdict, checks).
"""

import time
from typing import Any, Optional

from app.checkers.base import CheckContext, Checker
from app.checkers.registry import build_checkers
from app.core.policy import Policy, policy
from app.core.results import CheckResult, CheckStatus, EmailAssessment
from app.scoring.scorer import Scorer, scorer
from app.services.cache import DomainCache, domain_cache

# Checks cuyo resultado es por-dominio y por tanto cacheables
CACHEABLE = {"mx", "disposable"}

# Checks rapidos que corren siempre (en este orden)
FAST_CHECKS = ("mx", "disposable", "role_account")


class Orchestrator:
    def __init__(
        self,
        checkers: Optional[dict[str, Checker]] = None,
        score_engine: Optional[Scorer] = None,
        cache: Optional[DomainCache] = None,
        pol: Optional[Policy] = None,
    ):
        self.checkers = checkers or build_checkers()
        self.scorer = score_engine or scorer
        self.cache = cache or domain_cache
        self.policy = pol or policy

    async def assess(self, email: str, mode: str = "standard") -> EmailAssessment:
        start = time.time()
        assessment = EmailAssessment(email=email)

        # ---- 1. Sintaxis (short-circuit si falla) ----
        ctx = CheckContext(email=email, domain="")
        syntax = await self.checkers["syntax"].run(ctx)
        assessment.checks.append(syntax)

        if syntax.status == CheckStatus.FAIL:
            assessment.confidence_score, assessment.verdict = self.scorer.score(
                assessment.checks
            )
            return self._finish(assessment, start)

        # Usar el email normalizado de aqui en adelante
        normalized = syntax.detail.get("normalized")
        if normalized:
            assessment.email = normalized
            email = normalized

        domain = email.split("@")[1].lower()
        assessment.domain = domain
        ctx = CheckContext(email=email, domain=domain)

        # ---- 2. Whitelist / blacklist (short-circuit) ----
        if domain in self.policy.DOMAIN_BLACKLIST:
            assessment.verdict = "REJECT"
            assessment.confidence_score = 0.0
            assessment.checks.append(
                CheckResult(
                    "blacklist", CheckStatus.FAIL, 0,
                    note="Dominio en lista negra",
                )
            )
            return self._finish(assessment, start)

        if domain in self.policy.DOMAIN_WHITELIST:
            assessment.verdict = "ACCEPT"
            assessment.confidence_score = 100.0
            assessment.checks.append(
                CheckResult(
                    "whitelist", CheckStatus.PASS, 0,
                    note="Dominio en lista blanca",
                )
            )
            return self._finish(assessment, start)

        # ---- 3. Checks rapidos (con cache por dominio) ----
        for name in FAST_CHECKS:
            result = await self._run_cached(name, ctx)
            assessment.checks.append(result)
            # Propagar MX al contexto compartido para SMTP
            if name == "mx" and result.status == CheckStatus.PASS:
                ctx.shared["mx_records"] = result.detail.get("records")

        # ---- 4. SMTP segun modo y politica ----
        smtp_cfg = self.policy.mode_config(mode).get("smtp", True)
        if smtp_cfg is True:
            if self.policy.smtp_blocked(domain):
                assessment.checks.append(
                    CheckResult(
                        "smtp", CheckStatus.SKIPPED,
                        self.checkers["smtp"].weight,
                        note=(
                            "Este proveedor bloquea verificacion SMTP; "
                            "score basado en MX y dominio"
                        ),
                    )
                )
            else:
                assessment.checks.append(await self.checkers["smtp"].run(ctx))
        elif smtp_cfg == "defer":
            # Futuro: encolar en worker. Hoy: marcar pendiente sin castigar score.
            assessment.checks.append(
                CheckResult(
                    "smtp", CheckStatus.SKIPPED,
                    self.checkers["smtp"].weight,
                    note="Verificacion SMTP diferida (async no habilitado aun)",
                )
            )
        else:
            # quick mode: SMTP explicitamente apagado
            assessment.checks.append(
                CheckResult(
                    "smtp", CheckStatus.SKIPPED,
                    self.checkers["smtp"].weight,
                    note="Modo rapido: SMTP omitido",
                )
            )

        # ---- 5. Scoring ----
        assessment.confidence_score, assessment.verdict = self.scorer.score(
            assessment.checks
        )
        return self._finish(assessment, start)

    async def _run_cached(self, name: str, ctx: CheckContext) -> CheckResult:
        if name in CACHEABLE:
            key = f"{name}:{ctx.domain}"
            cached = self.cache.get(key)
            if cached is not None:
                return cached
            result = await self.checkers[name].run(ctx)
            # Solo cachear resultados concluyentes
            if result.status in (CheckStatus.PASS, CheckStatus.FAIL):
                self.cache.set(key, result)
            return result
        return await self.checkers[name].run(ctx)

    @staticmethod
    def _finish(a: EmailAssessment, start: float) -> EmailAssessment:
        a.processing_time_ms = round((time.time() - start) * 1000, 2)
        return a


def to_response(a: EmailAssessment) -> dict[str, Any]:
    """
    Mapea EmailAssessment al contrato actual de EmailValidationResponse.
    Los campos existentes se mantienen identicos; verdict y checks son
    nuevos y opcionales (agregar como Optional en schemas.py).
    """
    smtp = a.get("smtp")
    mx = a.get("mx")
    syntax = a.get("syntax")
    disposable = a.get("disposable")

    def tri(c: Optional[CheckResult]) -> Optional[bool]:
        if c is None:
            return None
        if c.status == CheckStatus.PASS:
            return True
        if c.status == CheckStatus.FAIL:
            return False
        return None  # INCONCLUSIVE / SKIPPED

    smtp_performed = bool(smtp and smtp.status != CheckStatus.SKIPPED)

    return {
        # ---- contrato existente (RapidAPI) ----
        "email": a.email,
        "domain": a.domain or "",
        "syntax_valid": bool(syntax and syntax.status == CheckStatus.PASS),
        "has_mx_records": bool(mx and mx.status == CheckStatus.PASS),
        "mx_records": (mx.detail.get("records") if mx else None),
        "is_disposable": bool(
            disposable and disposable.status == CheckStatus.FAIL
        ),
        "smtp_check_performed": smtp_performed,
        "mailbox_exists": tri(smtp) if smtp_performed else None,
        "smtp_response": (
            (smtp.detail.get("smtp_response") or smtp.note) if smtp else None
        ),
        "is_catch_all": (smtp.detail.get("is_catch_all") if smtp else None),
        "deliverability_score": a.confidence_score,
        "is_valid": a.verdict == "ACCEPT",
        "processing_time_ms": a.processing_time_ms,
        # ---- nuevos, opcionales ----
        "verdict": a.verdict,
        "checks": [
            {"name": c.name, "status": c.status.value, "note": c.note}
            for c in a.checks
        ],
    }


# Singleton listo para importar desde routes.py
orchestrator = Orchestrator()
