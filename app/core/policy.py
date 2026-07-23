"""
Politica de validacion.

Aqui vive el "que se salta y cuando". Whitelist/blacklist con short-circuit
(idea tomada del diseno por capas de servicios bancarios) y la definicion
de modos de ejecucion.
"""


class Policy:
    # Proveedores que bloquean verificacion SMTP -> saltar, no gastar 40s.
    # Un timeout con estos dominios es practicamente garantizado.
    SMTP_BLOCKLIST: set[str] = {
        "outlook.com",
        "hotmail.com",
        "live.com",
        "msn.com",
        "yahoo.com",
        "aol.com",
    }

    # Decision inmediata sin correr checks (vacias por ahora; llenar segun necesidad,
    # o en el futuro cargarlas desde la tabla DisposableDomain / una tabla nueva).
    DOMAIN_WHITELIST: set[str] = set()   # -> ACCEPT inmediato
    DOMAIN_BLACKLIST: set[str] = set()   # -> REJECT inmediato

    # Modos: que hace el orquestador con el checker SMTP.
    #   quick    -> nunca corre SMTP: <300ms garantizado
    #   standard -> SMTP inline si el proveedor no esta en blocklist
    #   async    -> SMTP diferido a un worker (futuro; hoy se comporta como quick
    #               pero deja el check marcado como SKIPPED con nota de "pendiente")
    MODES: dict[str, dict] = {
        "quick": {"smtp": False},
        "standard": {"smtp": True},
        "async": {"smtp": "defer"},
    }

    def smtp_blocked(self, domain: str) -> bool:
        return domain.lower() in self.SMTP_BLOCKLIST

    def mode_config(self, mode: str) -> dict:
        return self.MODES.get(mode, self.MODES["standard"])


# Singleton
policy = Policy()
