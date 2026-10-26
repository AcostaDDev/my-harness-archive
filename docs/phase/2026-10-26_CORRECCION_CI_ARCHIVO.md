# Corrección documental y carrera de CI del archivo

Fecha: 2026-10-26. Encargo: corregir el desfase de ROADMAP y el fallo de GitHub Actions comunicado por el
usuario para `my-harness-archive`, con commit en inglés. Mantenimiento acotado posterior a P012, sin fase nueva.
Decisión: [D213](../DECISIONS.md#d213--mantenimiento-git-desactivado-en-fixtures-de-incorporación).

## Causa y corrección

El log aportado muestra 1759 pruebas pasadas y una fallida: la prueba de rechazo de Git sin `--no-lazy-fetch`
observa la desaparición de `.git/objects/maintenance.lock` entre sus dos snapshots. Sustituye `Git.run` antes
de llamar al inventario, por lo que este no llega a ejecutar Git. El commit previo del fixture sí usaba un
helper sin supresión de mantenimiento automático.

Una regresión registra `GIT_TRACE2_EVENT` fuera del checkout sintético y comprueba los procesos hijos reales
del commit. Antes del cambio falla de forma determinista con:

```text
AssertionError: [['git', 'maintenance', 'run', '--auto', '--quiet', '--detach']]
1 failed
```

El helper Git compartido de `tests/product/test_project_onboarding.py` añade las opciones por invocación
`-c gc.auto=0 -c maintenance.auto=false`, ya usadas en el adaptador del producto. Se evita el escritor
secundario al crear los fixtures, conservando íntegra la comprobación de bytes de `.git`, incluidos los locks.
Sin sleeps, reintentos, exclusiones de snapshot ni cambios de configuración persistente. La documentación
oficial describe [maintenance.auto](https://git-scm.com/docs/git-config#Documentation/git-config.txt-maintenanceauto)
y [gc.auto](https://git-scm.com/docs/git-config#Documentation/git-config.txt-gcauto).

La fila resumen de P012 en ROADMAP pasa de planificada a completada el 2026-10-26 y enlaza
`archive/phase-012/SUMMARY.md`, coherente con su sección detallada, STATE/NEXT_STEPS y D212. Los documentos
archivados conservan sus bytes y el estado que tenían al congelarse.

## Comprobaciones

- Regresión nueva antes del arreglo: fallo esperado al observar mantenimiento automático real.
- Tras el arreglo: `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0
  tests/product/test_project_onboarding.py tests/product/test_import_local_objects.py`: **30 pasadas**.
- Suite completa paralela: `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`:
  **1761 pasadas, 2 opt-in omitidas, 29 subtests pasados**, en 153,34 s. Diez avisos de deprecación
  Starlette/httpx; sin cambiar dependencias en esta tarea.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **8 pasadas**.
- Parsers documentales: 12 fases, 213 decisiones, sin tareas activas; 127 enlaces relativos comprobados en
  ROADMAP, STATE, NEXT_STEPS e informe. STATE dentro del límite de 24 KiB.
- Diff revisado y `git diff --check` correcto. Sin cambios en `docs/archive/` ni cuerpos D001–D212.

## Límites

Pruebas offline con Git/SQLite temporales y datos sintéticos; sin proveedores ni smokes. No se cambia código
de producto, modelos, migraciones, API, flujos ni frontend. No se regeneran candidato/paquete ni manifiestos
de P012. Sin push ni CI remota ejecutados por esta tarea; el error de GitHub procede del log del usuario.
El archivo remoto comunicado y el candidato público independiente mantienen sus alcances separados.
No se repiten frontend, Alembic ni build de distribución, al cambiar únicamente documentación y pruebas.
