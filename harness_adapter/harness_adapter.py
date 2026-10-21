#!/usr/bin/env python3
"""Harness Adapter — pipeline T1/T2/T3/T4 a través de líneas base no-LLM."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from preflight.preflight_validator import PreflightValidator
from memory_guardrail.memory_guardrail import MemoryGuardrail

TAU = 0.95

class HarnessAdapter:
    def __init__(self):
        self.pf = PreflightValidator()
        self.mg = MemoryGuardrail()

    def process_task(self, task: dict) -> dict:
        t1 = self.pf.evaluate_t1_shell(task.get("context", ""))
        t4 = self.pf.evaluate_t4_tool_selection(task.get("tools", []), task.get("allowed_sigs", []))
        t2 = self.mg.evaluate_t2_memory_recall(task.get("memory_query", ""), task.get("context_window", []))
        t3 = self.mg.evaluate_t3_memory_write(task.get("new_memory", ""), task.get("existing_memories", []))
        scores = {"t1": t1["tau_score"], "t2": t2["tau_score"], "t3": t3["tau_score"], "t4": t4["tau_score"]}
        # Fail-closed: cualquier componente < TAU -> blocked; solo pasa si todos >= TAU y sin riesgo
        blocked = any(s < TAU for s in scores.values())
        status = "approved" if not blocked else "blocked"
        # Si hay riesgo pero no bloque total (por diseño del paper: 0/16 pasan), marcar revisión humana
        if any(s == 0.0 for s in scores.values()):
            status = "requires_human_review"
        return {"status": status, "tau_scores": scores, "reason": f"T1={t1['reason']}; T2={t2['reason']}; T3={t3['reason']}; T4={t4['reason']}"}
