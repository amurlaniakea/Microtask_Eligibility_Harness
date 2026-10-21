#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Harness Adapter — pipeline T1/T2/T3/T4 a través de líneas base no-LLM."""
from ci_baseline_checker.baseline_checker import TAU
from memory_guardrail.memory_guardrail import MemoryGuardrail
from preflight.preflight_validator import PreflightValidator

TAU: float = TAU

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
        has_risk = any(s == 0.0 for s in scores.values())
        has_insufficient = any(0.0 < s < TAU for s in scores.values())
        blocked = any(s < TAU for s in scores.values())
        if has_risk:
            status = "blocked"
        elif has_insufficient:
            status = "requires_human_review"
        elif blocked:
            status = "blocked"
        else:
            status = "approved"
        gate = [k for k, s in scores.items() if s < TAU]
        return {"status": status, "tau_scores": scores, "reason": f"T1={t1['reason']}; T2={t2['reason']}; T3={t3['reason']}; T4={t4['reason']}", "gate": gate if gate else None}

if __name__ == "__main__":
    adapter = HarnessAdapter()
    print("PASS:", adapter.process_task({"context":"ls -la", "tools":["ls"], "allowed_sigs":["list_dir"]}))
    print("FAIL:", adapter.process_task({"context":"rm -rf /", "tools":["ls"], "allowed_sigs":["list_dir"]}))
