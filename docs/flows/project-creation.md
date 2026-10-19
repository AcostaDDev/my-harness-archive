# Flujo previsto — carpeta de proyectos y Django desde cero (P009)

**Estado: diseñado, pendiente de implementación.** D115; [plan](../phase/P009_PLAN_DJANGO.md) y
[tareas](../NEXT_STEPS.md). El flujo vigente de definición documental continúa en
[project-definition](project-definition.md); este documento describe la ampliación de P009.

```mermaid
flowchart TD
    U["Usuario elige explícitamente su carpeta de proyectos"] --> R["Servicio muestra ruta canónica y guarda la autorización de creación de hijos"]
    R --> N["Usuario indica nombre; UI muestra destino completo nuevo"]
    N --> V{"¿Raíz vigente y destino nuevo dentro de su alcance?"}
    V -- no --> X["Diagnóstico sin escribir en destinos ajenos"]
    V -- sí --> C["Persistir intención; crear hijo y registrar idempotentemente"]
    C --> D["Definición conversacional D088 y commit documental raíz"]
    D --> P["Mostrar receta Django: archivos, dependencias, comandos y red exactos"]
    P --> A["Usuario acepta el plan de preparación dentro de la carpeta ya autorizada"]
    A --> S["Preparación controlada: entorno, scaffold, configuración y commit técnico"]
    S --> Q["Usuario elige roles y modelo/esfuerzo del revisor por proyecto"]
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

T001 definirá API, persistencia/migraciones y convivencia con el TOML. Al implementar T002–T004 se actualizarán
este flujo y los diagramas vigentes con lo realmente construido. Este diseño no añade tablas al diagrama actual.
