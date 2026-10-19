# Flujo — carpeta de proyectos y Django desde cero (P009)

**Estado: selección/retirada de carpeta y creación/registro del hijo implementados en T002 (D117).**
Roles por proyecto implementados en T003 (D118); preparación Django implementada en T004 (D119), con herramientas sintéticas. D115/D116;
[contrato/API/recuperación](../phase/P009-T001_CONTRATO_CREACION.md), [plan](../phase/P009_PLAN_DJANGO.md) y
[tareas](../NEXT_STEPS.md). El flujo vigente de definición documental continúa en
[project-definition](project-definition.md); el detalle técnico de preparación está en [project-preparation](project-preparation.md). El piloto real sigue pendiente.

```mermaid
flowchart TD
    U["Usuario elige explícitamente su carpeta de proyectos"] --> R["Servicio muestra ruta canónica y guarda la autorización de creación de hijos"]
    R --> N["Usuario indica nombre; UI muestra destino completo nuevo"]
    N --> V{"¿Raíz vigente y destino nuevo dentro de su alcance?"}
    V -- no --> X["Diagnóstico sin escribir en destinos ajenos"]
    V -- sí --> C["Persistir intención; crear hijo y registrar idempotentemente"]
    C --> D["Enlace a definición documental con agentes efectivos: presets v5 o pareja heredada"]
    D --> DC["Definición conversacional D088 y commit documental raíz"]
    DC --> P["Mostrar receta Django: archivos, dependencias, comandos y red exactos"]
    P --> A["Usuario acepta el plan de preparación dentro de la carpeta ya autorizada"]
    A --> S["Preparación controlada: entorno, scaffold, configuración y commit técnico"]
    S --> Q["Usuario revisa roles y modelo/esfuerzo del revisor por proyecto"]
    Q --> E["Revisor planifica y decide modelo/esfuerzo del ejecutor con motivo"]
    E --> T["Ejecutor escribe solo en el hijo; validaciones, revisión y commit del harness"]
    T --> M{"¿Faltan tareas de la matriz?"}
    M -- sí --> B["Con tarea COMMITTED y sin jobs pendientes, cambiar ajustes del mismo proyecto"]
    B --> Q
    M -- no --> F["QA final; check READY y cierre/archivo de P001 del Django"]
    F --> I["Revisión de salida de P009 con resultados y límites"]
    C -. caída .-> Z["Recuperación por intención y autoridad vigente; sin duplicar ni borrar contenido incierto"]
    S -. caída .-> Z
```

La raíz padre se elige desde una acción de UI; la IA no la descubre o deduce. Guardarla concede al servicio
crear nuevos hijos sin repetir el permiso de carpeta para cada proyecto; no concede escritura al ejecutor
en el padre/hermanos ni autorización general para red, instalación o proveedores. Las operaciones técnicas
se ejecutan dentro de su plan confirmado, con intención previa, idempotencia y recuperación.

La configuración de roles es por proyecto, desde presets del servicio: el usuario fija proveedor/modelo/esfuerzo
del revisor y proveedor/catálogo del ejecutor; el revisor fija modelo/esfuerzo concretos de este último.
Matriz en el mismo id/checkout: Codex→Codex, Codex→Claude, Claude→Claude y Claude→Codex, siempre revisor→ejecutor.
Las cuatro tareas terminan COMMITTED; no se modifican los snapshots previos al cambiar ajustes.

La autoridad UI permite hijos directos nuevos, aunque el padre no figure en el TOML. Las raíces TOML mantienen
el alta de carpetas existentes con confianza exacta; elegir el padre no amplía ese alta ni confía en hermanos.
Al guardar/cambiar/retirar la selección aumenta su revisión. Antes de cada efecto corto, creación comprueba
esa revisión y la identidad del padre bajo exclusión compartida con la retirada. Los conflictos incluyen ancestros físicos y alias de mayúsculas, también en reservas aún sin carpeta.
Un hijo ya registrado sigue con su autoridad propia. Reelección de la misma ruta no reanuda operaciones automáticamente.

```mermaid
stateDiagram-v2
    [*] --> INTENDED: intención y reservas persistidas
    INTENDED --> DIRECTORY_CREATED: mkdir exclusivo e identidad persistida
    DIRECTORY_CREATED --> REGISTERED: alta y resultado atómicos
    INTENDED --> RECOVERY_REQUIRED: carpeta sin prueba de propiedad
    INTENDED --> BLOCKED: autoridad o destino cambiado
    DIRECTORY_CREATED --> BLOCKED: autoridad retirada o deriva
    RECOVERY_REQUIRED --> CANCELLED: conservar carpeta y reserva inciertas
    BLOCKED --> CANCELLED: detener sin borrar
    BLOCKED --> DIRECTORY_CREATED: reanudación confirmada con propiedad acreditada
    INTENDED --> CANCELLED: detener efectos pendientes
    DIRECTORY_CREATED --> CANCELLED: conservar carpeta
    CANCELLED --> CANCELLED: comprobar ausencia sin reabrir efectos
    REGISTERED --> [*]
```

Una caída después de `mkdir` y antes de persistir la identidad exige recuperación explícita; el vacío no
demuestra propiedad. No se borran carpetas inciertas. Repetir clave/payload devuelve la operación original;
otra clave no puede reservar el mismo destino/id. Una respuesta perdida tras el alta devuelve el mismo proyecto,
incluso si después se retiró el padre. El estado `BLOCKED` no concede autoridad para continuar.

**Implementado en T003:** en v5, presets seleccionados y agentes efectivos se componen por checkout.
[Selección, bloqueos e invalidación de planes](project-agents.md). Cambiar ajustes exige no tener
trabajo pendiente utilizable bajo la selección anterior; se congelan versiones y los borradores anteriores
quedan obsoletos. Formatos previos y proyectos sin override conservan su pareja global, sin sustituciones.

**Implementado en T004:** la definición admite solo sus documentos actuales. Los enlaces tipados a herramientas de `.venv` permiten
confirmar ese commit sin instalar antes; tareas/checks de ese perfil siguen bloqueados hasta preparar.
La receta usa escritor y plan propios para archivos protegidos, con intención/pasos/lease/lock y procesos
registrados. Confirmar liga archivos/argv/HEAD/versiones/red/límites; fallos o cancelación detienen, sin repetir
instalación/red. El commit técnico se concilia antes de adoptar atómicamente el recibo y habilitar tareas.

T002 implementa `/project-creation-root` (GET, preview y apply) y `/project-creations`
(preview, confirm, lectura por id, resume/preview, resume/confirm y cancel). Confirmaciones con sesión, CSRF,
clave idempotente, versión y hash; el formulario conserva el sobre tras perder respuesta o recargar.
El arranque clasifica un destino presente sin identidad acreditada como RECOVERY_REQUIRED, sin tocarlo.
Los efectos son síncronos y cortos, serializados con la retirada mediante lock y transacciones SQLite.
Guardar otra selección o retirarla bloquea intenciones pendientes; la reanudación confirma la misma operación
y preserva su intención original. Cancelar solo libera reservas si se acredita ausencia; conserva bytes. Tras resolución externa, una nueva
comprobación versionada puede liberar una reserva de cancelación sin reabrir efectos.
Cuatro tablas nuevas y procedencia del registro en [DDBB-DIAGRAM](../DDBB-DIAGRAM.md);
detalles y verificación en [entrega T002](../phase/P009-T002_CARPETA_PROYECTOS.md). D118 implementa roles con el JSON existente del registro. D116 sigue fijando
el contrato de receta implementado por D119; [flujo de preparación](project-preparation.md) y [entrega T004](../phase/P009-T004_RECETA_DJANGO.md).
