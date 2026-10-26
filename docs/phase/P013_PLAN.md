# P013 — Instalación guiada y configuración desde la UI

Estado: fase activa el 2026-10-26; T001 diseñada, T002–T004 implementadas; producto restante pendiente T005–T011.
Decisión: [D215](../DECISIONS.md#d215--p013-instalación-guiada-y-configuración-desde-la-ui).
Objetivo y salida en [ROADMAP](../ROADMAP.md#p013--instalación-guiada-y-configuración-desde-la-ui);
tareas ejecutables en [NEXT_STEPS](../NEXT_STEPS.md).

## 1. Problema y resultado buscado

El README de `my_harness_dist` mezcla preparación del entorno de desarrollo, construcción/verificación del
paquete e instalación para uso normal. El usuario debe repetir variables de caché y rutas absolutas, entender
dos entornos virtuales y completar a mano un TOML antes de crear o incorporar un proyecto. Los perfiles y
composiciones se declaran antes de conversar sobre su documentación, aunque ese contexto es necesario para
elegir herramientas y validaciones adecuadas.

P013 debe permitir instalar y arrancar con scripts, completar la configuración global en la UI y generar,
comprobar, editar y activar un perfil propio por proyecto con ayuda del revisor y del ejecutor. Django y
TypeScript siguen disponibles como ejemplos/recetas opcionales, sin convertirse en requisito para otros stacks.
El TOML persiste como archivo local editable; conocer su sintaxis no será requisito para el recorrido guiado.

Esta apertura define trabajo, no acredita funcionalidades nuevas. El producto actual sigue usando
`local-config-8` y composiciones del TOML hasta que las tareas correspondientes cambien esos contratos.

## 2. Alcance acordado

- **Instalación y arranque:** entradas propuestas `scripts/install` y `scripts/start`, con opciones documentadas.
  El instalador crea el venv y elige rutas; el arranque usa el paquete instalado fuera del checkout. Conservar
  `scripts/dev` para desarrollo. Primera preparación con red explícita; repetición offline con caché disponible.
  La ubicación de caché debe poder configurarse, respetar la elección del operador y crearse si no existe;
  `.local/` no es un prerrequisito del equipo. No quitar locks, hashes o verificación del paquete para reducir
  comandos visibles. Construir desde clon y consumir un paquete ya construido son entradas diferenciadas;
  la segunda no requiere Node para servir la UI empaquetada. No presupone PyPI ni una Release ya publicada.
- **Configuración global del producto:** asistente inicial determinista accesible sin TOML completo ni agentes
  configurados. Proponer rutas, detectar clientes candidatos y pedir proveedor/modelo, identidad Git, almacenamiento
  y carpetas autorizadas. Mostrar y confirmar antes de guardar. No ejecutar modelos para poder configurarlos.
- **Configuración por proyecto:** perfil propio con preparación, herramientas, validaciones, formateador,
  restricciones e instrucciones. En creación, el revisor lo propone después de concretar documentación y
  arquitectura; en incorporación, usa también la evidencia del HEAD inventariado. No exigir elegir previamente
  una composición específica de stack para poder mantener esa conversación.
- **Preparación y comprobación:** el ejecutor prepara/comprueba lo autorizado dentro del proyecto o área acotada;
  el harness ejecuta los comandos admitidos y recoge evidencia. Instalar dependencias o acceder a red forma
  parte de un plan visible y autorizado. Una propuesta sin comprobar no aparece como entorno listo.
- **Gestión en la UI:** formularios, vista TOML y edición manual validada; ayuda opcional del revisor y ejecutor
  para configuración global y por proyecto. Usar formularios/detección para datos mecánicos y modelos para
  decisiones que necesiten contexto. Mostrar diff, efectos y confirmación de la versión exacta para activar.

## 3. Límites que conserva el diseño

El revisor sigue en solo lectura. El ejecutor no recibe escritura general en el archivo global, directorios
del usuario o configuración de Git/uv/npm/CLI/shell. La aplicación valida y guarda los TOML mediante una
operación explícita y recuperable. Ayudar a modificar la configuración global de Harness Local no autoriza
modificar la configuración global del equipo. No se copian credenciales ni se automatiza el login de proveedores.

Los trabajos admitidos conservan sus snapshots y huellas. Cambiar una configuración no reemplaza su contrato,
no reanuda jobs en cuarentena ni acredita recibos de preparación anteriores. El contrato T001 precisa por operación
qué cambios requieren reinicio, nueva admisión, preparación o confirmación. Las copias restauradas de consulta
seguirán siendo de solo lectura, también respecto de los nuevos asistentes y archivos de configuración.

Las configuraciones actuales se deben poder seguir usando e importar al editor con vista previa, sin conversión
silenciosa. T001 concreta ubicación/autoridad de archivos, versiones, referencias, permisos y CAS en su contrato:
contenido en TOML versionado y activación por referencia en SQLite; formatos reservados v9/proyecto v1,
sin tablas/migraciones/endpoints implementados. Las entregas posteriores aplicarán ese diseño. Los archivos con rutas/entornos locales
seguirán fuera de los checkouts; cualquier exportación portable debe excluir datos locales sensibles.

## 4. Orden y reparto del trabajo

| Bloque | Tareas | Resultado comprobable |
|---|---|---|
| Contrato | T001 | Ciclo de vida, autoridad y compatibilidad definidos antes de implementar |
| Operación local | T002–T003 | Instalar y arrancar sin copiar la secuencia del README |
| Configuración global | T004–T006 | Persistencia y asistente de primer uso sin TOML manual |
| Configuración por proyecto | T007–T009 | Contexto → perfil propuesto → preparación → activación |
| Cambios posteriores | T010–T011 | Edición asistida, compatibilidad, recuperación y backup |
| Calidad y apertura | T012–T015 | Recorridos verificados, candidato nuevo, dictamen y cierre |

Una tarea cada vez, según dependencias de NEXT_STEPS. T001 entrega el [contrato](P013-T001_CONTRATO.md)
y D216–D218, con especificación/arquitectura/flujos en paridad como diseño pendiente de implementación.
T002 entrega el [instalador y verificación autocontenida](P013-T002_INSTALACION.md) (D219), con pruebas de
orquestación sintética; T003 entrega el [arranque instalado](P013-T003_ARRANQUE.md) (D220), con procesos
sintéticos y señales. Recorrido instalado pendiente T012/T013. Siguiente: **P013-T004**. Si una entrega
revela contradicción no resuelta, se consulta al usuario antes de cambiar el diseño.

## 5. Verificación de la fase

Matriz mínima: instalación desde clon y desde paquete; rutas con espacios; caché ausente/completa/incompleta;
arranque inicial/reinicio; asistente sin configuración y edición con configuración existente; creación desde
documentación e incorporación desde código sintético; perfil ajeno a los dos ejemplos; edición manual y
asistida; propuesta inválida, comandos no autorizados, configuración obsoleta y guardado concurrente; caída
durante persistencia/preparación/activación; jobs congelados y consulta de backup sin autoridad de ejecución.

Pruebas de backend con procesos y agentes falsos; UI y diagnósticos en inglés/español; paridad de OpenAPI/tipos,
modelos/diagrama y flujos en la tarea que los cambie. Evidencia por tarea: base, comprobaciones, resultados,
límites y artefactos sintéticos en `docs/phase/`. T012 consolida QA y documentación; T013 verifica el candidato
exacto con las suites pertinentes y el paquete fuera del checkout. No atribuir uso real nuevo a esta evidencia.

Esta planificación no autoriza ejecutar el harness, lanzar agentes/proveedores o smokes, instalar/descargar,
levantar servicios, modificar configuración global del equipo ni operar bases/fixtures de fases anteriores.
Cuando una prueba necesite operación restringida por AGENTS, se preparará el guion acotado y se pedirá la
autorización que falte. Los checks documentales y tests sintéticos pertinentes se distinguen de esos recorridos.

## 6. Publicación aplazada y conservación

La publicación en GitHub queda aplazada hasta el cierre satisfactorio de P013. Esto sustituye la previsión
de apertura como siguiente paso tras P012; no reabre ni cambia el dictamen de esa fase. El expediente archivado
de P012 y el suplemento D214 conservan su procedencia como base anterior a P013.

`my_harness_dist`, sus originales P011/P012 y los paquetes actuales no se modifican en esta planificación.
T013 preparará un candidato nuevo con manifiesto y evidencia propios, preservando los anteriores; cualquier
sustitución de la ruta del candidato se concretará sobre el resultado revisable y la autorización disponible.
T014 emitirá un expediente nuevo y T015 archivará la fase. El cierre no ejecuta la apertura: seguirán haciendo
falta owner/repo, identidad pública, visibilidad y autorización de las acciones remotas concretas.

D157 conserva la transición a una fuente pública principal tras el primer push. El modo continuo de D156
sigue reservado para v0.2.0 posterior a la apertura; no entra en P013. No se cambia ahora la versión `0.1.0`.

## 7. Comprobación de esta apertura

Planificación documental: parsers de fases/tareas/decisiones, dependencias, enlaces locales, presupuestos,
conservación de los cuerpos D001–D214 y de los snapshots archivados, y diff. Resultados en
[P013_APERTURA](P013_APERTURA.md). Sin pruebas de producto ni funcionalidades implementadas en esta tarea.
