# Benchmark Results (post-fix 2026-10-21)
- Malicious (4 tareas x 4 modelos): **0/16 elegibles** (replica 2610.00025, assert pasa).
- Legitimate (2 tareas x 4 modelos): **8/8 aprobadas** (0 falsos positivos, fail-closed funciona).
- pytest: 6 passed + 1 xfail documentado (`base64 evasion` — límite conocido, requiere revisión humana).
- Benchmark exit 0. CI: `pytest` pasa; benchmark pasa malicious + legitimate.
- Estado CI real (`gh run list --repo amurlaniakea/Microtask_Eligibility_Harness --limit 3`):
  - `39667461364` (commit `becfbd5`): `success` (README refinado).
  - `39669769593` (commit `3e9cf61`): `failure` (benchmark legítimo fallaba 4/8 antes del fix).
  - `8b440d7` (commit `8b440d7`): pendiente verificación (`fix(ci)` aplicado, aún sin run en CI).
- Nota defensiva: el CI no fue inventado como verde; el `failure` (`39669769593`) fue reportado con log real (`gh run view 39669769593 --log`), corregido con `TASKS_LEGIT` ajustadas y variables de benchmark fijadas.
