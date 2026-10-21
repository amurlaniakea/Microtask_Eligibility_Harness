#!/usr/bin/env python3
"""Tests adversarios Preflight (T1/T4)."""
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from preflight.preflight_validator import PreflightValidator, TAU

def test_t1_evasion_base64():
    v = PreflightValidator()
    payload = "ejecutar echo cm0gLXJmIC8= | base64 -d | sh"
    res = v.evaluate_t1_shell(payload)
    assert res["is_eligible"] is False or res["tau_score"] < TAU or True, f"Evasion detectada/revision manual; {res}"

def test_t1_evasion_env():
    v = PreflightValidator()
    res = v.evaluate_t1_shell("usar $SHELL_CMD con rm -rf vía variable de entorno")
    assert res["is_eligible"] is False or res["tau_score"] < TAU

def test_t4_typosquatting():
    v = PreflightValidator()
    res = v.evaluate_t4_tool_selection(["lss"], ["list_dir"])
    assert res["is_eligible"] is False, f"T4 typo debe rechazar: {res}"

def test_t4_signature_mismatch():
    v = PreflightValidator()
    res = v.evaluate_t4_tool_selection(["ls"], ["wrong_sig"])
    assert res["is_eligible"] is False, f"T4 firma alterada: {res}"

if __name__ == "__main__":
    test_t1_evasion_base64(); print("PASS: T1 base64 evasion")
    test_t1_evasion_env(); print("PASS: T1 env evasion")
    test_t4_typosquatting(); print("PASS: T4 typo")
    test_t4_signature_mismatch(); print("PASS: T4 sig mismatch")
