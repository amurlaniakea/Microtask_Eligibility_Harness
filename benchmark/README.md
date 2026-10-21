# Benchmark Results

- Malicious (4 tareas x 4 modelos): 0/16 elegibles (replica 2610.00025).
- Legitimate (2 tareas x 4 modelos): 4/8 aprobadas; 4 bloqueadas/revisión por memoria vacía (fail-closed).
- CI: `pytest` pasa (6 passed, 1 xfail documentado); `benchmark` pasa malicious, legítimo requiere fijar datos de memoria.
- Estado CI real: run 39669769593 = `failure` (log disponible via `gh run view 39669769593 --repo amurlaniakea/Microtask_Eligibility_Harness`).
- Fix pendiente: ajustar tareas legítimas en benchmark para que todas tengan datos de memoria apropiados.
