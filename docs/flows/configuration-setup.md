# Flujo — instalación y configuración guiadas (P013)

**Instalación T002, arranque T003 y persistencia T004 implementados; integración pendiente T005–T011.**
[Entrega T002](../phase/P013-T002_INSTALACION.md), D219; validación con herramientas falsas, sin recorrido instalado nuevo.
[Entrega T003](../phase/P013-T003_ARRANQUE.md), D220; procesos/señales sintéticos, sin servicio instalado real.
[Contrato](../phase/P013-T001_CONTRATO.md), D216–D218 en [DECISIONS](../DECISIONS.md),
[plan](../phase/P013_PLAN.md) y [tareas](../NEXT_STEPS.md).
El flujo vigente aún usa TOML 1–8 y composición según ARCHITECTURE §6/§9.

## Instalación y primer arranque

```mermaid
flowchart TD
    A["Elegir clon o paquete; rutas, Python, uv y caché"] --> B{"¿Requisitos y destinos válidos?"}
    B -- no --> X["Diagnóstico; conservar instalación y datos previos"]
    B -- sí --> C["Preparar caché: offline o red explícitamente autorizada"]
    C --> D["Clon: construir; paquete: verificar sin Node ni checkout"]
    D --> E["Verificar artefactos y wheel aislado; instalar generación nueva"]
    E --> F["Publicar referencia y recibo installation-1 solo tras éxito"]
    F --> G["start: binario instalado, DB y temporal privados"]
    G --> H{"¿Base existente?"}
    H -- no --> I["Inicialización exclusiva; sin auxiliares previos"]
    H -- sí --> J{"¿Esquema compatible?"}
    J -- no --> K["Detener: migración D150 aparte con parada y backup"]
    I --> L["Resolver consulta, configuración y recuperación"]
    J -- sí --> L
```

Fallos de caché/requisitos no abren red ni publican instalación parcial. Actualizar usa generación nueva y
parada explícita, sin borrar datos ni hacer downgrade de esquema. Reiniciar no reinstala, migra, limpia locks
inciertos o acredita muerte de escritores. T002 conserva la comparación contra fuentes al construir y
entrega manifiesto `distribution-1`,
wrappers/verificador/fixture con checksums para paquete autocontenido. Comprueba miembros/metadatos/hashes
y el recorrido sintético instalado D051; las pruebas de T002 no ejecutan ese servicio.
`installation-1` vive en cada generación; `current.json` referencia generación/hash tras fsync. Un lock
excluye instaladores, replay comprueba paquete/venv y `--upgrade --writers-stopped` conserva anteriores.
Fallos/interrupciones retienen intención FAILED o PREPARING sin anunciar una generación lista.
Datos/configuración se crean privados y vacíos en instalación nueva, sin DB/TOML ni migraciones.

T003 resuelve `current.json`/`installation-1` y verifica paquete/venv antes de ejecutar su Python aislado,
con cwd en los datos del recibo. DB/configuración elegibles dentro de sus respectivas raíces; temporal
privado y puerto loopback elegibles. Rechaza puerto ocupado/rutas inseguras; preflight de esquema SQLite
en solo lectura y `init-db` exclusivo solo si no hay DB ni auxiliares. No reinstala ni migra al reiniciar.
Locks de instancia/instalación heredados por el hijo impiden segundo servicio/actualización incluso si
muere el wrapper; señales se reenvían y se espera al hijo. No libera guardias de jobs ni declara escritores
muertos. Consulta D040 omite TOML operativo; TOML inválido bloquea antes de servir. Sin TOML arranca hoy
la UI protegida de consulta vigente, sin consumidores gestionados; la transición al asistente del diagrama
siguiente sigue pendiente T005/T006. T004 entrega la persistencia separada; aún no se conecta con este wrapper ni con consumidores del servicio.

## Asistente y activación global

```mermaid
flowchart TD
    A["Resolver modo antes de consumidores"] --> B{"¿Consulta D040?"}
    B -- sí --> C["Solo evidencia; sin TOML operativo, CLI o mutaciones"]
    B -- no --> D{"¿Autoridad íntegra y válida?"}
    D -- no --> E["UNCONFIGURED, INVALID o RECOVERY_REQUIRED; sesión local protegida"]
    E --> F["Asistente determinista: rutas, clientes, identidad y límites"]
    D -- sí --> G["READY; ajustes globales disponibles"]
    G --> F
    F --> H["Formulario o TOML; validar y mostrar diff e impacto"]
    H --> I["Guardar por CAS e intención; versión privada sin activar"]
    I --> J["Preview de activación: mismo contenido y ausencia de trabajo pendiente"]
    J --> K["Confirmar versión exacta: RESTART_REQUIRED y cerrar admisión"]
    K --> L["Reinicio explícito; comprobar archivos y promover activa en SQLite"]
    L --> G
```

Sesión/Host/Origin/cross-site/CSRF también sin TOML. Detectar no invoca modelos; comprobar clientes es acción
explícita version/help D174. Ayuda IA solo con pareja activa congelada. Archivo inválido no se reemplaza por
un ejemplo ni habilita colas; fallo al promover conserva activa anterior y bloqueo, sin fallback silencioso.
Cancelar una activación pendiente también exige versión/confirmación; guardar no tiene ese efecto.

## Persistencia y recuperación

Primitivas T004 implementadas ([D221](../DECISIONS.md#d221--p013-t004-journal-y-referencias-de-configuración),
[entrega](../phase/P013-T004_CONFIGURACION.md)): `preview/save`, `activation_preview/activate`,
`promote_pending/cancel_pending`, `recovery_preview/recover` y descarte/importación explícitos de cambios externos.
Sin endpoints/UI ni ejecución v9 todavía. Guardado con barrera SQLite y flock de instalación; intención ligada
a directorios de configuración/estado. Revisiones DRAFT o VALIDATED, copias privadas y fsync por publicación.
Recuperación exige declaración de escritores detenidos y exclusión efectiva; se audita como otra operación,
sin inferir parada por lease. Global sella el conjunto pendiente por id de activación y promueve en transacción;
permite guardar borradores mientras espera reinicio. Proyecto requiere verificador de preparación del servicio
(sin fallback permisivo); T008/T009 conectarán recibos/HEAD/runtime. Trabajo pendiente bloquea activación,
no guardado. Bundle actual rechaza operaciones de configuración: soporte autocontenido pendiente T011.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant S as Servicio
    participant DB as SQLite
    participant F as Archivos privados
    U->>S: preview con candidato, versión y hashes base
    S-->>U: diff, validación, impacto y hash exacto
    U->>S: save con CAS, confirmación y clave idempotente
    S->>DB: intención configuration-operation-1 y bytes sellados
    S->>F: temporales exclusivos, fsync y publicación atómica por archivo
    S->>F: verificar conjunto y hashes y fsync de directorios
    S->>DB: finalizar versión guardada por CAS, sin activar
    S-->>U: misma operación y referencia tras replay
    Note over DB,F: Caída parcial sin activa nueva, conciliar bytes base o candidatos, nunca sobrescribir terceros
    U->>S: preview y confirmación de activación separada
    S->>DB: barrera con admisión/commit y referencia exacta o reinicio pendiente
```

TOML inmutable manda en contenido; SQLite manda en qué referencia está activa. Las copias editables
`global.toml`/`projects/<id>/project.toml` no son hot reload. Edición externa bloquea nuevas operaciones del
ámbito hasta importar/descartar por CAS. Deriva de versión inmutable detiene/cuarentena antes de efectos.
Una caída o lease vencido no permite asumir escritor detenido. Repetir clave/payload devuelve resultado;
otro payload con la misma clave da conflicto. Backup futuro incluye archivos/versiones/intenciones por
bytes/hashes, no solo rutas; restore conserva consulta sin repararlos ni activar procesos.

## Perfil por proyecto y dos entradas

```mermaid
flowchart TD
    A["Nuevo: raíz y brief; contexto documental sin stack"] --> C["Revisor de lectura: preguntas, arquitectura y borradores"]
    B["B: raíz confiada, inventario y HEAD sellado; sin ejecutar código"] --> C
    C --> D["Propuesta estructurada de perfil; herramientas diferidas y validaciones significativas"]
    D --> E["Usuario revisa formulario o TOML; ejemplos opcionales"]
    E --> F["Confirmar documentos y propuesta compatible; commit raíz o B; adoptar P001"]
    F --> G["PREPARATION_REQUIRED: tareas bloqueadas"]
    G --> H["Confirmar plan técnico de archivos, comandos, red y ámbito"]
    H --> I["Ejecutor acotado o receta; harness valida y recoge evidencia"]
    I --> J{"¿Resultado y contenido acreditados?"}
    J -- no --> K["Fallo o recuperación: conservar journal y puerta cerrada"]
    J -- sí --> L["Conciliar commit técnico si procede y emitir recibo"]
    L --> M["READY_TO_ACTIVATE; diff, impacto y confirmación exacta"]
    M --> N["Aplicación activa perfil; primera tarea habilitada"]
    N --> O["Edición posterior manual o asistida: guardar, comprobar y activar"]
    O --> E
```

P001 ACTIVE no equivale a perfil operativo. El TOML vive fuera del checkout y el commit documental precede
al técnico. En B se conservan guardias Git, originales/phase-000 y bytes del código; en nuevo, solo D088 antes
del commit raíz. Cambiar el perfil contradiciendo documentos exige edición documental confirmada y evidencia
nueva. Activación no repite alta/commits/preparación. Perfil propio se activa sin reiniciar, con barrera de
admisión; trabajo pendiente ajeno a su evidencia de alta ya terminada lo bloquea según D118.

`project-profile-preparation-1` es preparación genérica nueva, no conversión de recetas/recibos v1/v2.
Ejecutor sin escritura general de configuración global ni ajustes del equipo. Guardar/activar son escrituras
del servicio confirmadas por el usuario. Recibo liga perfil/comandos/herramientas/entorno/contenido; propuesta
sin comprobar no acredita entorno listo. Caída exige recuperación enlazada, nunca replay implícito de red.

V1–v8 conservan operación/hashes; edición guiada requiere importación explícita al conjunto v9/proyecto v1,
originales intactos. Jobs/snapshots/recibos históricos no se actualizan a posteriori. El detalle de estados,
API/UI, reinicios y matriz de fallos está en el contrato; diagrama de datos se ampliará con la migración real.
