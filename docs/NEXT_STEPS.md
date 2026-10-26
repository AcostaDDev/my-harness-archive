# P013 — Instalación guiada y configuración desde la UI

**Estado:** fase activa; T001 diseñada y T002–T007 implementadas el 2026-10-26, ocho tareas pendientes.
**Siguiente: P013-T008**, preparación y comprobación acotadas con el ejecutor.
[Objetivo y criterios](ROADMAP.md#p013--instalación-guiada-y-configuración-desde-la-ui),
[D215](DECISIONS.md#d215--p013-instalación-guiada-y-configuración-desde-la-ui) y
[plan de fase](phase/P013_PLAN.md).

Publicación en GitHub aplazada hasta cerrar P013 con candidato nuevo y dictamen favorable. P001–P012
permanecen cerradas y sus snapshots intactos. El expediente P012 y el suplemento D214 se conservan como
antecedentes, sin autorizar abrir el candidato anterior durante P013. Tras el primer push seguirá rigiendo D157.
Modo continuo v0.2.0 fuera de esta fase (D156).

## Restricciones compartidas

- Una tarea acotada cada vez, desarrollo manual; no operar este repositorio con el harness ni lanzar agentes,
  proveedores o smokes por el hecho de abrir la fase. Sin commits salvo petición, push, CI remota, tag o publicación.
- Fixtures sintéticos y áreas temporales propias, sin reutilizar bases, saldos o consentimientos de P012.
  ReferenceProject solo lectura; sin credenciales ni cambios en la configuración global de Git/CLI/uv/npm/shell.
- El revisor propone en solo lectura; el ejecutor prepara/comprueba en un ámbito acotado; la aplicación guarda
  la configuración validada. Configuración global de Harness Local y configuración global del equipo son distintas.
- Formularios y detección local para datos mecánicos; ayuda IA opcional una vez configurados los clientes.
  TOML editable, con validación, diff y confirmación; no exigir comandos de stack antes de la definición.
- Toda tarea que cambie datos actualiza DDBB-DIAGRAM; todo flujo, su documento en `docs/flows/`;
  API/OpenAPI/tipos e inglés/español en paridad. No dar por implementado el diseño de T001 o de esta apertura.
- Decisiones duraderas en DECISIONS; evidencia por tarea en `docs/phase/` con checks, omisiones y límites.
  Historiales, recibos y snapshots congelados no se reescriben al cambiar configuración.

## P013-T001 — Contrato de instalación y ciclo de vida de la configuración

**Estado:** completada como diseño (2026-10-26), sin cambios de producto. **Depende de:** apertura D215.
[Contrato](phase/P013-T001_CONTRATO.md), [validación](phase/P013-T001_VALIDACION.md) y D216–D218.
**Objetivo:** concretar antes de implementar el diseño acordado en el plan de fase.
**Rutas permitidas:** `docs/**` vigentes; archivos históricos solo lectura.
**Criterios de aceptación:**

- Definir instalación desde clon/paquete, directorios, selección de Python/uv, caché configurable, primer uso con
  red, repetición offline, actualizaciones y reinicios; conservar aislamiento del wheel y verificación D051/D150.
- Definir autoridad, localización fuera de checkouts, versiones y referencias de TOML global y por proyecto;
  relación con SQLite, importación de formatos 1–8, permisos y guardado atómico con CAS/recuperación.
- Definir arranque sin configuración, sesión inicial, activación, cambios con jobs pendientes/activos, recibos
  de preparación, backup/consulta y efecto de editar archivos externamente. Precisar cuándo hace falta reinicio.
- Concretar las dos entradas sin composición previa: contexto/documentos → propuesta → preparación/comprobación
  → activación, incluidos commits documentales y recetas existentes. Asistencia IA global solo tras configurar
  clientes; ningún agente adquiere escritura general de la configuración global.
- Diseñar estados, API/UI y matriz de fallos; actualizar especificación, arquitectura y flujos como diseño
  pendiente. Registrar decisiones; consultar incongruencias no resueltas por D215 antes de cambiar el diseño.

**Validación:** contraste con código y D049/D051/D078/D095/D118/D150/D157/D161/D174/D194/D215;
parsers, enlaces y dependencias. Sin migraciones ni proveedores.
**Entregable:** `docs/phase/P013-T001_CONTRATO.md` y decisiones duraderas.

## P013-T002 — Instalación automatizada y cachés configurables

**Estado:** completada (2026-10-26); orquestación sintética, recorrido instalado pendiente T012/T013.
[Entrega y validación](phase/P013-T002_INSTALACION.md), D219. **Depende de:** T001.
**Objetivo:** instalar sin copiar la secuencia de construcción/venv/pip del README.
**Rutas permitidas:** `scripts/**`, empaquetado si lo exige T001, pruebas específicas y documentación vigente.
**Criterios de aceptación:**

- Entrada `scripts/install` con ayuda/opciones de rutas; crea venv, directorios y caché cuando corresponda,
  respeta la elección del operador y no exige `.local/` preexistente ni activación manual del entorno.
- Desde clon compone construcción, verificación e instalación con locks/hashes. Desde paquete ya construido,
  instala sin Node/npm ni checkout de desarrollo como dependencia de ejecución.
- Primera preparación con red explícita y modo offline; caché incompleta o requisito ausente produce diagnóstico
  útil sin modificar configuración global ni presentar una instalación parcial como válida.
- Rutas con espacios, repetición y destino ocupado tratados sin sobrescribir instalaciones/datos a ciegas;
  diferenciar nueva instalación y actualización con D150.

**Validación:** orquestación con herramientas falsas/directorios temporales; recorrido instalado en T012/T013.
**Entregable:** `docs/phase/P013-T002_INSTALACION.md`.

## P013-T003 — Arranque automatizado del paquete instalado

**Estado:** completada (2026-10-26); orquestación/señales sintéticas, recorrido instalado pendiente T012/T013.
[Entrega y validación](phase/P013-T003_ARRANQUE.md), D220. **Depende de:** T001–T002.
**Objetivo:** arrancar con una entrada corta y opciones editables/documentadas.
**Rutas permitidas:** `scripts/**`, pruebas específicas y documentación vigente.
**Criterios de aceptación:**

- Entrada `scripts/start` usa venv/rutas elegidas; admite base, configuración, puerto y temporal privado.
  Inicializa base nueva según T001 y conserva datos al reiniciar.
- Usa el paquete fuera del checkout, sin Node/Vite; conserva `scripts/dev` para desarrollo. Maneja puerto ocupado,
  configuración ausente/inválida y señales; no consume colas/proveedores al mostrar el asistente inicial.
- Base desactualizada pasa por parada/backup/migración acordados, sin migración silenciosa en `serve` ni asumir
  muerte de escritores. Reiniciar no reinstala ni sobrescribe el archivo del usuario.

**Validación:** orquestación/señales con procesos sintéticos; arranque instalado en T012/T013.
**Entregable:** `docs/phase/P013-T003_ARRANQUE.md`.

## P013-T004 — Persistencia y activación versionada de configuración

**Estado:** completada (2026-10-26), primitivas verificadas con archivos/SQLite sintéticos;
API/arranque global conectados en T005; perfiles/recibos/importación pendientes T007–T011.
[Entrega y validación](phase/P013-T004_CONFIGURACION.md), D221. **Depende de:** T001.
**Objetivo:** implementar la autoridad de archivos y versiones compartida por asistentes y edición.
**Rutas permitidas:** configuración/servicios/storage, migraciones según T001, pruebas y docs de paridad.
**Criterios de aceptación:**

- Leer, validar, previsualizar y guardar configuración global y por proyecto; archivos privados fuera de
  checkouts, sin secretos, con límites y comprobación de rutas/propiedad.
- Guardado por versión/hash, intención recuperable y escritura atómica; concurrencia, cambio externo, TOML
  inválido o caída conservan la versión anterior y permiten conciliación sin duplicar efectos entre archivo/SQLite.
- Solo activación confirmada cambia autoridad; no reescribir versiones/snapshots previos ni ampliar permisos
  por un valor propuesto por IA. Formatos actuales siguen cargando; conversión/importación al editor explícita.
- Diagrama actualizado en esta tarea si se añaden modelos/migraciones; no fijar formatos nuevos fuera de T001.

**Validación:** parser, persistencia, concurrencia, fallos inyectados y compatibilidad con fixtures sintéticos.
**Entregable:** `docs/phase/P013-T004_CONFIGURACION.md`.

## P013-T005 — API de configuración inicial sin TOML completo

**Estado:** completada (2026-10-26); API/TestClient y clientes sintéticos, UI entregada en T006.
[Entrega y checks](phase/P013-T005_ASISTENTE_API.md), D222. **Depende de:** T003–T004.
**Objetivo:** configurar el producto antes de disponer de agentes o composiciones.
**Rutas permitidas:** CLI/API, servicios de configuración/runtime, pruebas y docs de paridad.
**Criterios de aceptación:**

- Servicio instalado admite asistente autenticado sin configurar; rechaza mutaciones gestionadas hasta tener
  autoridad válida. Conservar sesión local, Host/Origin y CSRF; restore de consulta no habilita este carril.
- Detectar rutas/clientes candidatos y permitir valores manuales; elegir proveedor/modelo, identidad Git,
  almacenamiento y raíces sin invocar modelos ni automatizar credenciales.
- Validar/previsualizar/confirmar configuración mínima por T004; distinguir guardar y activar/reiniciar.
  Comprobación de clientes conserva D174, sin confundir preflight con uso real acreditado.

**Validación:** API con clientes falsos, sesión y estados sin configuración/válido/inválido/consulta;
OpenAPI y tipos regenerados cuando cambie contrato.
**Entregable:** `docs/phase/P013-T005_ASISTENTE_API.md`.

## P013-T006 — Asistente inicial y ajustes globales en la UI

**Estado:** completada (2026-10-26); UI/contrato sintéticos, QA visual integrada pendiente T012.
[Entrega y checks](phase/P013-T006_ASISTENTE_UI.md), D223. **Depende de:** T005.
**Objetivo:** completar/editar configuración global sin copiar una plantilla ni escribir TOML a mano.
**Rutas permitidas:** frontend, API para completar T005, pruebas y docs de paridad.
**Criterios de aceptación:**

- Primer arranque conduce al asistente y explica requisitos/datos faltantes; no exige archivo de ejemplo ni
  composición Django/TypeScript. Ajustes accesibles después desde la navegación normal.
- Formularios con sugerencias, vista TOML y edición manual validada; diff, errores por campo, confirmación exacta
  y estado de activación/reinicio visibles; conflicto no pierde cambios ni sobreescribe otra versión.
- Textos/diagnósticos propios en/es, navegación por teclado y tamaños soportados; no exponer credenciales,
  tokens de sesión o entornos privados en listados públicos.

**Validación:** tests UI/contrato, tipos/build; revisión visual sintética en T012.
**Entregable:** `docs/phase/P013-T006_ASISTENTE_UI.md`.

## P013-T007 — Propuesta de perfil propio a partir del contexto del proyecto

**Estado:** completada (2026-10-26); agentes falsos y fixtures Go, sin preparación/activación ni proveedores reales.
[Entrega y checks](phase/P013-T007_PROPUESTA_PERFIL.md), D224. **Depende de:** T004–T006.
**Objetivo:** proponer el perfil tras disponer de documentación/arquitectura o inventario del repositorio.
**Rutas permitidas:** planificación/definición/incorporación, perfiles/prompts, API/storage, pruebas y docs de paridad.
**Criterios de aceptación:**

- Definición nueva conversa sin composición de stack previa; al concretar arquitectura el revisor propone
  preparación, herramientas, validaciones, formateador, rutas e instrucciones del proyecto.
- Incorporación conserva inventario/HEAD sellados, evidencia por comando y preguntas sobre lo no deducible;
  no ejecuta código para inferir perfil. Django/TypeScript siguen como ayudas opcionales.
- Salida estructurada, contexto/idiomas congelados y borradores versionados; opciones inválidas, validaciones
  insuficientes o base obsoleta bloquean. Proponer no escribe ni activa el TOML.

**Validación:** agentes falsos y fixtures de creación/incorporación, incluido stack distinto de los ejemplos;
forma inválida, ausencia de herramientas y base obsoleta. Sin llamadas reales.
**Entregable:** `docs/phase/P013-T007_PROPUESTA_PERFIL.md`.

## P013-T008 — Preparación y comprobación acotadas con el ejecutor

**Estado:** pendiente. **Depende de:** T007.
**Objetivo:** comprobar que el perfil corresponde a un entorno utilizable antes de activarlo.
**Rutas permitidas:** preparación/runner/agentes, perfiles/recetas, storage/API, pruebas y docs de paridad.
**Criterios de aceptación:**

- Plan visible de archivos, comandos, dependencias, red y ámbito de escritura; confirmación exacta antes de
  preparar. Ejecutor solo en ese ámbito, sin escribir TOML global ni ajustes del equipo.
- Harness ejecuta autorizaciones exactas/validaciones, conserva argv sin shell y protecciones. Preparación
  genérica no exige receta Django/TypeScript para el stack elegido.
- Evidencia/recibo ligados a configuración, herramientas y contenido comprobados; fallo/interrupción no acredita
  entorno listo. Recuperación idempotente con locks y declaración de escritor detenido cuando corresponda.
- Recetas/recibos existentes conservados; distinguir proponer, instalar y validar.

**Validación:** ejecutor/herramientas falsos, red rechazada, fallo por paso, caída/recuperación y guardias;
proveedores o descargas reales necesitan autorización propia.
**Entregable:** `docs/phase/P013-T008_PREPARACION.md`.

## P013-T009 — Activación del perfil y alta completa desde la UI

**Estado:** pendiente. **Depende de:** T007–T008.
**Objetivo:** unir conversación, perfil y preparación en las dos entradas del producto.
**Rutas permitidas:** frontend, API/servicios de alta/activación, pruebas y docs de paridad.
**Criterios de aceptación:**

- Crear/incorporar permiten editar perfil por formulario/TOML, responder preguntas, confirmar plan y consultar
  preparación sin salir al editor de archivos. Composición existente seleccionable como alternativa.
- Mostrar diff, restricciones y evidencia antes de activar la versión exacta; la aplicación guarda los archivos.
  Primera tarea habilitada solo tras las puertas T001, con documentos/commits y guardias Git conservados.
- Reenvío de confirmación no duplica perfil, preparación, alta ni commit; estado claro ante conflicto,
  propuesta obsoleta y preparación fallida. Interfaz en/es.

**Validación:** integración API/UI con agentes falsos en ambas entradas; tipos/build y reenvío/conflicto.
**Entregable:** `docs/phase/P013-T009_ALTA_UI.md`.

## P013-T010 — Edición posterior manual y asistida de configuración

**Estado:** pendiente. **Depende de:** T006 y T009.
**Objetivo:** mantener ajustes globales/perfiles desde la UI con ayuda IA opcional.
**Rutas permitidas:** configuración/planificación/agentes, API/frontend/storage, pruebas y docs de paridad.
**Criterios de aceptación:**

- Editar formularios/TOML; pedir al revisor cambios razonados con contexto autorizado y al ejecutor
  comprobaciones/preparación acotadas. Ayuda global solo con clientes ya configurados.
- Revisor de lectura y ejecutor sin escritura general de archivos globales; aplicación valida/guarda con
  diff/confirmación, reutilizando T004/T008 sin vía lateral de permisos.
- Mostrar impacto en proyectos, comandos, herramientas, recibos, reinicio y jobs pendientes/activos; editar un
  perfil propio no altera otros por referencia compartida accidental. Cancelar conserva autoridad e históricos.
- Cambiar los propios clientes de asistencia no modifica sesión/job admitidos ni provoca fallback silencioso.

**Validación:** propuestas falsas, concurrencia, impacto global/local y jobs congelados; UI/diagnósticos en/es.
**Entregable:** `docs/phase/P013-T010_EDICION_ASISTIDA.md`.

## P013-T011 — Compatibilidad, recuperación y backup de configuración

**Estado:** pendiente. **Depende de:** T004–T010.
**Objetivo:** verificar la transición desde el TOML actual y la recuperación de las nuevas operaciones.
**Rutas permitidas:** runtime/configuración/backup/storage, API/frontend para defectos acotados, pruebas y docs.
**Criterios de aceptación:**

- TOML 1–8 conserva entrada/hashes; importación/edición explícitas. Jobs/historiales/recibos previos conservan
  autoridad o bloqueo definido, sin actualizar snapshots a posteriori.
- Caída/conflicto archivo/SQLite/activación no deja dos autoridades ni duplica efectos; recuperación verificable
  sin asumir muerte de escritores. Cubrir cambio externo, pendientes/activos y permisos/rutas inválidos.
- Backup incluye/referencia archivos/versiones según contrato; restore de consulta permite leer evidencia sin
  configuración original/agentes y rechaza edición, activación, preparación y llamadas.
- Actualizar flujos/diagrama en cualquier corrección de datos; separar hallazgos ajenos al alcance en tareas propias.

**Validación:** Git/SQLite/archivos temporales, fallos inyectados y agentes falsos; sin operar bases P012.
**Entregable:** `docs/phase/P013-T011_COMPATIBILIDAD.md`.

## P013-T012 — Primer uso integrado, QA y documentación de usuario

**Estado:** pendiente. **Depende de:** T002–T011.
**Objetivo:** acreditar el recorrido completo y explicar uso/desarrollo sin pasos implícitos.
**Rutas permitidas:** README/README.es, docs vigentes/públicas, ejemplos y tests de integración;
correcciones de producto se acotan antes de ampliar rutas.
**Criterios de aceptación:**

- Desde entorno limpio: instalar, arrancar, configurar global desde UI, crear desde documentos y generar/preparar/
  activar perfil; incorporar repositorio y ejecutar tarea con agentes falsos. Perfil ajeno a Django/TypeScript.
- Repetición con caché y diagnóstico de incompleta; rutas con espacios, reinicio, edición y consulta de backup.
  QA visual en/es de asistentes, teclado, temas y anchos soportados, con resultados/límites registrados.
- README separa usuario/desarrollador, explica uv y creación de venv/caché, scripts/opciones, primera instalación
  con red y modo offline; ejemplos opcionales y edición. Docs públicas reflejan lo entregado y son autocontenidas.
- Preparar autorización acotada antes de servicios/smokes restringidos por AGENTS; evidencia sintética no se
  presenta como uso real nuevo ni modifica la procedencia de P012.

**Validación:** matriz de fase, integración con herramientas/agentes falsos, QA visual autorizada y checks documentales.
**Entregable:** `docs/phase/P013-T012_PRIMER_USO.md` y matriz de aceptación.

## P013-T013 — Candidato público nuevo y paquete verificado

**Estado:** pendiente. **Depende de:** T012 y correcciones obligatorias.
**Objetivo:** preparar el árbol exacto que se propondrá publicar tras P013.
**Rutas permitidas:** empaquetado/exportación, `docs/phase/` y área nueva acotada en su guion;
originales D214/P011/P012 solo lectura; sustitución del destino según autorización disponible.
**Criterios de aceptación:**

- Candidato por lista positiva revisada, sin Git/historia privada, credenciales, datos operativos o cachés;
  baseline pública, manifiesto y procedencia nuevos. Conservar árboles/paquetes anteriores por bytes.
- Wheel con UI/migraciones, sdist, pylock/checksums nuevos; instalar fuera del checkout y verificar uso sin Node
  y scripts con árbol exportado. Registrar versión conforme a política vigente, hashes, resultados y omisiones.
- Suites pertinentes en árbol/copia exactos: pytest, unittest, Node, tipos/build, Alembic temporal, documentación
  y verificador de distribución. Verificador/smoke bajo la autorización operativa correspondiente.
- No atribuir hashes/resultados P012 al candidato cambiado; sin publicación ni CI remota.

**Validación:** suites/artefactos indicados, diff contra base D214 y conservación de originales.
**Entregable:** `docs/phase/P013-T013_CANDIDATO.md`, manifiestos y logs saneados.

## P013-T014 — Revisión de salida y expediente de apertura actualizado

**Estado:** pendiente. **Depende de:** T013.
**Objetivo:** dictaminar criterios de P013 sobre evidencia y candidato exactos antes de cerrar.
**Rutas permitidas:** docs vigentes y `docs/phase/`; originales archivados solo lectura.
**Criterios de aceptación:**

- Cada criterio de ROADMAP tiene evidencia, alcance y dictamen; distinguir diseño, prueba sintética y uso real.
  Hallazgos obligatorios bloquean cierre y pasan a tareas acotadas.
- Contrastar árbol/paquete/docs/matriz; expediente nuevo sustituye operativamente P012/D214 sin reescribirlos.
- Enumerar parámetros y acciones remotas pendientes: owner/repo, visibilidad, identidad pública; el cierre no
  autoriza repositorio, push, CI remota, cambio de visibilidad, tag ni Release.

**Validación:** evidencia, manifiestos, diff y documentación; no repetir suites válidas sin motivo.
**Entregable:** `docs/phase/P013_REVIEW.md` y `docs/phase/P013_EXPEDIENTE_APERTURA.md`.

## P013-T015 — Cierre documental y publicación pendiente de autorización

**Estado:** pendiente. **Depende de:** T014 favorable y correcciones obligatorias completadas.
**Objetivo:** cerrar/archivar P013 y dejar preparada la apertura sin ejecutarla.
**Rutas permitidas:** docs vigentes y destino nuevo `docs/archive/phase-013/`; archivos anteriores intactos.
**Criterios de aceptación:**

- Archivar por bytes documentos/artefactos con manifiesto, resumen, revisión y registro de cierre; conservar
  snapshots/evidencia de todas las fases anteriores, incluidos resultados parciales.
- STATE/NEXT_STEPS/ROADMAP reflejan implementación, pruebas y pendientes; publicación vuelve a ser siguiente
  paso solo después de este cierre, con expediente/candidato nuevos y permisos concretos.
- Conservar D157 y modo continuo posterior D156; sin sucesora asumida, operación del harness sobre este
  repositorio, tag, commit no solicitado, push o publicación por efecto del cierre manual.

**Validación:** parsers, enlaces, presupuestos, manifiesto y diff.
**Entregable:** `docs/archive/phase-013/SUMMARY.md`, `REVIEW.md` y registro de cierre con procedencia.
