# P009-T011 — Piloto Claude→Codex

Fecha: 2026-10-21. Base: `c5539fd`. Autorización: petición del usuario de continuar con la siguiente tarea,
dentro de D121 y de la [propuesta](P009-T006_PROPUESTA_PILOTO.md) §§3–6. Techo propio: 7 invocaciones;
consumo previo del piloto: 21 de 60. Decisión [D137](../DECISIONS.md#d137--p009-t011-completada-claudecodex-committed).

**Resultado:** P001-T004 COMMITTED en `a2de6ad`: búsqueda por título combinable con filtros, 27 tests y las seis
validaciones correctas. Claude `claude-sonnet-5-5`/`medium` planifica y revisa; elige Codex `gpt-6-luna`/`medium`
como ejecutor. ACCEPT a la primera. T011 consume 3 de 7; piloto acumulado: 24 de 60.

## 1. Preparación y selección desde la UI

- Checkout del harness limpio en `c5539fd`; hijo limpio en `882af9b`, con las tres tareas anteriores COMMITTED.
  Se reutiliza el wheel instalado de `5ba32f8` (T020), ya verificado en T010; no se construye ni instala otro.
- SHA-256 de ambas CLI idénticos a la propuesta §1. `check-config --preflight` devuelve `version_help_match`
  en los seis roles/presets. Servicio iniciado desde el área autorizada en 8031, con TMPDIR privado del área.
  Sesión local iniciada desde la UI. No se abre la SQLite con otro proceso mientras corre `serve`.
- Ajustes: registro v3 sin trabajos pendientes ni bloqueos. Se cambia solo el ejecutor a `codex-executor`,
  catálogo `gpt-6-luna` × {low, medium, high}; revisor Sonnet/medium, dos correcciones y planificación `agent`
  intactos. Vista previa revisada y confirmada; registro v4, SHA-256
  `6bc75b343f00b3bc7779c955b208cba4e933cac0187f731246af6ce21c9dbecb`, con motivo auditado.
- «Django preparado». Selector documental P001-T004: 1455 bytes, SHA-256
  `4e2034996e5aca5e90306cfca84a43e71adf9822ac493510dc64b02168946912`. La última sección incluye el bloque
  gestionado final, tal como lo devuelve el producto. No se modifica el contrato fuente.
- Se añaden notas para cumplir la petición de commits en inglés: el planificador debe usar el título
  `Search tasks by title`, del que deriva el mensaje determinista. Las notas quedan congeladas y el planificador
  respeta ese título, sin ampliar rutas ni permisos. Segundo uso real del selector; primer uso de sus notas.

## 2. Run y procedencia

Run: `6bb55757-6a17-4d29-b7fc-50ae46ba00d5`.

| Intento | Selección congelada | Resultado | Duración de pared |
|---|---|---|---|
| 1 planificador | Claude `claude-sonnet-5-5`/`medium`, política del usuario | COMPLETE | 22,5 s |
| 2 ejecutor | Codex `gpt-6-luna`/`medium`, elección del revisor | COMPLETE | 59,9 s |
| 3 revisor | Claude `claude-sonnet-5-5`/`medium`, política del usuario | COMPLETE, ACCEPT | 12,5 s |

El revisor justifica Luna/medium por ser un cambio acotado en vistas, plantilla, pruebas y flujo sobre el filtro
existente, de riesgo bajo-medio y sin cambios de modelo. El argv conservado, comprobado con el servicio detenido,
coincide: Claude con `--model claude-sonnet-5-5 --effort medium`; Codex con `--model gpt-6-luna` y
`model_reasoning_effort="medium"`, workspace-write y red desactivada. Los streams de Claude reportan Sonnet;
el de Codex no reporta modelo independiente (`reported_models = null`). No se presenta el argv como medida del
modelo/esfuerzo efectivo del proveedor. Sin fallback, escalado, correcciones, preguntas ni concesiones.

| CLI | Entrada | Lectura caché | Creación caché | Salida | Razonamiento | Turnos normalizados | Coste reportado USD |
|---|---|---|---|---|---|---|---|
| Claude planificador | 6 | 13 163 | 5267 | 3016 | 63 | 3 | 0,0525563 |
| Codex ejecutor | 436 122 | 405 760 | 0 | 4472 | 450 | 34 | ausente |
| Claude revisor | 6 | 30 705 | 21 955 | 975 | 283 | 3 | 0,1006525 |

Procedencia: `attempt_metrics`, `observed.usage` y duraciones del adaptador. Semánticas distintas de entrada y
turnos entre CLI; no se agregan como si fueran equivalentes ni permiten clasificar modelos. Coste equivalente
reportado de Claude: 0,1532088 USD, no factura ni coste total del run; falta el de Codex.

## 3. Contenido, validación y commit

- Cuatro rutas: vista, plantilla, pruebas y `docs/flows/tasks.md`. `q` mediante GET, espacios extremos recortados,
  búsqueda parcial con `title__icontains` combinada con `status`. ORM y autoescape; enlaces con query codificada.
  Formulario y filtros conservan la búsqueda, también al completar/reabrir. Mensaje legible sin coincidencias.
- Cinco tests nuevos, 27 totales: mayúsculas y espacios, combinación con los tres estados, HTML escapado,
  ausencia de resultados e integración alta→edición→completar→borrado, más regresiones anteriores.
  JUnit completo, SHA-256 `f853aaa9f4c463a1900ba43dc12f71a010bd57527dabfbddb3e6d77a6bbb9c3e`.
- Las seis validaciones terminan con salida 0: pytest/JUnit, Ruff lint, Ruff formato, mypy, check Django y
  comprobación de migraciones. El harness ejecuta `ruff format -- core/tests.py core/views.py`: ambos sin cambios.
  Sin cambios de modelos/migraciones; no procede actualizar el diagrama de datos.
- Diff revisado: 8789 bytes, SHA-256 `f47a40fddf54ace58199ff642d8f3c051cb50bb5fce1decbd53ece9390e9d9f6`;
  huella aceptada `7ed6c7a5db017417fb72023bb4b447b99cd5bbc699a15603e997cb964c9a4765`.
  Revisor ACCEPT sin hallazgos y aceptación elegible. Propuesta de decisión sobre `q` conservada en el historial;
  no se escribe DECISIONS del hijo a mano.
- Confirmación desde la UI, commit `a2de6ada6a6fe283f946801585a94594686c2c8b`, mensaje
  `harness: accept P001-T004 - Search tasks by title`. Bloques mecánicos añadidos en STATE y NEXT_STEPS del hijo.
  Run COMMITTED, checkout limpio e historial anterior conservado.

## 4. Verificaciones, límites y siguiente tarea

- UI del harness: cambio de registro, selector y notas, seguimiento, validaciones, ACCEPT y COMMITTED verificados.
  No se lanza runserver: QA funcional del Django, incluida búsqueda, corresponde a T012 con
  `PYTHONDONTWRITEBYTECODE=1`. Las cuatro parejas ya tienen tareas COMMITTED; el piloto aún no está cerrado.
- Observación documental para revisar en T012: el Mermaid de `tasks.md` reutiliza `R` para el botón Reabrir y
  para «¿Hay resultados?». La prosa y el comportamiento están descritos, pero el diagrama mezcla ambos nodos.
  Se conserva el commit aceptado; cualquier corrección del hijo sigue el flujo gestionado.
- Harness: 12 checks unittest correctos, enlaces/anclas de los documentos modificados y orden/unicidad de las
  decisiones comprobados; diff revisado y `git diff --check` correcto. Sin repetir pytest completo, Node,
  tipos/build, Alembic o wheel: esta entrega del harness solo cambia documentación.
- Servicio detenido con salida 0 y sesión cerrada. Puertos 8031/8032 libres. SQLite leída solo después de parar:
  `integrity_check = ok`, cero locks y trabajos pendientes, 24 intentos acumulados. Los tres grupos de procesos
  de T011 figuran STOPPED y se comprueban muertos. Originales privados; sin fixtures derivados, cambios globales,
  edición manual del hijo, push ni publicación.
- Siguiente: T012, QA conjunto y check/cierre/archivo de P001 del hijo con revisor Claude Sonnet/medium,
  techo de 2 invocaciones. No incluye planificar otra fase ni cerrar P009 del harness.
