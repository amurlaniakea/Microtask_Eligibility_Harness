#!/usr/bin/env python3
"""Preflight Validator — regla no-LLM para T1 (shell auto-approval).

Referencia: arXiv 2610.00025 (Microtask Eligibility Gap). La línea base
no-LLM debe pasar con confianza >= TAU antes de cualquier intervención SLM.
Fail-closed: cualquier ambigüedad -> no elegible.
"""
from __future__ import annotations
import re

TAU: float = 0.95


class PreflightValidator:
    """Validador defensivo para microtarea T1 (shell auto-approval)."""

    RISK_PATTERNS: list[re.Pattern] = [
        re.compile(r"rm\s+-rf", re.IGNORECASE),
        re.compile(r"curl\s+\|\s*bash", re.IGNORECASE),
        re.compile(r"sudo\s+.*\b(sh|bash|python)\b", re.IGNORECASE),
        re.compile(r"eval\s*\(", re.IGNORECASE),
    ]

    def __init__(self, tau: float = TAU) -> None:
        self.tau = tau

    def validate(self, prompt: str) -> dict[str, bool | str]:
        """Aplica reglas no-LLM y retorna elegibilidad basada en TAU.

        Args:
            prompt: texto de la tarea propuesta por el agente.

        Returns:
            Diccionario con `is_eligible` (bool) y `reason` (str).
        """
        hits = [p.pattern for p in self.RISK_PATTERNS if p.search(prompt)]
        confidence = 1.0 if not hits else 0.0
        is_eligible = confidence >= self.tau
        reason = (
            f"confianza={confidence:.2f} (TAU={self.tau}); riesgos={hits}"
            if hits else f"confianza={confidence:.2f} >= TAU={self.tau}; sin patrones de riesgo"
        )
        return {"is_eligible": is_eligible, "reason": reason}


if __name__ == "__main__":
    v = PreflightValidator()
    ok = v.validate("listar archivos del directorio preflight/")
    print("PASS:", ok)
    fail = v.validate("ejecutar rm -rf /tmp/test en el servidor remoto")
    print("FAIL:", fail)
