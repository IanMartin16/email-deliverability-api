"""
Scorer: consume la lista de CheckResult y produce (confidence_score, verdict).

Clave: normaliza sobre los pesos APLICABLES (excluye SKIPPED), asi Outlook
no queda castigado solo porque SMTP no pudo correr. INCONCLUSIVE aporta
credito parcial (50%) reflejando incertidumbre, no fallo.

verdict (ACCEPT / REJECT / RISKY) es el veredicto accionable para el
suscriptor: mando / no mando / reviso.
"""

from app.core.results import CheckResult, CheckStatus


class Scorer:
    # Un FAIL en estos checks = REJECT sin importar el score
    CRITICAL: set[str] = {"syntax", "mx"}

    # Desechable tambien tumba el verdict (aunque no el score completo)
    REJECT_ON_FAIL: set[str] = {"disposable"}

    INCONCLUSIVE_CREDIT = 0.5

    def score(self, checks: list[CheckResult]) -> tuple[float, str]:
        applicable = [c for c in checks if c.status != CheckStatus.SKIPPED]
        total_weight = sum(c.weight for c in applicable) or 1.0

        earned = 0.0
        for c in applicable:
            if c.status == CheckStatus.PASS:
                earned += c.weight
            elif c.status == CheckStatus.INCONCLUSIVE:
                earned += c.weight * self.INCONCLUSIVE_CREDIT

        confidence = round(earned / total_weight * 100, 2)

        # Veredicto
        critical_fail = any(
            c.name in self.CRITICAL and c.status == CheckStatus.FAIL for c in checks
        )
        reject_fail = any(
            c.name in self.REJECT_ON_FAIL and c.status == CheckStatus.FAIL
            for c in checks
        )
        if critical_fail or reject_fail:
            return confidence, "REJECT"

        has_inconclusive = any(
            c.status == CheckStatus.INCONCLUSIVE for c in checks
        )
        if confidence >= 85 and not has_inconclusive:
            return confidence, "ACCEPT"
        if confidence >= 60:
            return confidence, "RISKY"
        return confidence, "REJECT" if confidence < 40 else "RISKY"


# Singleton
scorer = Scorer()
