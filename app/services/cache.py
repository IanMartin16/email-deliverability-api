"""
Cache por dominio con TTL. In-memory por ahora (suficiente para una sola
instancia en Railway); la interfaz permite cambiar a Redis despues sin
tocar el orquestador.

Que cachear: resultados de checks cuyo resultado depende del DOMINIO,
no del email individual (mx, disposable). NO cachear syntax (trivial)
ni smtp (depende del buzon individual).
"""

import time
from typing import Any, Optional


class DomainCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time() + self.ttl, value)

    def clear(self) -> None:
        self._store.clear()


# TTL de 1h: los MX de un dominio no cambian minuto a minuto
domain_cache = DomainCache(ttl_seconds=3600)
