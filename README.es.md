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
paquete declara `0.1.0` y no está en PyPI. Solo se ha probado en macOS sobre Apple silicon (ARM64). Los pasos de
primer uso se han contrastado con los scripts y la CLI, pero aún no se han ensayado de principio a fin desde un
clon limpio. Licencia [MIT](LICENSE). Detalle en [Status](README.md#status) y
[Supported scope and limits](README.md#supported-scope-and-limits).

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

## Seguridad, operación y contribución

- La contención es cooperativa, no un aislamiento del sistema operativo: registra solo repositorios y herramientas de
  confianza ([Safety model](README.md#safety-model)). Para vulnerabilidades, [SECURITY.md](SECURITY.md).
- Reinicio, actualización con `migrate`, backups, diagnóstico y desinstalación conservando los datos:
  [Operation](README.md#operation).
- Para contribuir: [CONTRIBUTING.md](CONTRIBUTING.md), las instrucciones para agentes en [AGENTS.md](AGENTS.md), el
  [roadmap](docs/ROADMAP.md) y las [decisiones](docs/DECISIONS.md).
