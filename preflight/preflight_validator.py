#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Preflight Validator (T1 + T4) — arXiv 2610.00025. Non-LLM baseline."""
from __future__ import annotations

import re

from ci_baseline_checker.baseline_checker import TAU

TAU: float = TAU

class PreflightValidator:
    """Validador defensivo: T1 (shell) y T4 (tool selection por firma)."""
    SHELL_RISK = [re.compile(p, re.IGNORECASE) for p in [r"rm\s+-rf", r"sudo\s+", r"curl\s+.*\|\s*(sh|bash)", r"eval\s*\("]]
    TOOL_SIGS = {"ls": "list_dir", "cat": "read_file", "git": "git_op"}

    def __init__(self, tau: float = TAU) -> None:
        self.tau = tau

    def evaluate_t1_shell(self, task_context: str) -> dict:
        hits = [p.pattern for p in self.SHELL_RISK if p.search(task_context)]
        score = 0.0 if hits else 1.0
        return {"is_eligible": score >= self.tau, "tau_score": score, "reason": "T1-shell-risk" if hits else "T1-ok"}

    def evaluate_t4_tool_selection(self, requested_tools: list, allowed_signatures: list) -> dict:
        missing = [t for t in requested_tools if t not in self.TOOL_SIGS or self.TOOL_SIGS[t] not in allowed_signatures]
        score = 0.0 if missing else 1.0
        return {"is_eligible": score >= self.tau, "tau_score": score, "reason": f"T4-missing:{missing}" if missing else "T4-ok"}

    def check_eligibility(self, task_description: str) -> dict:
        r1 = self.evaluate_t1_shell(task_description)
        score = r1["tau_score"]
        return {"is_eligible": r1["is_eligible"], "tau_score": score, "reason": r1["reason"]}

if __name__ == "__main__":
    v = PreflightValidator()
    print("PASS:", v.check_eligibility("ls -la /workspace"))
    print("FAIL:", v.check_eligibility("rm -rf /tmp/test"))
