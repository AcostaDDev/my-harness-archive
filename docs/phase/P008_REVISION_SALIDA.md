# P008 — Revisión de salida

Fecha: 2026-10-17. Base revisada: `f650851` (T001–T015). Decisión de revisión:
[D104](../DECISIONS.md#d104--revisión-de-salida-de-p008-con-hallazgos-en-el-flujo-a).

## Dictamen

**Revisión completada; P008 no está lista para cerrar.** Las quince entregas existen y los recorridos sintéticos
previstos están cubiertos, pero el Flujo A incumple la lectura sin ejecución y la confirmación de bytes exactos.
Además, admite una vista previa que no puede completar cuando un destino nuevo está ignorado por Git.
Los tres casos se han reproducido con Git/SQLite temporales y agentes falsos; no son solo sospechas de lectura.

Esta tarea registra los hallazgos y prepara su corrección en P008-T016. No cambia el diseño ni el código del
producto, no cierra ni archiva la fase y no registra este repositorio en el harness. Las ADR y evidencias de las
entregas previas conservan su contenido; este documento añade la evidencia posterior.

## Hallazgos

### H1 — Alta: el inventario del Flujo A ejecuta filtros locales

`adapters/project_import.py:86` consulta `git status` antes de comprobar si hay filtros `clean` o `process`
configurados. Los controles de hooks, fsmonitor y configuración global de `adapters/git.py` no desactivan los
filtros locales del repositorio. `status` puede invocarlos al comparar un archivo cuyo stat cambió.

Reproducción: README versionado, `.gitattributes` con `*.md filter=review-probe`, filtro sintético que deja un
marcador fuera del checkout y devuelve la entrada intacta, y cambio solo de mtime del README. `read_checkout`
acepta el inventario como limpio **y el marcador demuestra que se ejecutó el filtro**, antes de cualquier
confirmación o turno. Incumple T009, D096 y la lectura sin ejecución del Flujo A.

Corrección necesaria: rechazar filtros ejecutables, incluidos los includes locales, antes de la primera
operación Git que pueda invocarlos, y comprobar también la frontera de ejecución de la importación. El Flujo B
ya aplica esa política en `storage/onboarding_commit.py:14` y en el supervisor. Una prueba debe acreditar
rechazo sin marcador, con el origen y el índice intactos.

### H2 — Alta: un commit COMPLETED contiene bytes distintos de la vista confirmada

`core/engine/import_commit.py:130` sella el árbol usando `hash-object --path` del escritor compartido, pero el
Flujo A no contrasta los blobs resultantes con `documents[].after_sha256`. Las conversiones de atributos Git
pueden cambiar los bytes. El Flujo B sí los contrasta en `storage/onboarding_commit.py:43`.

Reproducción: `.gitattributes` con `GEMINI.md text eol=lf` y borrador de GEMINI con CRLF. Se acepta la vista previa,
se confirma y el job termina DONE con importación COMPLETED/COMMITTED. El archivo del worktree conserva CRLF,
pero el blob de `HEAD:GEMINI.md` contiene LF:

| Contenido | SHA-256 |
|---|---|
| Confirmado y escrito en disco | `7422cb318daee9ab89ed83111a3e900c963324db9646f5dcecb8ea0569254e1d` |
| Blob del commit | `33e3ec280f4319f645b532b57d09332d2e04e3334cd376250bb93be04e5ed28c` |

El usuario autoriza unos bytes y el resultado registra otros como válidos. Incumple la confirmación del árbol
exacto de D100 y SPECIFICATION §5.3/§5.8. La comparación debe suceder antes de admitir la vista previa y los
efectos; también debe cubrir documentos archivados y binarios, sin reescribir intenciones históricas.

### H3 — Media: un destino ignorado deja documentos escritos y una importación interrumpida

El Flujo A no comprueba `check-ignore` sobre los destinos nuevos antes de confirmar. El Flujo B sí lo hace
en `storage/onboarding_commit.py:40`.

Reproducción: fixture ReferenceProject sintético con `GEMINI.md` en `.gitignore`, sin GEMINI previo. La vista previa y
la confirmación se aceptan. El escritor aplica los documentos, pero la captura Git posterior omite GEMINI y
el commit se invalida. Resultado: job DONE, importación INTERRUPTED/INVALIDATED, GEMINI escrito, un solo commit
(el inicial) y ninguna fase adoptada. No hay pérdida acreditada de originales; sí una escritura documental
sin el commit prometido, evitable antes de la confirmación y que bloquea la continuidad.

Corrección necesaria: rechazar esos destinos antes de escribir, sin modificar `.gitignore` ni configuración del
usuario. La prueba debe comprobar checkout/índice intactos y ausencia de operación/commit/fase nuevos.

### H4 — Menor: referencias vigentes desactualizadas

- SPECIFICATION F11 conserva «adaptación de UI pendiente (T006)» y F18 «Pendiente (P008-T008)», aunque ambas
  entregas están implementadas y documentadas en D093/D095.
- ARCHITECTURE §6 llama `cli-11` al adaptador vigente (`cli-12`) y `d088-7` al layout vigente (`d088-8`).
- Home, Registry, la ayuda de `serve --config` y el diagnóstico del registro siguen presentando
  `local-config-3` como requisito sin mencionar v4; ya estaban pendientes en el registro de T008.
- `frontend/src/Prompts.tsx:58` presenta `close-phase` y `reconcile-phase` como flujos no implementados.

Son textos activos que deben sincronizarse antes de dar por terminada la fase. Las referencias históricas en
ADR, snapshots o archivos congelados se conservan. No se propone cambiar los contratos por estos textos.

## Criterios de salida contrastados

| Criterio de ROADMAP | Evidencia y resultado |
|---|---|
| Este repositorio cumple D088, enlaces y diagramas | Documentos e instrucciones presentes, parsers y presupuestos válidos; enlaces comprobados. 35 tablas y todas sus columnas concuerdan con el diagrama. 20 diagramas válidos por parser/gramática, sin renderizado DOM. |
| Plantilla, contratos, prompts y API unificados; creación v1 retirada | Implementación y pruebas de documentos, definición, prompts y contratos; las rutas de escritura v1/transición están retiradas. Quedan los textos de H4. Los lectores y las plantillas históricas permanecen por compatibilidad. |
| Cierre READY con archivo, reinicio y commit conciliable | `test_phase_closure.py`: archivo exacto, binarios, sucesora vacía, rechazo previo y recuperación del mismo tag/commit. |
| AGENTS en el contexto congelado de cada intento | `test_project_instructions.py`: roles, hash, cambios entre intentos, rechazos antes de invocar y cuarentena. Definición/importación/onboarding redactan las instrucciones según D094/D098/D102. |
| Perfiles declarativos y Python/Django | `test_declared_profiles.py`: parser v4, compatibilidad, hash, cuarentena y recorrido con validaciones/JUnit falsos. Sin ensayo de Django real. |
| Flujos A/B hasta commit confirmado sin ejecución ni pérdida de historial | Recorridos de tres orígenes A y Django/TypeScript B con conservación, recuperación y continuidad cubiertos. **Parcial: H1–H3 impiden acreditar las garantías generales del Flujo A.** |
| Checks offline y ningún proveedor sin consentimiento | Verificación indicada abajo. Una suite verde no cubre las tres reproducciones adicionales. |

## Evidencia reproducible

[Script de reproducción](P008_REVISION_SALIDA_REPRO.py) y [salida JSON](P008_REVISION_SALIDA_EVIDENCE.json).
Desde la raíz, con las dependencias ya instaladas:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P008_REVISION_SALIDA_REPRO.py
```

El script reutiliza fixtures/helpers sintéticos de las pruebas, crea sus propias SQLite y repositorios temporales
y usa revisores falsos. El filtro de H1 es un programa sintético que solo deja el marcador de la prueba y copia
stdin; no se invoca ninguna CLI de proveedor ni herramienta de un proyecto real. El script describe los fallos:
su exit 0 no significa que se cumplan los contratos. Al corregirlos se incorporarán pruebas de regresión a la suite.

## Verificación de esta tarea

- Suite pytest completa cubierta: **1.345 pruebas y 121 subtests correctos**. La primera pasada serial se
  interrumpió deliberadamente tras 767 casos correctos (sin fallos) para repartir los 578 pendientes. Se recogieron
  los 1.345 nodeids ordenados; el primer pendiente coincide con el caso interrumpido, y se verificó que el prefijo
  ejecutado y los tres lotes no se solapan y cubren exactamente los 1.345 casos. Los lotes terminaron con exit 0:
  193, 194 y 191 OK, con 29 y 92 subtests en los dos últimos. Duraciones: 5 min 8 s, 3 min 31 s y 4 min 2 s;
  pasada inicial: 12 min 16 s. Solo el aviso conocido de deprecación Starlette/httpx.
- 12 checks ligeros con unittest, 75 pruebas Node y build del frontend, incluido `tsc --noEmit`, correctos.
  El build conserva el aviso de tamaño de chunks; no hay cambio de dependencias ni assets versionados.
- Alembic `upgrade head` y `check` sobre SQLite temporal: sin nuevas operaciones de upgrade. No se migró la base
  local del usuario ni se arrancó el servicio.
- 32 Markdown activos/raíz/phase con 363 enlaces relativos y anclas válidos; 104 decisiones sin duplicados,
  ocho fases y dieciséis tareas reconocidas por sus parsers. Instrucciones dentro de sus límites, STATE y base
  acumulada dentro de 24/12 KiB y NEXT_STEPS dentro de 48 KiB. STATE compacta T003–T005, cuyo detalle permanece
  en las entregas y ADR existentes.
- Las 35 tablas y todas sus columnas coinciden con el metadata SQLAlchemy. Siete ER y tres secuencias pasan
  `mermaid.parse` local; siete flowcharts y tres diagramas de estados pasan su gramática local. Sin DOM se omite
  la sanitización/renderizado de etiquetas de los dos últimos tipos: esto valida sintaxis, no apariencia.
- Reproducciones H1–H3 ejecutadas con la salida JSON conservada; script compilado y diff revisado sin errores de
  espacios. Ningún cambio de código del producto, esquema, API, UI, dependencias o versiones congeladas.
- Sin comprobación visual de UI, proveedores reales, smokes, push, publicación ni subagentes. El harness solo se
  ejercita en repositorios sintéticos temporales mediante sus puertos falsos; nunca sobre este repositorio.

## Continuidad

Siguiente tarea: P008-T016, corregir H1–H3 sin cambiar las reglas de D096/D100 y sin reescribir intenciones
selladas. Después deben sincronizarse los textos de H4 y repetirse la revisión de salida. El cierre, archivo y
cualquier ensayo con proveedores reales siguen requiriendo sus operaciones y autorizaciones correspondientes.
