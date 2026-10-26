# P013-T010 — Edición posterior manual y asistida

Fecha: 2026-10-26. Base: `81be482`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local en inglés.
**Estado: implementada con evidencia sintética; QA instalada pendiente T012.**
[D227](../DECISIONS.md#d227--p013-t010-edición-posterior-asistencia-congelada-e-impacto-conjunto),
[flujo](../flows/configuration-setup.md#edición-y-asistencia-entregadas-en-t010),
[datos](../DDBB-DIAGRAM.md#edición-y-asistencia-p013-t010).

## Resultado y motivo

El perfil ACTIVE ya no oculta el editor. Global y perfil propio permiten mantener formularios/TOML, guardar
por CAS y revisar impacto antes de activar. La ayuda IA usa la pareja activa y contenido autorizado, con
confirmación propia; un candidato de clientes no puede sustituir a quien lo propone o comprueba. Aplicar una
propuesta solo cambia el borrador local. Esto completa la gestión posterior prevista en T010 sin convertir
el chat en escritor de configuración ni cambiar trabajos ya admitidos.

La disponibilidad operativa y la del candidato guardado se exponen por separado: guardar otro borrador no
oculta tareas si la configuración activa sigue acreditada.

Global v9 se guarda como conjunto: la aplicación deriva copias de los perfiles activos con la nueva referencia
global exacta. Sus campos técnicos siguen siendo propios; no siguen catálogos/presets por nombre. Preview
muestra diff, comandos/herramientas, necesidad de preparación, reinicio y jobs; el hash sella esa información.
Activar requiere todas las referencias y barrera D118; publica pendientes para el siguiente arranque. Cancelar
comprueba versiones de todos los ámbitos de la activación pendiente y conserva activas, también si se
guardó otro borrador global durante la espera. Un borrador independiente de proyecto impide
sobrescribirlo; las derivadas de una edición global anterior sí se pueden revisar en otra preview.

## Edición y evidencia técnica

`POST /projects/{id}/configuration/edit-base` toma HEAD limpio, hashes de AGENTS/especificación/arquitectura/
decisiones y plan anterior. Devuelve candidato de edición; no guarda, prepara ni escribe Git. Datos en
`project-config-1.edit` opcional, sin convertir formatos 1–8 ni modificar el texto de versiones previas.
Un cambio de perfil requiere una actualización documental confirmada previamente; el vínculo debe coincidir
con los documentos actuales al validar. La comprobación mecánica exige cambio documental y revisión exacta;
no sustituye la revisión semántica del operador sobre la concordancia de documentos y perfil.

Cambios técnicos de perfil/comandos/herramientas/entorno/plan necesitan una preparación T008 nueva. El candidato
guardado y el plan documental sellado reemplazan la entrada de la propuesta inicial para ese recorrido posterior;
se conservan propuesta/aceptación/commit de alta, y no se repite la incorporación. Preparación usa la pareja y
política admitidas; el candidato no amplía sus permisos. Nuevas operaciones permiten otra preparación tras una
COMPLETED anterior, con la misma exclusión/journal/procesos, validación JUnit fresca y commit conciliable si hay
cambios. Una respuesta repetida no repite comandos ni commits.

Cambios exclusivos de agentes/política/global pueden reutilizar evidencia original después de verificar igualdad
técnica y de plan, herramientas/archivos/entorno. La selección usa referencia exacta o el recibo que ACTIVATE
registró para esa referencia; nunca el último recibo parecido. La nueva activación conserva el recibo original
por bytes y añade su referencia en la operación. Preparar otro candidato no sustituye la evidencia activa ni
la de un borrador revertido. Activación local precompone antes de publicar; arranque global verifica el conjunto
antes de componer runtime. Los jobs pendientes/activos impiden activar y conservan sus versiones/historiales.

## Asistencia opcional y proceso

API protegida `/configuration/assistance/preview`, `/confirm` y `/{id}/recover`:

1. Requiere global READY y autoridad activa del ámbito; nunca configura clientes mediante modelos.
2. Preview congela pareja activa/identidades D174, selección, texto del candidato, mensaje y documentos
   expresamente elegidos de la lista permitida. No infiere ni guarda. Revisor usa su modelo/esfuerzo activos;
   ejecutor global selección explícita, ejecutor local política activa. No hay fallback a la pareja candidata.
3. Confirmar con hash, clave y cuerpo exactos persiste ASSIST/propietario/intento antes de invocar. Se crea un
   directorio privado nuevo bajo estado, fuera de configuración/checkouts; rutas sin enlaces y permisos 0700.
   Revisor tiene transporte de lectura y esquema tipado; ejecutor escritura en esa área privada. Para Codex
   escritor se inicializa solo allí un Git sintético, sin saltar su guardia de confianza/repositorio.
4. El journal JSON de la operación conserva prompt/esquema/contexto, intención del proceso, identidad de grupo
   antes de GO, captura y cierre. No fabrica run ni propietario de preparación; los artefactos privados del
   adaptador conservan streams. El revisor devuelve TOML/motivo/preguntas y el ejecutor observaciones; no ejecuta
   comandos/red/instalaciones ni obtiene escritura general del TOML. Preparar el proyecto sigue T008 aparte.
5. Resultado validado se muestra con su evidencia. Aplicar solo cambia el borrador de la pestaña; validación,
   diff/confirmación de guardado y activación siguen siendo pasos independientes. La fuente se comprueba tras
   el turno; una alteración externa no se adopta como autoridad.
6. Respuesta perdida/reenvío devuelve la operación original incluso tras reinicio. Ningún GET/montaje/arranque
   relanza un turno. Incertidumbre conserva RECOVERY_REQUIRED; recuperación exige declaración de escritores
   detenidos y liveness de propietario/grupo compatible, cierra sin replay. INTENDED de asistencia no cambia
   autoridad ni impide checkpoints de jobs admitidos, aunque bloquea otras mutaciones de configuración.

UI global/por proyecto comparte asistencia, confirmaciones y sobre persistido por ámbito en la pestaña, con
reenvío solo explícito. Textos propios en/es, controles nativos y borradores/base conservados ante conflicto.
Contexto del proyecto según el layout del servidor, sin selector arbitrario de archivos. Consulta restaurada
rechaza mutaciones antes de leer rutas/descubrir clientes; importación/backup integrado siguen en T011.

## Validación

- Backend sintético en las dos entradas Go de T009: revisión de agentes sin reinicio, perfil actualizado tras
  commit documental, nuevo plan/preparación, global derivado con reinicio/cancelación conjuntos, revisión de
  sus derivadas, barrera por job admitido y conservación de snapshots/recibos. Cambio de perfil sin actualización
  documental rechazado; plan distinto no reutiliza evidencia; borrador revertido usa evidencia activa.
- Asistencia con agentes falsos: preview pasiva, fuente activa frente a cliente candidato, área privada,
  reenvío/key conflict, preview obsoleta, contexto no autorizado, CSRF/Origin y recuperación sin replay.
  Job propio sigue usando autoridad congelada mientras se atiende una asistencia.
- Cuatro transportes CLI **sintéticos**, Codex/Claude como revisor/ejecutor: flags de lectura/escritura,
  esquema del lector, intención/spawn/captura/grupo detenido y una sola invocación con replay. La respuesta
  genérica del fixture no se acepta como propuesta de configuración: se verifica su rechazo estructural.
- Suite completa offline: **2000 pytest correctos y 29 subtests, dos opt-in omitidas**. Primera pasada: 1991
  correctos/29 subtests y un fallo del catálogo por un diagnóstico interno de dos palabras sin catalogar; se
  sustituyó por el diagnóstico existente y la segunda suite completa pasó. No hubo llamadas a proveedores.
  La suite completa precede a los últimos casos de transporte/plan y selección del recibo en la vista;
  **152 regresiones de configuración/catálogo** posteriores correctas; **90 sobre recibos/vistas** después de
  comprobar reversión del borrador y selección de evidencia; **69 finales sobre edición/API/alta** después
  de separar disponibilidad activa/candidata y cubrir cancelación con borrador global posterior. Las pruebas
  incluyen los 26 casos parametrizados de T010; no se suman como si fueran ejecuciones de proveedores.
- **151 Node y 8 unittest correctos**. Casos UI propios en/es: perfil activo editable, asistencia autorizada,
  aplicación solo al borrador y respuesta perdida con sobre/clave exactos y sin reenvío automático. Se amplió
  el transporte sintético de recuperación existente para distinguir SAVE de ASSIST mediante su GET pasivo.
- Tipos/build correctos, aviso conocido de chunks grandes; OpenAPI/tipos regenerados y paridad con
  `create_app().openapi()`. Alembic `upgrade head` y `check` en SQLite temporal sin diferencias: **0027, 54 tablas**.
  Sin modelos, migración, dependencia ni versión de producto nueva.
- Checks documentales reproducibles: [script T010](P013-T010_CHECK_DOCS.py), parsers/enlaces/presupuestos,
  **13 fases, 15 tareas, 227 decisiones y 853 enlaces/anclas en diez documentos**, presupuestos correctos
  y cuerpos D001–D226 intactos. Mermaid de configuración/datos: **tres flowcharts, dos secuencias y trece ER**,
  cero fallos con el checker archivado citado en T001; parseo con stub DOMPurify, sin renderizado/QA visual.
  `git diff --check`, revisión de diff y conservación de `docs/archive/`/`docs/public/`.

Los fallos iniciales de implementación se resolvieron antes de cerrar: expansión global recibía una lista en
vez de un cambio y se restituyó el tipo de rechazo de la preparación; 81 regresiones pasaron después. Los
primeros cuatro tests nuevos de transporte omitían el USER explícito exigido por D024; corregido solo el fixture,
los cuatro pasaron con la política existente. La revisión también acotó la selección de recibos a referencias/
evidencia de activación, evitando que una preparación posterior reemplazase evidencia previa por semejanza.

## Límites y siguiente tarea

Sin proveedores reales, autenticación/credenciales, descargas, navegador/QA visual, servicio instalado, smokes
ni harness sobre este repositorio. No se modifica configuración global del equipo, bases/fixtures privados,
candidatos/paquetes D214/P011/P012, tags, push, CI remota ni publicación. Contención cooperativa existente:
no se acredita aislamiento de sistema operativo ni calidad de modelos con estas pruebas.

No hubo contradicciones de diseño pendientes de HITL; las representaciones concretan el contrato T001 y D215.
Siguiente: **P013-T011**, compatibilidad/importación/recuperación y backup autocontenido. T012 acreditará
recorrido instalado/QA y actualizará documentación de usuario; T013–T015, candidato, revisión y cierre nuevos.
