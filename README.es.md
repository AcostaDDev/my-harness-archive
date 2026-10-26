# Harness Local (español)

Harness Local es una aplicación local que ejecuta un harness de desarrollo con agentes de IA sobre tus propios
repositorios Git. Un agente **revisor** planifica y revisa en solo lectura; un agente **ejecutor** es el único que
escribe. El harness valida cada cambio con los comandos de tu proyecto, liga la revisión al contenido exacto y hace él
mismo el commit. El trabajo se organiza en fases y tareas acotadas, con documentación del proyecto, chat, métricas y
recuperación tras caídas. Todo corre en tu máquina: el servicio solo escucha en `127.0.0.1` y los modelos se usan a
través de las CLI oficiales de Codex y Claude Code con tu propia cuenta.

La documentación de referencia está en inglés: el [README](README.md) explica la instalación, la configuración, el
primer uso y la operación paso a paso. Esta página resume lo esencial y enlaza cada apartado.

## Estado

Versión previa a la primera publicación: la primera versión local está completa en el alcance declarado, el
paquete declara `0.1.0`, candidata a primera versión pública, y no está en PyPI ([changelog](CHANGELOG.md)).
Solo se ha probado en macOS sobre Apple silicon (ARM64). Los pasos de primer uso se han ensayado desde un clon limpio
con cachés vacías hasta COMMITTED y una fase cerrada, con CLI falsas: sin inicio de sesión ni llamadas reales a
modelos. La interfaz instalada se revisó después en Chrome en inglés y español, temas claro y oscuro, escritorio y
móvil; no se han probado otros navegadores ni lectores de pantalla. Licencia [MIT](LICENSE). Detalle en
[Status](README.md#status) y [Supported scope and limits](README.md#supported-scope-and-limits).

## Dos formas de empezar un proyecto

- **Crear un proyecto nuevo desde cero**: eliges en la interfaz una carpeta de proyectos, das nombre al proyecto y
  conversas con el revisor a partir de un brief; aceptas los documentos y el harness hace el commit raíz. Con una
  receta (Django o TypeScript web), una preparación confirmada crea después el entorno y el andamiaje técnico.
- **Incorporar un repositorio existente sin harness**: registras un checkout Git con al menos un commit y sin
  documentos de harness; el harness inventaría su árbol sin ejecutar código, el revisor redacta la documentación y
  una propuesta de perfil, y tú confirmas el commit documental que adopta la fase `P001`.

[Más detalle](README.md#two-ways-to-start-a-project).

## Instalación y primer uso, en resumen

1. Requisitos ([Requirements](README.md#requirements)): Python 3.14 para el servicio; uv 0.12.19, Node 24.15.0 y npm
   11.12.1 exactos para construir; Codex ≥ 0.163.0 o Claude Code ≥ 2.1.304 con tu sesión iniciada.
2. Primera descarga de dependencias (necesita red) y construcción del paquete, sin red
   ([Install from a clone](README.md#install-from-a-clone)). El uso real se hace siempre desde el paquete instalado
   en su propio entorno virtual, nunca desde el checkout de desarrollo.
3. Configuración: copia [el ejemplo mínimo de un proveedor](examples/local_config.minimal.example.toml) fuera de todo
   checkout, con `chmod 600`, y sustituye sus marcadores ([Configure](README.md#configure)).
4. `init-db`, `serve` y el navegador en `http://127.0.0.1:8013` con la clave de acceso que anuncia el arranque
   ([First run](README.md#first-run)). Con `supervisor = true` cada intento de un agente usa tu cuenta del proveedor.

## Idiomas

Dos ajustes, ambos en inglés o español:

- **Idioma de la interfaz**: global y modificable en cualquier momento desde Preferencias. Rige la interfaz, los
  mensajes del servicio y de la CLI, la conversación con los agentes, sus respuestas y sus preguntas.
- **Idioma de trabajo**: se elige por proyecto al crearlo o incorporarlo (inicializado con el valor global por
  defecto) y después no cambia. Rige la documentación, los planes, las decisiones, el código y los comentarios.

Ejemplo: interfaz en español e idioma de trabajo inglés. Conversas con el revisor en español y lees sus preguntas en
español, mientras que todo lo técnico del proyecto se escribe en inglés, tanto con Codex como con Claude Code. Cada
tarea congela ambos idiomas al encolarse; cambiar después la interfaz solo afecta a las interacciones nuevas.
[Más detalle](README.md#languages).

## Alcance soportado y límites

| Capacidad | Offline (datos sintéticos y agentes falsos) | Con proveedores reales |
|---|---|---|
| Plan → ejecución → validación → revisión → commit, fases, cierre y archivo | Sí | Adaptador actual: tareas Django y TypeScript COMMITTED; fase TypeScript READY, cerrada y archivada |
| Revisor y ejecutor Codex o Claude Code, en las cuatro combinaciones | Sí | Las cuatro antes de `cli-14`; con el actual solo revisor Claude → ejecutor Codex |
| Proyecto Django nuevo con receta | Sí | Creación, cuatro tareas y cierre históricos en macOS ARM64/Python 3.13; creación v2 solo offline |
| Proyecto TypeScript web nuevo con receta | Sí, también con node/npm reales y caché local | v2 e idioma de trabajo español: definición, preparación offline, una tarea COMMITTED y cierre |
| Recetas v2 según el idioma de trabajo | Sí, con herramientas sintéticas | Solo TypeScript v2 en español; sin creación Django v2 real ni matriz completa de idiomas |
| Perfiles declarados e incorporación de repositorios existentes | Sí | Dos Django sintéticos incorporados con originales intactos; clon documental COMMITTED con perfil v8, seis validaciones/13 casos JUnit y formateador nativo (dos archivos sin cambios) |
| Chat, backup y restauración | Sí | Dos respuestas reales, comando determinista sin modelo y propuesta confirmada QUEUED sin ejecutar; consulta API/UI Chrome de runs, diff, JUnit y métricas restaurados |
| Vistas de runs, métricas y vista previa de exportación con historiales grandes | Sí | Vistas/métricas reales restauradas comprobadas; historiales grandes y vista previa de exportación solo sintéticos |

Evidencia del adaptador actual: octubre de 2026, macOS ARM64, revisor Claude Code **2.1.310** y ejecutor Codex
**0.164.0**, wheels instalados y proyectos sintéticos desechables. Las cuatro combinaciones y la receta Django
históricas usaron Codex 0.162.1/0.163.0 y Claude Code 2.1.295–2.1.304 antes de `cli-14`. No acredita otras
parejas, versiones, plataformas o proyectos de producción, ni compara modelos o prueba efectos internos de las CLI.
Se mantienen los mínimos y la compatibilidad condicionada. Dos tareas acabaron en REVISION_LIMIT y dos checks
TypeScript fallaron antes de una edición documental autorizada y un READY válido; sus resultados se conservaron.
La propuesta del chat sigue QUEUED y la identidad de procesos históricos sigue siendo incierta.

`local-config-8` permite formateador optativo en perfiles declarados y conserva presets/recetas v2; v1–v7 mantienen
sus reglas. La restauración ofrece consulta por id en `/runs/:id` sin proyecto ni checkout, con diff/JUnit/métricas,
sin supervisor ni agentes y con mutaciones rechazadas (409). Consultar no certifica la parada de escritores históricos.
Persisten la contención cooperativa sin aislamiento del sistema operativo, los manifiestos de receta fijos tras
preparar y las validaciones sin hora. Detalle y límites restantes en
[Supported scope and limits](README.md#supported-scope-and-limits) y [STATE](docs/STATE.md).

## Seguridad, operación y contribución

- La contención es cooperativa, no un aislamiento del sistema operativo: registra solo repositorios y herramientas de
  confianza ([Safety model](README.md#safety-model)). Para vulnerabilidades, [SECURITY.md](SECURITY.md).
- Reinicio, actualización con `migrate`, backups, diagnóstico y desinstalación conservando los datos:
  [Operation](README.md#operation).
- Para contribuir: [CONTRIBUTING.md](CONTRIBUTING.md), las instrucciones para agentes en [AGENTS.md](AGENTS.md), el
  [roadmap](docs/ROADMAP.md) y las [decisiones](docs/DECISIONS.md). La documentación técnica, en inglés:
  [especificación](docs/SPECIFICATION.md), [arquitectura](docs/ARCHITECTURE.md),
  [modelo de datos](docs/DDBB-DIAGRAM.md) y [flujos](docs/flows/task-run.md).
