# P009-T010 — Piloto Claude→Claude

Fecha: 2026-10-21. Base: `5ba32f8` (T020). Autorización: petición del usuario de continuar con la siguiente
tarea, dentro de D121 y de la [propuesta](P009-T006_PROPUESTA_PILOTO.md) §§3–6. Techo de T010: 7 invocaciones;
consumo previo del piloto: 18 de 60. Decisión [D136](../DECISIONS.md#d136--p009-t010-completada-claudeclaude-committed).

**Resultado:** P001-T003 COMMITTED en `882af9b`: completar/reabrir por POST y filtros por estado, con 22 tests
verdes y las seis validaciones del perfil correctas. Claude Sonnet 5.5 con esfuerzo `medium` en los tres roles;
ACCEPT a la primera. T010 consume 3 de 7 invocaciones; piloto acumulado: 21 de 60.

## 1. Preparación sin proveedores

| Comprobación | Resultado |
|---|---|
| SHA-256 de ambos binarios de §1 de la propuesta | idénticos |
| Hijo `harness-django-pilot` | limpio en `2f2b13f`; P001-T001 y P001-T002 COMMITTED |
| Wheel de `5ba32f8`, con T020 | `6845630beef31f88f7d683e2625d4cead7f80000270fd5535928260a52446980` |
| Construcción y verificación del wheel | offline; `check_distribution.py` completo con agentes sintéticos |
| Instalación | offline, sin dependencias, en el venv existente del área y con `serve` detenido |
| `check-config --preflight` | `version_help_match` en los 6 roles/presets |
| Servicio | iniciado desde el área, en 8031, con `TMPDIR=…/harness-local/tmp` |

La navegación de la extensión de Chrome fue rechazada por la guardia de origen (`origin_rejected`), como en T008.
Se pidió al usuario abrir la URL manualmente e iniciar la sesión local. No se abrió la SQLite viva desde otro proceso.

## 2. Selección y contrato desde la UI

- El usuario abrió la UI e inició sesión. Ajustes mostraba registro v2, sin trabajos pendientes ni bloqueos.
  Se cambió solo el revisor a `claude-reviewer`, modelo `claude-sonnet-5-5` y esfuerzo `medium`, como fija D121.
  La vista previa confirmó el único cambio; registro v3, hash `9570b8146238…aea35`, con motivo auditado.
  Ejecutor Claude, catálogo Sonnet/Opus y esfuerzos low/medium/high, dos correcciones y planificación `agent` intactos.
- El resumen mostró «Django preparado». El selector nuevo de T020 cargó P001-T003 desde NEXT_STEPS,
  con 847 bytes y SHA-256 `796f1839471ba9bc972ae988b3219ef2afec8092c4db8435b3bbfde373863ca8`, contrato de solo
  lectura y notas vacías. No se pegó ni editó el texto a mano.
- La planificación congeló `core/**` y `docs/flows/tasks.md`; excluyó migraciones y las rutas protegidas.
  El campo `completed` ya existía: no cambian modelos ni migraciones, ni procede cambiar el diagrama de datos.
- Había un check de fase adicional, `08f3532f`, completado antes de esta sesión y sin intentos de agentes.
  No consume invocaciones de proveedor ni afecta al techo del piloto.

## 3. Run `beaf4528`

Identificador: `beaf4528-199b-4b52-8182-b0a99533f9c1`.

| Intento | Proveedor/modelo/esfuerzo congelados | Resultado | Duración | Turnos reportados |
|---|---|---|---|---|
| 1 planificador | Claude `claude-sonnet-5-5`/`medium` (política del usuario) | COMPLETE | 22,7 s | 7 |
| 2 ejecutor | Claude `claude-sonnet-5-5`/`medium` (elección del revisor) | COMPLETE | 35,4 s | 13 |
| 3 revisor | Claude `claude-sonnet-5-5`/`medium` (política del usuario) | COMPLETE, **ACCEPT** | 9,7 s | 3 |

- **Procedencia:** los streams reportan `claude-sonnet-5-5` en los tres intentos. Con el servicio detenido se
  comprobó el argv conservado de cada proceso: `--model claude-sonnet-5-5 --effort medium`, coincidente con la
  selección congelada; sin medida independiente del esfuerzo efectivo del proveedor. El revisor elige
  Sonnet/medium para el ejecutor porque es un cambio convencional de vistas, plantilla, pruebas y flujo sobre un campo
  existente y de riesgo bajo. No hubo escalado, fallback ni correcciones.
- **Cambio:** 5 rutas de producto/documentación, 11 230 bytes de diff; SHA-256
  `a3079d2038eff85f4b80adfd919c2552865b4e443350c5196f4f108ac040e4ab`, huella aceptada
  `e2e36e3c014317e992d190f378d6ce1e9490f637c8f443c9e62102de31dd1c22`.
- **Comportamiento:** vistas `task_complete` y `task_reopen`, con `require_POST`, CSRF y 404 para inexistentes.
  Solo se actualiza `completed`. La lista filtra `pending`, `completed` o `all`; ausente o inválido equivale a
  todas. Un campo oculto conserva el filtro al completar/reabrir; la redirección usa valores normalizados.
  La plantilla muestra el estado, los botones y un mensaje vacío específico de cada filtro.
- **Pruebas:** 11 nuevas y 11 anteriores, 22 verdes: transiciones, GET sin efectos/405, inexistentes, CSRF,
  filtros, valor inválido, orden y vacíos, más regresión del CRUD. JUnit completo, hash
  `1c2faff18b43781f88af1f9281aad9ecb2b2ee7a1eb4a59c9e91af6e587069fa`.
- **Validaciones:** pytest/JUnit, `ruff check`, `ruff format --check`, mypy, `manage.py check` y
  `makemigrations --check --dry-run --noinput`, todas con salida 0. El formateador previo del harness ejecutó
  `ruff format -- core/tests.py core/urls.py core/views.py`: salida 0, los tres archivos ya estaban formateados.
- **Revisión:** ACCEPT sin hallazgos, preguntas ni concesiones, aceptación elegible. Propone documentar el uso
  de POST y el filtro normalizado, ya descritos en `docs/flows/tasks.md`; la propuesta queda en el historial,
  sin consolidarla manualmente en DECISIONS del hijo.
- **Consumo reportado por la CLI:** 23 turnos y coste equivalente agregado de 0,2995099 USD (no factura).
  Tokens agregados por categoría: entrada 20, creación de caché 51 775, lectura de caché 84 499 y salida 8 392.
  Procedencia: `observed.usage`, `num_turns`, `total_cost_usd` de cada intento; duraciones de pared del adaptador.

## 4. Commit, límites y siguiente paso

Diff revisado antes de confirmar desde la UI. Commit `882af9bdefe4fe5cd71cdf9db758a3272fc8620a`, sobre `2f2b13f`,
con huella y árbol revisados en sus trailers. El harness añade solo los bloques mecánicos de STATE y NEXT_STEPS
a las cinco rutas del ejecutor. Run COMMITTED, checkout limpio y tareas anteriores conservadas.

El mensaje automático toma el título congelado en español. Se detectó después de confirmar el commit y se consultó
al usuario, que eligió conservarlo y aplicar el inglés al commit de esta sesión en `my_harness`. No se reescribió
el commit ni su evidencia.

- Verificación del harness: wheel construido, tipos/build y `check_distribution.py` completo offline; 12 checks
  unittest, 376 enlaces/anclas relativos válidos, 136 decisiones únicas y ordenadas y `git diff --check` correcto.
  Sin repetir pytest completo, tests Node o Alembic: no cambia código ni esquema.
- QA de la UI del harness: selección/confirmación del registro, selector documental, seguimiento de intentos,
  validaciones, aceptación y confirmación de commit. La captura muestra COMMITTED y ACCEPT.
- No se lanzó `runserver` ni se hizo QA funcional del Django en navegador: corresponde a T012, con
  `PYTHONDONTWRITEBYTECODE=1`. T011, pareja Claude→Codex, sigue pendiente; no se presenta el piloto como terminado.
- Los originales de prompts, streams y SQLite siguen privados en el área; este documento solo recoge el resumen.
  Sin edición manual del hijo, configuración global, push ni publicación.
- Limpieza: sesión local cerrada, pestaña cerrada y `serve` detenido con salida 0; puertos 8031/8032 libres.
  Lectura de SQLite solo después de detener el servicio: `integrity_check` correcto, cero locks y trabajos
  pendientes, run COMMITTED y 21 intentos acumulados. Los tres grupos de agentes figuran detenidos y muertos.
- Siguiente: T011, P001-T004 (buscar por título y combinar con filtros), cambiando solo el ejecutor a Codex en
  Ajustes del mismo proyecto. Techo propio de 7; techo total de 60 intacto.
