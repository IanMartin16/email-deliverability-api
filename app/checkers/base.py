"""
Interfaz base de los checkers.

Todos los checks tienen la misma firma. Agregar SPF, DMARC o typo-check
manana es escribir una clase nueva, no tocar el flujo.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.results import CheckResult


@dataclass
class CheckContext:
    email: str
    domain: str
    # Datos ya resueltos por checkers previos (ej. mx_records) para no repetir trabajo
    shared: dict[str, Any] = field(default_factory=dict)


class Checker(ABC):
    name: str = "base"
    weight: float = 0
    cost: str = "fast"        # "fast" | "slow"
    deferrable: bool = False  # True = candidato a correr async en un worker (SMTP)

    @abstractmethod
    async def run(self, ctx: CheckContext) -> CheckResult:
        ...
