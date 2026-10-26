# P013-T007 — Propuesta de perfil propio a partir del contexto

Fecha: 2026-10-26. Base: `9182493`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local en inglés.
**Implementada la propuesta documental; preparación T008 y alta/UI/activación T009 pendientes.**
[D224](../DECISIONS.md#d224--p013-t007-contexto-documental-sin-stack-y-propuesta-de-perfil),
[contrato §7–§9](P013-T001_CONTRATO.md#7-dos-entradas-commits-y-perfil-preparado),
[flujo entregado](../flows/configuration-setup.md#propuesta-entregada-en-t007),
[paridad de datos](../DDBB-DIAGRAM.md#altas-documentales-y-propuestas-de-perfil-p013-t007).

## Resultado y motivo

El registro v9 puede representar una raíz existente confiada, vacía o con repositorio B, sin composición ni
perfil. `IntakeContext` lleva solo raíz, layout, política de agentes e idioma de trabajo; no fabrica un
`ProjectProfile` para poder conversar y no crea runner de stack. Solo admite jobs de definición/incorporación;
las guardias del motor y del repositorio rechazan tareas. Registro ACTIVE identifica la raíz, mientras
`PROFILE_REQUIRED`/`PROFILE_PROPOSED` expresan la disponibilidad documental, sin acreditar entorno.

La conversación parte de brief/documentos o inventario estático y HEAD. Las nuevas plantillas
`define-project-profile`/`onboard-project-profile` conservan el revisor de lectura y su esquema tipado por
intento. Se pregunta antes de concretar arquitectura insuficiente; el perfil puede ser null. Una vez concretas
especificación/arquitectura, el perfil se propone aparte de los documentos D088. Se congela el perfil anterior
para poder refinarlo en otro turno. Los ejemplos de stack son opcionales; el fixture nuevo usa Go.

Se contrastaron D218, T001 y las conversaciones/guardias vigentes. No quedaron ambigüedades de diseño que
requirieran HITL. La representación nullable y el uso de las propuestas versionadas existentes concretan los
modelos/DTO reservados por D218. La guardia de arranque global de T005 distingue ahora filas v9 sin perfil de registros legacy con composición;
las primeras pueden reiniciar y los segundos siguen exigiendo importación T011. La operación de carpeta
y el commit documental propios se integran en T009;
esta tarea puede conversar sobre una carpeta vacía ya elegida mediante el registro protegido.

## Candidato y evidencia

`project-profile-proposal-1` contiene nombre/perfil declarativo, herramientas, motivo y evidencia por comando.
Reutiliza el parser de perfiles del producto: argv sin shell, cwd/patrones relativos, preparación/validaciones,
JUnit opcional, prefijos, rutas protegidas/sensibles/de modelos, instrucciones y formateador optativo con `--`.
Cada herramienta se declara una vez por nombre y requisito de entorno, sin afirmar ruta instalada. Herramientas
faltantes de la declaración bloquean; disponibilidad efectiva queda diferida a preparación T008.

Cada comando de preparación, validación, formateador y prefijo debe tener evidencia exacta de documento o
entrada de inventario con path/hash y motivo. Una validación declara propósito test/build/check; ayuda, versión
y no-op no acreditan validación funcional. Se rechazan claves desconocidas, forma inválida, secretos reconocibles,
comandos/rutas/formateador inválidos y propuestas mayores de 64 KiB. El error propio es saneado y localizado en/es.
Esta comprobación estructural no ejecuta ni prueba la semántica de una herramienta: T008 comprobará el entorno.

El binding sella todos los borradores resultantes y HEAD/tree/huella de inventario cuando existen. Las fuentes
pueden ser documentos propuestos en el mismo turno; antes de adoptar el perfil deben estar aplicados por CAS.
Los borradores de B siguen privados y el revisor trabaja sobre la exportación de lectura del HEAD, sin metadatos
Git ni ejecución de fuentes/scripts/gestores. HEAD/inventario se revisan antes de encolar, antes de invocar y al
adoptar; los turnos históricos 1–8 conservan su comportamiento de instantánea.

## Confirmación y persistencia

`POST /projects/{p}/planning/{c}/profile/preview` recibe id/hash de propuesta y versión de conversación.
Devuelve candidato, evidencia, bloqueos y hash exacto de preview. `profile/confirm` añade hash de preview,
confirmación literal, motivo e `Idempotency-Key`. Revalida versión, último turno, contexto/política/idioma y
versiones actuales, documentos aplicados, HEAD/inventario y preguntas/pendientes. Una pregunta bloqueante
aplazada no se convierte en respuesta para este carril. Una base obsoleta no se rebasa silenciosamente.

Confirmar cambia la propuesta de PROPOSED a ACCEPTED e incrementa la conversación; solo adopta borrador.
No escribe TOML, crea operaciones de configuración, prepara, comitea documentos ni activa. Reenvío exacto
retorna el resultado previo; otra petición con la misma clave rechaza. Otro turno válido sustituye los perfiles
anteriores, incluso adoptados, conservando confirmación y resultado de replay. GET describe el borrador sin
sondear herramientas; preview vuelve a comprobar su vigencia. Las composiciones con nombre no habilitan un
atajo de registro v9 hacia tareas mientras faltan T008/T009. Los formatos 1–8 conservan su carril.

Se reutilizan `planning_proposals` (kind `profile`, contenido JSON canónico), turnos y conversaciones.
`0027_profile_proposals` conserva 54 tablas: composición/perfil nullable en registro. Filas/hashes/auditorías
anteriores intactos. Downgrade rechaza altas null, runs de intake o propuestas de perfil. La reconstrucción
SQLite difiere referencias y comprueba todas las FK antes de liberar el diferimiento; una regresión con fila
y auditoría existentes prueba upgrade/downgrade sin pérdida. El downgrade 0021 retira columna/FK con batch
para aceptar la representación reconstruida; no cambia su upgrade ni reescribe datos históricos.

## Validación

- Suite completa `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: **1917 correctos y
  29 subtests**, **dos opt-in omitidas**, sin fallos. Avisos conocidos de TestClient y ZIP duplicado deliberado.
  El ajuste posterior de la guardia global y su caso nuevo se verificaron con **18 pruebas focalizadas
  correctas** (`test_configuration_api.py` y el recorrido global versionado/alta/reinicio), sin repetir otra
  suite completa. Ambos resultados se distinguen para no atribuir a la suite un caso añadido después de recogerla.
- Regresión focalizada final: **38 correctos**: ambas entradas sin perfil, respuesta sin candidato/preguntas,
  Go ajeno a los ejemplos, adopción exacta/replay y reemplazo con perfil anterior congelado; forma inválida,
  herramientas ausentes, validación insuficiente, shell/cwd/formateador/evidencia/secretos/prefijo inválidos;
  documentos/contexto/versiones/HEAD obsoletos, guardias de tareas/commit, API estricta, CSRF/Origin y estado.
  También perfil completo con preparación/JUnit/formateador/prefijo, registro v9/reinicio/downgrade bloqueado,
  migración con auditoría existente y flujo HTTP previo de tareas/commit.
- **8 unittest y 136 Node correctos**. OpenAPI exportado y tipos regenerados: dos rutas nuevas y cuatro DTO
  de propuesta; profile nullable en lecturas de registro/proyecto y estado documental público. Tipos y build
  correctos, con aviso conocido de chunks grandes. Sin componentes nuevos; UI integrada queda en T009.
- Alembic `upgrade head` y `check` en SQLite temporal: sin diferencias, **54 tablas** de producto y guardia
  de esquema correcta. Upgrade/downgrade con referencias existentes, metadata y bloqueo del downgrade de
  intake probados. Regresión de migraciones/conversaciones/prompts: 32 correctos tras ajustar batch 0021.
  Regresión adicional del arranque global versionado → alta sin perfil → reinicio, con preflight/modelos
  sustituidos, conserva READY y la puerta documental; el rechazo de legacy sigue cubierto por T005.
- Primera suite completa: 1915 correctos y 29 subtests, un fallo de expectativa por el campo público nuevo
  `configuration_state` y tres omisiones (dos opt-in y un parámetro HEAD de definición). Expectativa actualizada;
  parámetro sin HEAD ya no se omite. La comprobación focalizada posterior incluye el caso corregido.
- Parsers: **13 fases, 15 tareas y 224 decisiones consecutivas**, 835 enlaces/anclas locales comprobados.
  Cuerpos D001–D223 y archivos de fases anteriores intactos. Presupuestos D088 correctos. Mermaid: **tres
  flowcharts, dos secuencias y trece diagramas ER**, cero errores, con el checker archivado citado por T001;
  se corrigieron separadores en la nueva secuencia. Solo sintaxis con stub DOMPurify, sin renderizado ni QA
  visual. El intento inicial de parser directo en Node no disponía de DOM y se sustituyó por ese checker.
  `git diff --check` correcto y diff revisado.

## Límites y siguiente tarea

Las pruebas usan agentes/herramientas falsos y archivos/Git/SQLite temporales. No hay proveedores/modelos,
servicios instalados, navegador/QA visual, red, operación del harness sobre este repositorio ni cambios globales
del equipo. No se operan bases privadas ni artefactos/snapshots/candidatos P001–P012/D214. Sin wheel nuevo,
push, CI remota, tag ni publicación. Diagnósticos propios en/es y API protegida; no se atribuye preparación
real a una propuesta validada por forma/fuentes. Siguiente tarea: **P013-T008**.
