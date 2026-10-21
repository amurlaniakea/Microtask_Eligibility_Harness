# Microtask Eligibility Harness

![CI](https://github.com/amurlaniakea/Microtask_Eligibility_Harness/actions/workflows/ci.yml/badge.svg) ![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## El Problema

Agent harnesses delegan microtareas críticas (shell auto-approval, memory recall/write, tool selection) a modelos pequeños (SLMs). El paper `arXiv:2610.00025` (Hu / Ramachandran, 2026) mide un **Microtask Eligibility Gap**: con línea base no-LLM + regla CI (`tau_score >= 0.95`), ninguna de las 16 configuraciones evaluadas (`Qwen3` 0.6/1.7/4/8B, `Llama-3.x`) pasa. **0/16 elegibles**. La solución no es confiar en el SLM: es proteger cada microtarea con una base determinista certificada.

## La Solución

Este proyecto implementa un harness defensivo con 4 componentes deterministas:

- **Preflight Validator** (T1 / T4): reglas no-LLM (`re.Pattern`) para shell (`rm -rf`, `sudo`, `eval`) y tool selection (whitelist de firmas). Fail-closed.
- **Memory Guardrail** (T2 / T3): línea base BM25 simulada (solapamiento determinista de tokens) con cascade de contexto; rechazo de inyección (`clear_memory`, `.env`, `.secret`).
- **Harness Adapter**: pipeline determinista. Status: `approved` (todos >= TAU), `blocked` (algún score == 0.0 — riesgo confirmado), `requires_human_review` (algún score < TAU pero > 0.0 — confianza insuficiente, sin riesgo confirmado).
- **CI Baseline Checker**: umbral `TAU = 0.95` importado como fuente de verdad; tests adversarios incluidos.

## Uso Rápido

```bash
# Clonar e instalar en modo desarrollo
git clone https://github.com/amurlaniakea/Microtask_Eligibility_Harness.git
cd Microtask_Eligibility_Harness
pip install -e .[dev]

# Correr tests (incluye adversarios + coverage)
pytest -v --cov=. --cov-report=term-missing

# Ejecutar benchmark (replica 2610.00025: MALICIOUS 0/16 + LEGITIMATE 8/8)
python benchmark/run_benchmark.py

# Ejecutar linting
ruff check .
```

Salida esperada:
```
Benchmark completado: 0/16 elegibles (paper 2610.00025: 0/16).
ASSERT PASADO: 0/16 elegibles, replicando el eligibility gap del paper.
```

## Desarrollo

Este proyecto es un paquete Python instalable (Fase 2 completada 2026-10-21).
- **Instalación en desarrollo**: `pip install -e .[dev]`
- **Linting**: `ruff check .`
- **Coverage**: `pytest --cov=. --cov-report=term-missing`
- **Empaquetado**: `pip install build && python -m build`
- **CI**: `.github/workflows/ci.yml` ejecuta `ruff`, `pytest --cov=.` y `benchmark` en cada push/PR.

## Referencia

- Paper: [arXiv:2610.00025 — Measuring the Microtask Eligibility Gap](https://arxiv.org/abs/2610.00025) (Hu, Ramachandran; 2026).
- Licencia: [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0) (`LICENSE`, 661 líneas, texto FSF verbatim).
- Autor: Pedro Sordo Martínez — `amurlaniakea@gmail.com`
