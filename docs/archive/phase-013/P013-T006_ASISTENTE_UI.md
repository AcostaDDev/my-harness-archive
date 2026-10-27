# P013-T006 — Asistente inicial y ajustes globales en la UI

Fecha: 2026-10-26. Base: `b0995ca`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local en inglés.
**Implementada la UI global; perfiles/altas T007–T009, asistencia T010 e importación/backup T011 pendientes.**
[D223](../DECISIONS.md#d223--p013-t006-asistente-y-editor-global-con-confirmaciones-exactas),
[contrato T001](P013-T001_CONTRATO.md), [API T005](P013-T005_ASISTENTE_API.md),
[flujo actualizado](../flows/configuration-setup.md).

## Resultado y motivo

El primer arranque sin autoridad conduce a `/setup`, conservando la sesión protegida, y la navegación normal
ofrece `/settings/configuration` para editar después. Ambas rutas comparten `ConfigurationPage`; no exigen
plantilla, composición Django/TypeScript, TOML manual ni llamadas a modelos. Formularios en/es para clientes,
modelo/esfuerzo del revisor, identidad Git, raíces y límites del servicio. La selección de modelos del ejecutor
sigue siendo por proyecto. Almacenamiento fijado al arrancar: la UI muestra el elegido y explica que no mueve
la DB ni cambia puerto/instalación.

Se contrastaron D216/D217/D222 y T001/T005 con el código. No se identificaron ambigüedades de diseño que
requirieran HITL. La conversión de representación y la señal de modo concretan API para completar T005,
dentro de las rutas permitidas; no añaden autoridad, formatos, modelos ni migraciones.

## Formulario y autoridad

- `GET /api/managed/configuration` añade `form`, derivado del mismo TOML guardado y confinado al editor
  autenticado. `POST /configuration/form` convierte formulario/TOML con el parser del servidor, incluye
  el `state_dir` fijado cuando falta y conserva campos avanzados. Admite borrador incompleto con validación
  explícitamente desactivada; rechaza secretos reconocibles, claves desconocidas, versiones legacy y TOML
  inválido. No guarda, detecta ni ejecuta procesos. Sin parser TOML nuevo en el navegador.
- `SupervisorRead.configuration_mode` publica únicamente el modo global o null cuando no existe este carril.
  Consulta D040 se resuelve antes de montar editor o workspace. Modo bloqueado conduce al asistente antes
  de montar acciones de proyecto; preferencias, estadísticas y evidencias de runs por id siguen consultables.
  La consulta de run reutiliza el componente de evidencia sin workspace, decisiones ni sondeo de ejecución.
  No publica formulario, ejecutables, entorno privado o credenciales en el supervisor/listados.
- Buscar clientes requiere PATH explícito; aplicar sugerencias es otra acción y conserva argumentos/entorno
  ajenos a esas sugerencias. Comprobar clientes invoca únicamente la API version/help D174, separada del
  preview/guardado; la UI explica que no acredita inferencia ni efectos internos. Tests con transporte falso.
- Errores locales por campo con etiquetas, `aria-invalid`, descripción asociada y foco en el primer error;
  validación final, rutas/propiedad, límites y guardias de autoridad siguen en T004/T005. TOML inválido sigue
  editable tras rechazo. Valores avanzados, herramientas y permisos no representados por el formulario
  permanecen en el candidato; pueden editarse desde TOML y quedan visibles en el diff.

## Confirmación, concurrencia y recuperación

Borrador, representación elegida y base CAS se conservan en `sessionStorage` de la pestaña. Sondear no
reemplaza el candidato ni actualiza su base. Conflicto conserva cambios y exige adoptar explícitamente la
base actual, revisar otro diff y confirmar de nuevo. Cargar la guardada descartando cambios requiere elección
expresa. Cambiar representación, valores, motivo, validación o base invalida las previews y confirmaciones.

Guardar muestra diff/TOML/hash y usa el mismo candidato/base confirmados. No activa. Activar usa solo la
referencia guardada VALIDATED exacta, con preview/hash y checkbox separados; muestra impacto y necesidad de
reinicio. Trabajo pendiente sigue bloqueando en servidor. Activa/guardada/pendiente permanecen visibles;
reiniciar exige parar/arrancar por el operador, sin endpoint ni efecto de reinicio desde el editor.

Una confirmación guarda su sobre y clave idempotente antes del POST. Respuesta perdida/recarga conserva
el sobre; montaje no lo reenvía. Usuario revisa/reintenta la petición exacta con la misma clave; mientras
está pendiente se bloquean otras acciones. Rechazo definitivo permite leer/rehacer preview; no sobrescribe
autoridad ajena. Cancelación fija id/versión pendientes revisados y deja de estar confirmada si cambian.
Recuperación inspecciona hashes antes de pedir declaración de escritores detenidos; no deduce parada por
tiempo ni ejecuta un reinicio. Legacy informa de la importación explícita pendiente T011, sin editar el original.

## Validación

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: **1878 correctos y 29 subtests**,
  **dos opt-in omitidas**. Avisos conocidos de TestClient y ZIP duplicado deliberado en prueba negativa.
  Pruebas de API con SQLite/archivos
  temporales y TestClient; caso nuevo de conversión preservando campos avanzados, comillas y saltos,
  borrador, rechazo saneado y CSRF. Extensión de primer uso comprueba formulario y modo público en cada etapa.
  La primera pasada completa detectó dos expectativas de supervisor en backup pendientes del campo nuevo;
  corregidas, su regresión focalizada y la segunda suite completa pasan. Lectura de evidencia intacta.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **8 correctos**.
- `node --test frontend/tests/*.test.mjs`: **136 correctos** (17 nuevos: 16 del editor y uno de consulta
  durante bloqueo). Componentes reales renderizados con hook host y transporte sintético: en/es, errores por campo, sugerencias explícitas, preflight separado, TOML/formulario,
  invalidación de confirmación, TOML rechazado editable, sustitución confirmada tras origen inválido, borrador no activable, elección de cambio externo,
  stale CAS/rebase, respuesta perdida y recarga sin POST, replay exacto, cancelación, recuperación con parada,
  URLs, consulta antes de setup y ausencia de acciones de proyecto en evidencias durante bloqueo.
- OpenAPI exportado y TypeScript regenerado: una ruta y un esquema nuevos; cambios aditivos en
  `ConfigurationRead` y `SupervisorRead`, resto de rutas/esquemas sin cambios estructurales.
  `npm --prefix frontend run check` y `npm --prefix frontend run build`, correctos; aviso conocido de chunks
  grandes. Alembic `upgrade head` y `check` sobre SQLite temporal: sin diferencias con metadata.
- Documentación: parsers, enlaces/anclas, estados, presupuestos y conservación de decisiones anteriores
  correctos: 13 fases, ocho criterios P013, quince tareas únicas y 223 decisiones consecutivas con estado.
  Cuerpos D001–D222 intactos; Mermaid existente sin cambios. `git diff --check` correcto y diff revisado.
  Sin paridad de datos nueva: esquema sigue
  `0026_configuration`, diagrama T004 vigente.

## Alcance y omisiones

Las pruebas de componentes acreditan estructura semántica/atributos y transiciones con transporte falso;
no acreditan navegación real con teclado, tamaño, foco del navegador ni contraste visual. Se reutilizan controles
nativos, foco visible y temas del producto, con rejillas flexibles y hashes que parten línea; QA visual en/es,
anchos/temas y teclado integrada pendiente T012 según NEXT_STEPS. No se presenta como ejecutada.

Sin instalaciones reales, servicios en puertos, navegador, harness sobre este checkout, agentes/proveedores,
smokes, red, bases privadas ni configuración global del equipo. Sin wheel/candidato nuevo, snapshots ni
artefactos P001–P012/D214 modificados. Sin push, CI remota, tag ni publicación. La suite ejecuta únicamente
fixtures sintéticos y herramientas falsas conforme al contrato de pruebas. Siguiente tarea: **P013-T007**.
