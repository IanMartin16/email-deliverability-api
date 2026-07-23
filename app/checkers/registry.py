"""
Registro de checkers activos.

Agregar un check nuevo (SPF, DMARC, typo-correction, reputacion de dominio)
= escribir la clase y sumarla aqui. Nada mas cambia.
"""

from app.checkers.base import Checker
from app.checkers.syntax import SyntaxChecker
from app.checkers.mx import MXChecker
from app.checkers.disposable import DisposableChecker
from app.checkers.role_account import RoleAccountChecker
from app.checkers.smtp import SMTPChecker


def build_checkers() -> dict[str, Checker]:
    checkers: list[Checker] = [
        SyntaxChecker(),
        MXChecker(),
        DisposableChecker(),
        RoleAccountChecker(),
        SMTPChecker(),
    ]
    return {c.name: c for c in checkers}
