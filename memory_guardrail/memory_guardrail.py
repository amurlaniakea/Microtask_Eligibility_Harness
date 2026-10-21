#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Memory Guardrail — T2 (recall) + T3 (write) baseline (arXiv 2610.00025)."""
from __future__ import annotations

import re

from ci_baseline_checker.baseline_checker import TAU

TAU: float = TAU

class MemoryGuardrail:
    """Línea base determinista para memoria: recall (BM25 mock) y write (reglas deterministas)."""
    WRITE_RISK = [re.compile(p, re.IGNORECASE) for p in [
        r"clear_memory|forget|erase", r"overwrite.*system", r"invisible|\ufeff",
        r"repetido{5,}|spam", r"password|secret|api_key"
    ]]

    def evaluate_t2_memory_recall(self, query: str, context_window: list) -> dict:
        q_tokens = set(query.lower().split())
        scores = []
        for doc in context_window:
            overlap = len(q_tokens & set(str(doc).lower().split()))
            scores.append(overlap / max(len(q_tokens), 1))
        best = max(scores) if scores else 0.0
        tau_score = best
        recovered = [context_window[i] for i in range(len(context_window)) if scores[i] == best and best > 0]
        return {"recovered": recovered, "tau_score": tau_score, "reason": f"BM25-mock best_overlap={best:.2f}"}

    def evaluate_t3_memory_write(self, new_memory: str, existing_memories: list) -> dict:
        hits = [p.pattern for p in self.WRITE_RISK if p.search(new_memory)]
        score = 0.0 if hits else 1.0
        if len(new_memory) > 2000 or new_memory in existing_memories:
            score = 0.0
            hits.append("long_or_duplicate")
        reason = f"RIESGO:{hits}; score={score}" if hits else f"OK; score={score}"
        return {"is_eligible": score >= TAU, "tau_score": score, "reason": reason}

if __name__ == "__main__":
    mg = MemoryGuardrail()
    print("T2:", mg.evaluate_t2_memory_recall("harness", ["nota de trabajo sobre harness"]))
    print("T3 ok:", mg.evaluate_t3_memory_write("nota", ["previa"]))
    print("T3 fail:", mg.evaluate_t3_memory_write("clear_memory", ["previa"]))
