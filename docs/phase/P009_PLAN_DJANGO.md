# P009 — Plan de Django desde cero

Fecha: 2026-10-19. Base: `747fc33` (P008 cerrada). Decisión:
[D115](../DECISIONS.md#d115--p009-django-desde-cero-carpeta-de-proyectos-y-agentes-por-proyecto).
**Estado:** planificación, sin implementación, configuración efectiva ni ejecución del piloto.
P009-T001 completada como diseño: [contrato](P009-T001_CONTRATO_CREACION.md) y
[D116](../DECISIONS.md#d116--p009-t001-autoridad-de-creación-presets-por-proyecto-y-preparación-separada).

## Resultado que se busca

Desde la UI, elegir dónde guardar proyectos, dar nombre a uno nuevo, definirlo y obtener un Django funcional
sin crear su carpeta, scaffold o entorno a mano. Después desarrollar cuatro funciones con parejas distintas
de agentes, conservando el mismo id, checkout, fase e historial. El usuario decide modelo/esfuerzo del revisor;
el revisor decide modelo/esfuerzo del ejecutor por tarea y revisión, como establece D052.

Proyecto propuesto: `harness-django-pilot`, pequeño gestor de tareas con SQLite y plantillas Django. Nombre y
destino definitivos se confirman antes del piloto. Sin login, REST, frontend separado, base externa o despliegue.
Los datos de prueba son sintéticos. No se utiliza este repositorio ni ReferenceProject como proyecto gestionado.

## Brechas constatadas

| Área | Implementación actual | Trabajo de P009 |
|---|---|---|
| Ubicación | `[registration].roots` procede del TOML; `canonical_root` exige carpeta de proyecto existente, canónica y autorizada. | Elegir una raíz desde la UI y crear en ella un hijo nuevo; persistencia y permisos auditados. |
| Agentes | `Settings.tsx` muestra agentes en solo lectura; el registro cambia composición/política, pero los proveedores vienen de los agentes globales del TOML. | Presets de roles seleccionables por proyecto, sin aceptar ejecutables o secretos del navegador. |
| Proyecto vacío | Definición admite documentación D088/flujos y termina en commit raíz; no crea Django ni su entorno. | Receta técnica confirmada posterior al bootstrap documental, antes de las tareas. |
| Perfil Django | Plantilla declarativa con checks; `manage.py`, dependencias y configuración están protegidos ante el ejecutor normal. | Generarlos mediante la receta y validar el perfil con herramientas reales, sin quitar esas protecciones. |
| Evidencia real | D071 verificó las cuatro parejas en un fixture anterior; P008 está validada offline. | Proyecto Django completo con cuatro tareas sucesivas, UI y cierre de fase reales. |

La selección de carpeta y los ajustes por proyecto amplían D049/D078; no se presentan como capacidades ya
existentes. T001 concreta persistencia, contratos y compatibilidad en el diseño enlazado, antes de modificar
código o migraciones en T002–T004.

## Carpeta de proyectos y autoridad

- Nueva sección de UI «Carpeta de proyectos / Elegir carpeta». La persona selecciona o introduce una carpeta
  existente y el servidor muestra su ruta canónica. No se examina HOME, cwd u otros repositorios para adivinarla.
  El ejemplo `$HOME/Documents/projects/` pertenece al usuario; no se codifica como valor por defecto.
- Guardar la elección concede al servicio crear nuevos proyectos hijos y persiste entre reinicios. El formulario
  pide nombre, muestra destino completo y crea el hijo sin repetir el permiso de carpeta. No se cambian permisos
  del sistema operativo ni se obtiene acceso si el proceso del servicio no lo tiene.
- El servicio controla la creación; la IA solo recibe la raíz del hijo. No se entrega el padre como raíz escribible
  ni se confía automáticamente en proyectos existentes. Destino existente, escape, enlace, raíz revocada o conflicto
  bloquean antes de efectos. No se reutiliza una carpeta vacía ajena ni se sobrescribe su contenido.
- Persistencia operativa auditada, sin editar el TOML/globales. D116 define convivencia con raíces del TOML,
  precedencia y retirada: no ampliar autoridades antiguas de manera implícita. Retirar una raíz impide nuevas
  creaciones y no borra hijos; los registros y jobs pendientes siguen reglas explícitas de autoridad/versiones.
- Elegir carpeta no concede llamadas a modelos, red o instalaciones. Esas operaciones se presentan juntas en el
  plan de creación/receta con comandos y límites; se reutiliza el consentimiento vigente para el mismo alcance.
  Definición, commits y cierre conservan sus confirmaciones de contenido existentes, sin permisos redundantes.

## De cero a Django

Orden previsto: elegir raíz → crear/registrar hijo inexistente → definición D088 y commit raíz → receta técnica
confirmada con commit propio → tareas del proyecto. La receta no se disfraza como borrador documental ni hace
pasar un repositorio ya preparado por una creación desde cero.

La receta controla scaffold, entorno, dependencias fijadas y configuración: Django, pytest-django, ruff, mypy
y los stubs que se necesiten. T004 concretará comandos/versiones dentro del contrato T001 y las dependencias de pruebas
sin añadir Django al runtime del harness. Instalación offline desde cache cuando sea posible; cualquier red
necesaria debe figurar en el plan autorizado. SQLite local, entorno, caches, reportes y secretos quedan ignorados.

Se conserva la protección normal de `manage.py`, `pyproject.toml`, locks y ajustes de herramientas. Solo la
operación de preparación confirmada los crea; las tareas de negocio trabajan en modelos, migraciones, vistas,
formularios, plantillas y tests con sus diagramas. `startproject`, `startapp` y aplicar migraciones no equivalen
a las validaciones actuales del perfil, por lo que necesitan la autorización exacta de esa operación.

Crear carpeta, registrar, preparar entorno/escribir archivos y hacer commit requieren intención previa,
idempotencia, comprobación de autoridad y recuperación. Repetir no crea otro proyecto ni destruye bytes ajenos.
Una caída con efecto incierto se concilia; no se borra ni reinstala a ciegas para hacer pasar el recorrido.

## Matriz del mismo proyecto

Flecha: **revisor→ejecutor**. Las tareas P009 son trabajo del harness/piloto; P001-T001–T004 son las tareas
gestionadas de la primera fase del Django hijo. No se crean cuatro proyectos o clones independientes.

| Tarea de P009 | Tarea del Django | Revisor | Ejecutor | Incremento |
|---|---|---|---|---|
| T008 | P001-T001 | Codex | Codex | Modelo Task, migración, alta y listado. |
| T009 | P001-T002 | Codex | Claude | Edición y borrado confirmado. |
| T010 | P001-T003 | Claude | Claude | Completar/reabrir y filtrar por estado. |
| T011 | P001-T004 | Claude | Codex | Búsqueda por título y regresión integrada. |

Antes de cada tarea, el usuario configura los proveedores y modelo/esfuerzo del revisor en Ajustes del mismo
proyecto. El catálogo del ejecutor limita lo admisible, pero el revisor decide modelo/esfuerzo concretos y motivo.
Los modelos/esfuerzos de los revisores no se fijan en este plan: el usuario los elegirá en T006 según los presets
disponibles. Los del ejecutor los elegirá el revisor al planificar y revisar cada tarea.
El piloto usa planificación por agente, no el contrato determinista que omitiría esa decisión del revisor.

El cambio se hace tras COMMITTED y sin jobs pendientes. Congelar versiones/política/selecciones por run y
preservar intentos anteriores. Una selección inválida o un preset ausente falla con diagnóstico, sin fallback.
La UI no escribe en archivos de autenticación, proveedores, ejecutables o configuración global.

## Puertas de ejecución y evidencia

1. T001: diseño. T002–T004: producto. T005: ensayo offline con agentes falsos y herramientas Django reales
   en un entorno temporal preparado/autorizado. Corregir fallos antes de pasar a proveedores reales.
2. T006: propuesta concreta y consentimiento. Elegir carpeta/nombre, modelos/esfuerzos de los revisores,
   catálogos del ejecutor, versiones, dependencias/red, puertos, límites de llamadas/tiempo/correcciones y parada.
   Preparar paquete/venv de uso real fuera del checkout del harness (D051).
3. T007–T011: creación y cuatro tareas desde el producto instalado. No editar manualmente el Django para
   completar lo que debería hacer el flujo. Un fallo de proveedor, entorno o permisos detiene el recorrido;
   corregir no da autorización implícita a repetir consumo o ampliar alcance.
4. T012: QA del Django en navegador, comprobaciones finales y cierre READY/archivo de P001 del hijo; revisión
   de salida del harness. Cerrar/archivar P009 será una tarea posterior a ese dictamen.

Evidencia por tarea: configuración elegida por el usuario, contrato/selección del revisor, proveedor/modelo/
esfuerzo realmente invocados y su procedencia, comandos/resultados/JUnit, diff aceptado y commit; métricas de
consumo/duración/intervenciones con ausencias explícitas. Las tareas son diferentes: el piloto demuestra
interoperabilidad y continuidad, no una comparación estadística de calidad o velocidad entre modelos.

Historiales/streams y configuración real se guardan en el estado privado de operación. En este repositorio solo
resúmenes saneados y referencias/hashes no sensibles; nunca runs privados, credenciales o datos de otros proyectos.

## Comprobación de esta planificación

- 12 checks ligeros unittest correctos; parsers: 115 decisiones, nueve fases y doce tareas P009, en orden.
- Instrucciones/bloques/presupuestos correctos: STATE 6.339 bytes, base 4.108 y NEXT_STEPS 19.835.
- 48 Markdown activos y del archivo P008: 518 enlaces relativos/anclas válidos; los 161 enlaces de snapshots
  archivados se comprueban desde su contexto original, sin modificar sus bytes.
- 21 diagramas aceptados por Mermaid: siete ER y tres secuencias por `mermaid.parse`, ocho flowcharts por
  su parser sin sanitización de etiquetas y tres estados por su gramática sin extracción dependiente del DOM.
  Comprobación de sintaxis, sin renderizado. Diff revisado y `git diff --check` correcto.
- Sin repetir pytest completo, Node/build o Alembic: solo cambia documentación; no cambian código, esquema,
  API, tipos, versiones ni configuración. Ninguna carpeta externa, instalación, servicio o proveedor iniciado.
