# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
#!/usr/bin/env python3
"""Memory Guardrail — T2 (recall) + T3 (write) non-LLM baseline (arXiv 2610.00025).
Línea base BM25 simulada con solapamiento determinista de tokens; SLM solo para re-ranking si score < TAU.
"""
from __future__ import annotations
import re, importlib.util
spec = importlib.util.spec_from_file_location("baseline", "ci_baseline_checker/baseline_checker.py")
baseline_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline_mod)
TAU = baseline_mod.TAU

class MemoryGuardrail:
    """Línea base determinista para memoria: recall (BM25 mock) y write (reglas deterministas)."""

    # T3: patrones de inyección / sobrescritura / metadatos críticos
    WRITE_RISK = [re.compile(p, re.IGNORECASE) for p in [
        r"forget|erase|clear_memory", r"overwrite.*system", r"invisible|\u200b|\ufeff",
        r"repetido{5,}|spam", r"password|secret|api_key"
    ]]

    def evaluate_t2_memory_recall(self, query: str, context_window: list) -> dict:
        # Mock determinista: solapamiento de tokens entre query y contexto
        q_tokens = set(query.lower().split())
        scores = []
        for doc in context_window:
            overlap = len(q_tokens & set(str(doc).lower().split()))
            scores.append(overlap / max(len(q_tokens), 1))
        best = max(scores) if scores else 0.0
        tau_score = best
        return {"recovered": [context_window[i] for i in range(len(context_window)) if scores[i] > 0] if best > 0 else [],
                "tau_score": tau_score, "reason": f"BM25-mock best_overlap={best:.2f}"}

    def evaluate_t3_memory_write(self, new_memory: str, existing_memories: list) -> dict:
        hits = [p.pattern for p in self.WRITE_RISK if p.search(new_memory)]
        # Rechazar si intenta sobrescribir memoria crítica o inyectar patrones
        score = 0.0 if hits else 1.0
        # Rechazar si excede longitud razonable o es duplicado exacto malicioso
        if len(new_memory) > 2000 or new_memory in existing_memories:
            score = 0.0
            hits.append("long_or_duplicate")
        reason = f"RIESGO:{hits}; score={score}" if hits else f"OK; score={score}"
        return {"is_eligible": score >= TAU, "tau_score": score, "reason": reason}

if __name__ == "__main__":
    mg = MemoryGuardrail()
    print("T2:", mg.evaluate_t2_memory_recall("agente harness", ["microtask eligibility gap", "harness defense"]))
    print("T3 ok:", mg.evaluate_t3_memory_write("nota de trabajo sobre harness", ["nota previa"]))
    print("T3 fail:", mg.evaluate_t3_memory_write("clear_memory forget all", ["nota previa"]))
