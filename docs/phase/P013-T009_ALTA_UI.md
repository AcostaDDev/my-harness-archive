# P013-T009 — Activación del perfil y alta completa desde la UI

Fecha: 2026-10-26. Base: `7de0111`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local en inglés.
Implementadas ambas entradas con perfil propio: documentos → propuesta → commit documental → TOML privado →
preparación/recibo → activación → admisión de primera tarea. **Verificación sintética; QA visual instalada T012 pendiente.**
[D226](../DECISIONS.md#d226--p013-t009-alta-documental-y-activación-del-perfil-propio),
[contrato §7–§9](P013-T001_CONTRATO.md#7-dos-entradas-commits-y-perfil-preparado),
[flujo](../flows/configuration-setup.md#alta-y-activación-entregadas-en-t009),
[paridad de datos](../DDBB-DIAGRAM.md#alta-y-activación-de-perfil-p013-t009).

## Resultado y motivo

T007 proponía y T008 preparaba, pero el alta seguía detenida: faltaban creación de carpeta sin perfil, commit
con perfil aceptado, guardado del TOML, activación/runtime y UI. T009 conecta esas piezas con las puertas
D218/D221/D224/D225. No se exige declarar Django/TypeScript antes de conocer requisitos/arquitectura.

Crear reutiliza padre autorizado, reserva, intención, identidad y recuperación existentes, con composición/perfil
null. Incorporar B conserva inventario/HEAD, lectura de objetos locales, borradores privados, originales y
phase-000. Perfil aceptado vigente obligatorio antes de commit raíz/B; preview sella `profile_proposal_sha256`.
El perfil real aceptado se presta solo al render documental; autoridad/run siguen siendo `IntakeContext` sin
runner. No se admite una tarea por tener P001 ACTIVE ni por haber guardado una propuesta.

El handoff B usa el `preview.result_tree` sellado para comprobar los hashes documentales. Su resultado de
importación nunca tuvo el campo `documents` del bootstrap: se conserva esa forma histórica y no se reescribe
ningún resultado para acomodar el consumidor de preparación. Código/originales y guardias Git permanecen.

`ProjectConfiguration` deriva `project-config-1` de propuesta/global/registro efectivos; usuario completa rutas
de herramientas, entorno y límites/autorizaciones. Identidad, hash de perfil/procedencia y pareja/política se
validan: un perfil que contradiga los documentos exige otro turno/edición documental confirmado. Aplicación
guarda bytes privados por CAS/intención/fsync T004 fuera del checkout. Guardar no prepara ni activa.

Activación tiene preview/diff/impacto/evidencia y confirmación independientes. Exige saved VALIDATED exacta,
global compatible, recibo T008 exacto, documentos/herramientas/entorno íntegros, HEAD técnico limpio y barrera
D118 sin trabajo/locks inciertos. Precompone antes de publicar; instala la referencia verificada sin reinicio.
Si falla instalar después de publicar, la admisión permanece cerrada hasta resolución/reinicio/replay verificados;
no repite alta, preparación o commits. Primera tarea se admite con el perfil preparado y sus referencias congeladas.

Arranque y resolución recuperan la activa por revisión/hash y recibo exactos. Otra versión guardada conserva la
activa anterior; no se confunde el candidato más reciente con autoridad. El runner comprueba recibo y las nuevas
admisiones comprueban copia/inmutable; el escritor propio verifica autoridad inmutable antes de efectos. Una
edición de copia no inyecta valores al job ya admitido. Formatos/hashes 1–8, recetas, historiales y snapshots intactos.

## UI y contrato API

`ProfileProposal`/`ProjectProfile` comparten definición y B, y el proyecto muestra progreso después del commit.
Preguntas/documentos siguen el editor existente. Perfil editable por campos, formulario completo y TOML; ejemplos
del catálogo seleccionables como copia propia, sin referencia mutable. Cambiar candidato invalida preview.
Edición manual versiona otra propuesta con evidencia/documentos/contexto vigentes y exige nueva adopción;
conserva bytes del revisor y confirmaciones/replay anteriores. Copiar un stack incompatible no acredita evidencia.

Editor de configuración muestra rutas/entorno, TOML, diff, referencias guardada/activa y restricciones. Preparación
comparte plan/pasos/journal/recibo, cancelación y confirm-stopped/reintento enlazado T008, ahora accesibles desde
las dos altas. Confirmar plan requiere motivo y no activa. Activación exacta separada habilita la primera tarea.
Estado y textos en/es, controles nativos de teclado. Se conservan campos avanzados sin exigir editor de archivos.

Borrador/formulario/TOML/base CAS permanecen en la pestaña ante conflicto/recarga. Respuesta perdida conserva
sobre y clave para reenvío explícito; sondeo/recarga nunca envían POST. Reenvío exacto no duplica perfil,
preparación, alta ni commits; misma clave con contenido distinto rechaza. Restricciones de sesión, Host/Origin,
CSRF y consulta restaurada se mantienen; contenido privado solo en editor autenticado. Sin proveedores en GET/
parse/preview/guardado/activación; preparación solo tras su confirmación propia.

API por proyecto: `/configuration`, `/configuration/form`, `/configuration/preview`, `/configuration/save`,
`/configuration/activation/preview`, `/configuration/activate`; planificación añade `/profile/form` y
`/profile/edit`; `/profile-templates/{name}` entrega copia de catálogo. Rutas de propuesta, documentos y
preparación conservan contratos anteriores. OpenAPI/tipos regenerados; estados intermedios y creación con perfil
null reflejados en DTO. Sin dependencias, tablas, modelos ni migraciones nuevas: `0027_profile_proposals`, 54 tablas.

## Validación

- Regresión inicial ampliada: **192 pytest correctos**, incluyendo 18 recorridos de integración T009 y las
  suites de propuesta/preparación/creación/configuración. Cuatro workers, archivos/Git/SQLite temporales.
- Regresión final de integración T009: **24 correctos**. Ambas entradas completas por HTTP, Go ajeno a los
  ejemplos, commit documental/P001 reales, guardado, preparación con ejecutor/herramienta falsos, recibo,
  activación, primera tarea QUEUED y reinicio sin consumidor. Reenvío de carpeta/documentos/configuración/
  preparación/activación; edición versionada y preservación de bytes; bloqueos ante HEAD/documentos/herramientas,
  ámbito ajeno, copia externa, perfil/política alterados y claves incompatibles. Guardar otro candidato conserva
  activa anterior; job propio verifica inmutable sin adoptar copia externa; CSRF/Origin y DTO estrictos.
- Pruebas UI en/es con React y transporte sintético: confirmaciones separadas, perfil/diff/evidencia, respuesta
  perdida con sobre exacto y reenvío explícito, conflicto con candidato conservado y ausencia de efectos implícitos.
- Suite general `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 4`: **1982 correctos y
  29 subtests**, **dos opt-in omitidas**, sin fallos. La primera ejecución dio 1973 correctos/29 subtests y
  un fallo: el nuevo handoff indexaba `conversation_id` antes de rechazar el cuerpo v1. Se restituyó su
  diagnóstico ValueError; la suite general posterior verifica el arreglo. Avisos conocidos de TestClient y
  ZIP duplicado deliberado, sin proveedores reales.
- La suite general precede a los últimos ajustes acotados del diff derivado de activación y exposición del
  hash de propuesta en el DTO B. **85 regresiones correctas** sobre configuración/definición tras el diff;
  **26 correctas finales** sobre ambas altas después del DTO, incluido formulario/TOML incompleto rechazado,
  conversión íntegra y hash de propuesta visible. No se atribuyen esas comprobaciones al paquete P012 ni a
  una ejecución instalada nueva.
- **146 Node y 8 unittest correctos**. Nueve casos propios de UI: separación de guardado/activación en/es,
  sobre exacto/replay, conflicto, adopción sin efectos, bindings, TOML/base conservados y puerta de tareas en
  su página individual antes/después de activar. La expectativa anterior de v9 desconocido en el selector de
  presets se actualizó para verificar soporte v5–v9 y conservar el fallback de formatos antiguos/desconocidos.
- Tipos y build correctos sobre el frontend final, con aviso conocido de chunks grandes. OpenAPI coincide
  con `create_app().openapi()`; tipos regenerados. Alembic `upgrade head` y `check` en SQLite temporal: sin
  diferencias, **54 tablas** de producto. Sin modelo/migración ni dependencia nueva.
- Checker [reproducible](P013-T009_CHECK_DOCS.py): **13 fases, 15 tareas, 226 decisiones, 887 enlaces/anclas
  en 14 documentos**, presupuestos D088 correctos y cuerpos D001–D225 intactos respecto de la base `7de0111`. Mermaid de
  configuración/datos: **tres flowcharts, dos secuencias y trece ER**, cero errores con el checker archivado
  citado en T001. Solo parseo con stub DOMPurify, sin renderizado ni QA visual. `git diff --check` y revisión
  del diff correctos; `docs/archive/` y `docs/public/` sin cambios.

## Límites y siguiente tarea

No se lanzan proveedores/modelos, descargas, servicios instalados, navegador/QA visual, smokes ni harness sobre
este repositorio. Primera tarea solo QUEUED en el recorrido nuevo: no se acredita una nueva ejecución real de
proveedor. La contención cooperativa de T008 no se convierte en sandbox. Datos sintéticos, sin bases privadas,
saldos/consentimientos anteriores, configuración global del equipo ni red/CI remota. Sin wheel/candidato nuevo,
push, tag ni publicación. Baseline pública y archivos/snapshots/candidatos P001–P012/D214 intactos.

No quedaron contradicciones de diseño que exigieran HITL; se concretó el contrato ya acordado. T010 cubre edición
posterior manual/asistida y sus impactos; T011, importación/compatibilidad/backup/recuperación integrada; T012,
primer uso instalado y QA visual. Siguiente tarea: **P013-T010**.
