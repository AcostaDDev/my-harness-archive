# P012-T002 — Propuesta de continuidad tras el rechazo de Ruff

Fecha: 2026-10-24. Base: `e68fdfa`. **Estado: alternativa A elegida por HITL; implementación offline autorizada.**
[Parada conservada](P012-T002_CONTINUACION_T009.md) y
[D193](../DECISIONS.md#d193--p012-t002-fixture-limpio-incorporado-y-rechazo-por-ruff).

## 1. Fronteras comprobadas offline

- `OfflineEngine.resume` exige el contexto/política original. El run `f98b16d9…` agotó sus cero correcciones;
  un retry no invoca al ejecutor. Revalidar solo prepara/valida/revisa, sin ejecutar ni formatear.
- `OfflineEngine.start` exige un checkout limpio en D088. Otro job en B2 mezclaría el diff fallido y se rechaza.
  `LocalComposer._composed` tampoco permite adoptar otra composición en los jobs congelados.
- No hay que repetir necesariamente la incorporación B: `SPECIFICATION` §8 permite registrar un proyecto ya
  gestionado; la UI normal ofrece crear su fase y editar documentación con vista previa, CAS y commit.
  `PhaseRepository.create` trabaja por raíz, conserva las fases existentes y no necesita un turno de modelo.
- Un clon independiente y limpio del **commit documental `9808fd97d349c6eeacb766be8ff5e5603b6e974c`** de B2
  contiene los documentos D088 y el código anterior a la tarea. No copia sus tres modificaciones fallidas,
  SQLite, venv ni archivos ignorados. B/B2, sus rutas, diffs, historiales y configuraciones se conservan.
- **El formateador D133 no es configurable en un perfil declarado actualmente.** `_profile` acepta las claves
  de D095 y solo `sensitive_allowlist` como opcional; rechaza `formatter_argv` y `formatter_paths`.
  El motor/runner sí implementan el formateo, pero `local_config.py` lo declara únicamente para el perfil de
  receta Django. No se puede añadir al TOML de python-django sin una tarea de producto nueva.

Fuentes: `core/engine/workflow.py` (`start`, `resume`, `_format`, `_review_loop`),
`services/local_config.py` (`_profile`, `_composed`, perfil python-django-recipe), `storage/phases.py` (`create`),
`api/managed.py` (alta de fase y edición documental), `frontend/src/Phases.tsx` y `pages/Phases.tsx`.
[Tareas](../flows/task-run.md), [documentos](../flows/documents.md), [fases](../flows/phase-lifecycle.md),
[D095](../DECISIONS.md#d095--p008-t008-perfiles-declarados-en-local-config-4) y
[D133](../DECISIONS.md#d133--p009-t019-el-harness-formatea-con-la-herramienta-del-perfil-tras-cada-turno-del-ejecutor).
No se declara un defecto del motor: este rechazó correctamente las dos validaciones fallidas.

## 2. Alternativa A — Habilitar el formateador en perfiles declarados

**Propuesta recomendada para el producto, pendiente de elección.** Abrir una tarea acotada offline que exponga
el formateador ya implementado a los perfiles declarados, con la misma frontera D133: comando sin shell,
argv terminado en `--`, patrones relativos explícitos, autorización de la composición, archivos existentes
permitidos por el contrato y registro del formateo anterior a la validación. Sin rebajar Ruff ni añadir
formateo a revalidaciones. Los perfiles que no lo declaren conservan comportamiento y huellas.

Antes de implementar se concreta el contrato de configuración y su compatibilidad con los formatos históricos;
no se presupone que admita claves nuevas en cualquier versión. Regresiones sintéticas de carga, autorización,
huellas y ejecución nativa falsa; ejemplo y documentación/flujos al día. No exige proveedores reales, cambio de
modelo/esfuerzo ni ampliación de presupuesto. Una implementación no acreditaría por sí sola éxito real nuevo.

Después de esa tarea, construir/verificar un wheel nuevo y preparar una continuación desde el commit documental
limpio requerirían otra propuesta y consentimiento operativo. Se conservarían cero correcciones si el usuario
no decide cambiarlas. No se aplicaría el formateador al checkout fallido ni al run congelado.

Motivo: el problema observado es mecánico y el producto ya dispone de formateo determinista antes de revisar;
el operador del perfil declarado carece de acceso a esa capacidad. Evita consumir otro turno para pedir a un
modelo que reproduzca el formato de una herramienta. Es una ampliación explícita, no una corrección ya decidida.

## 3. Alternativa B — Nuevo run con un ciclo de corrección normal

Sin modificar el producto: clonar localmente y sin hardlinks el HEAD documental limpio de B2 en otra raíz del
área, sin remoto/alternates/enlaces. Preparar venv/temporales propios y copia TOML con presets/composición nuevos,
manteniendo el mismo perfil declarado **sin formateador** y las seis validaciones. Mismo wheel `6efbd82`.

Registrar por UI como proyecto ya gestionado, crear P001 desde su ROADMAP y confirmar, también por UI, solo los
cambios documentales de preparación que reflejen la nueva composición y **max_revision_cycles = 1** en
AGENTS/NEXT_STEPS y una decisión nueva del hijo. No editar bloques gestionados ni archivos históricos;
los commits documentales preceden a la tarea y dejan el checkout limpio. No repetir la conversación B.

Ejecutar la misma tarea funcional y sus tres rutas con Claude sonnet/low y Codex gpt-6-luna/low. Autorizar
explícitamente la excepción a la parada por primera validación fallida: un REVISE válido puede activar **una**
corrección dentro del contrato y su revisión. No garantiza que se use ni que funcione. Se mantienen las paradas
por proveedor, esquema, timeout, permisos, CAS/hash, preguntas o cuarentena; sin fallback ni reparación manual.

Máximo nuevo **3 Claude + 2 Codex** (plan, revisión y revisión de corrección; ejecución y corrección).
Acumulado máximo **Claude 10/12 y Codex 4/4**: **amplía el techo Codex de 3 a 4** y cambia la política del nuevo
trabajo de cero a una corrección. El saldo actual 5/1 no basta para prometer ese ciclo; necesita autorización
explícita. No se modifica el presupuesto/política de los runs originales. T003/T004 siguen fuera.

Esta alternativa evita un cambio de producto, pero depende de que el ejecutor resuelva el formato y necesita
preparación y consumo real adicionales. Las rutas/nombres finales, delta TOML y cambios documentales exactos
deben quedar revisables antes del consentimiento operativo; elegirla aquí todavía no inicia esos efectos.

## 4. HITL y alcance de esta sesión

Las decisiones existentes no eligen entre ampliar el perfil declarativo o ampliar el consumo/ciclo de un run
nuevo. El usuario debe elegir. Una tercera opción es mantener la parada y no preparar otra continuación.
La elección autoriza solo el trabajo expresamente incluido en su respuesta; no se toma el silencio como permiso.

**Respuesta:** «Implementar formateador declarativo offline (recomendado)». Se abre P012-T010 para implementar
la alternativa A, sin ejecutar la B ni operaciones reales. La separación de versiones se concreta con
`local-config-8`; v1–v7 conservan su contrato. [Entrega](P012-T010_FORMATEADOR_DECLARATIVO.md).

Comprobación dirigida: ocho tests sintéticos existentes sobre corrección con sesión nueva, presupuesto agotado,
revalidación sin ejecutor, contexto congelado, checkout sucio, edición documental por CAS, fase por raíz y ruta
HTTP de fase. Sin ejecutar CLI reales, servicio, fixtures privados ni modelos. No se repiten suites completas.
Lectura Git de B2: HEAD documental esperado, tres rutas fallidas aún presentes; sin modificarlo o copiar su diff
al candidato. No se crean áreas ni TOML operativos, ni se toca SQLite o configuración global.
