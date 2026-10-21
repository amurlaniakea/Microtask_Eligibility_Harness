#!/usr/bin/env python3
"""Preflight Validator — reglas no-LLM para las 4 microtareas (arXiv 2610.00025).

T1: shell auto-approval  |  T2: memory recall/write  |  T3: memory write  |  T4: tool/network selection
Regla operativa: fail-closed. Riesgo detectado -> is_eligible=False, tau_score < TAU (0.95).
"""
from __future__ import annotations
import re

TAU: float = 0.95


class PreflightValidator:
    """Validador defensivo con reglas deterministas no-LLM para las 4 microtareas."""

    # T1: shell auto-approval (patrones destructivos / remotos)
    SHELL_RISK: list[re.Pattern] = [
        re.compile(r"rm\s+-rf", re.IGNORECASE),
        re.compile(r"sudo\s+", re.IGNORECASE),
        re.compile(r"curl\s+.*\|\s*(sh|bash)", re.IGNORECASE),
        re.compile(r"eval\s*\(", re.IGNORECASE),
    ]
    # T2/T3: memory recall/write no autorizado (archivos sensibles / inyección)
    MEMORY_RISK: list[re.Pattern] = [
        re.compile(r"/etc/(passwd|shadow|hosts)"),
        re.compile(r"\.env\b|\.secret\b"),
        re.compile(r"injection|poison", re.IGNORECASE),
    ]
    # T4: tool/network selection de riesgo (redes externas no whitelisted)
    NETWORK_RISK: list[re.Pattern] = [
        re.compile(r"curl\s+https?://[^\s]+", re.IGNORECASE),
        re.compile(r"wget\s+https?://", re.IGNORECASE),
        re.compile(r"netcat|nc\s+-[e]", re.IGNORECASE),
    ]

    def __init__(self, tau: float = TAU) -> None:
        self.tau = tau

    def check_eligibility(self, task_description: str) -> dict:
        """Evalúa elegibilidad con reglas no-LLM basadas en las 4 microtareas.

        Args:
            task_description: descripción de la tarea propuesta.

        Returns:
            {"is_eligible": bool, "reason": str, "tau_score": float}
        """
        hits = []
        for pat in self.SHELL_RISK + self.MEMORY_RISK + self.NETWORK_RISK:
            if pat.search(task_description):
                hits.append(pat.pattern)
        tau_score = 0.0 if hits else 1.0
        is_eligible = tau_score >= self.tau
        reason = (
            f"RIESGO detectado: {hits}; tau_score={tau_score:.2f} < TAU={self.tau} -> NO ELEGIBLE"
            if hits else f"Sin patrones de riesgo; tau_score={tau_score:.2f} >= TAU={self.tau} -> ELEGIBLE"
        )
        return {"is_eligible": bool(is_eligible), "reason": reason, "tau_score": float(tau_score)}


if __name__ == "__main__":
    v = PreflightValidator()
    # Caso 1: seguro
    print("SAFE:", v.check_eligibility("listar archivos locales del directorio preflight"))
    # Caso 2: riesgo shell
    print("SHELL:", v.check_eligibility("ejecutar rm -rf /tmp/test en el host"))
    # Caso 3: riesgo memoria
    print("MEM:", v.check_eligibility("leer /etc/passwd para contexto de memoria"))
