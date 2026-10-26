# P013-T008 — Preparación y comprobación acotadas con el ejecutor

Fecha: 2026-10-26. Base: `4c6c0fa`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local en inglés.
Implementado el carril genérico de servicio/API; **alta/guardado documental y activación/UI integrados pendientes T009**.
[D225](../DECISIONS.md#d225--p013-t008-preparación-genérica-confirmada-y-recibo-propio),
[contrato §8](P013-T001_CONTRATO.md#8-preparación-recibos-y-edición-asistida),
[flujo](../flows/configuration-setup.md#preparación-genérica-entregada-en-t008) y
[datos](../DDBB-DIAGRAM.md#preparación-genérica-p013-t008).

## Resultado y motivo

`project-profile-preparation-1` permite preparar/comprobar un perfil propio sin fabricar una receta Django o
TypeScript. Reutiliza intención, lock de checkout, lease, pasos, procesos, eventos, cancelación y recuperación de
D119; las recetas siguen por su contrato anterior. Sin tablas/migraciones/dependencias nuevas ni cambios en
formatos/hashes de TOML 1–8, historiales, recibos antiguos o fuentes de recetas.

El candidato del revisor puede incluir `preparation_plan` separado del perfil: `write_paths` (archivos literales
o prefijos `directorio/**`), `local_paths` (privados e ignorados), `environment_paths` (entorno estable a acreditar),
dependencias `{name, version, lock_path, sha256}`, destinos HTTPS, autorización de scripts, instrucciones y
selección de modelo/esfuerzo/motivo del ejecutor. La política permitida entra en el contexto congelado. El parser
rechaza rutas globales/Git/documentales/sensibles, comodines generales, dependencias sin hash y selecciones fuera
de política. Propuestas anteriores sin plan conservan lectura/adopción; preparar exige una propuesta nueva que
lo incluya. No se actualizan a posteriori los turnos congelados.

La preview sella configuración `project-config-1` guardada VALIDATED y global activa compatibles, propuesta
ACCEPTED, herramientas presentes/resueltas por bytes, comandos/entorno/cwd/límites, red/scripts/dependencias,
ámbito, identidad y contenido del checkout. La selección del ejecutor procede del revisor; el request no puede
sustituir argv, herramientas ni permisos. Locks existentes se comprueban antes de confirmar; uno nuevo o sustituido exige su ruta literal autorizada
y hash esperado visible, y se verifica después del ejecutor antes de comandos nativos y commit. Herramienta base
ausente bloquea; no se descarga ni descubre automáticamente. Si aún falta la regla de ignore, el plan debe autorizar `.gitignore`; antes del commit se comprueba que todo
archivo técnico entre en Git y que los directorios privados queden ignorados. La versión/requisito declarado está visible en la
propuesta; su acreditación funcional procede de las comprobaciones del perfil y de los resultados conservados,
sin interpretar semánticamente cualquier texto libre del requisito.

Antes de preparar exige operación documental COMPLETED, sus documentos finales, P001 adoptada y hash de perfil
sellado como `profile_proposal_sha256` en su preview. Primera preparación sobre su HEAD limpio. Este handoff se
implementará en T009: las pruebas T008 lo siembran expresamente sobre Git/SQLite sintéticos. T007 aún bloquea el
commit documental de IntakeContext; no se afirma un recorrido de alta v9 ya utilizable de extremo a extremo.
Se concreta así el límite entre T008 y T009 de T001/D218, sin invertir el orden documental → técnico → activación.
No quedaron ambigüedades de diseño que requirieran HITL.

## Ejecución y evidencia

Confirmación literal/hash/motivo/clave, CAS y replay comparten la barrera existente de confirmación/admisión.
GET/preview no invocan CLI ni comandos del stack. Tras confirmar, el worker reclama lease y verifica configuración,
identidad, herramientas/enlaces, HEAD/índice, documentos y snapshot antes de cada paso. El harness crea HOME/TMPDIR
privados declarados; el ejecutor de la pareja activa prepara archivos dentro del ámbito y recibe instrucciones de
no ejecutar comandos, Git, red ni editar configuración/documentos. Harness ejecuta después los comandos exactos
del perfil mediante `preparation-commands-1`, sin shell, herencia de entorno ni retry. HOME/TMPDIR/cachés nativos
deben estar dentro del área local confirmada e ignorada; overrides no pueden escapar.

El ejecutor recibe solo entradas técnicas necesarias, sin el TOML privado de clientes ni el inventario completo
de hashes del workspace. Los enlaces del entorno solo pueden resolver dentro del ámbito o a herramientas
explícitas acreditadas por bytes; otros destinos externos bloquean. El adaptador CLI liga un journal propio al paso de preparación. CLI y nativos persisten intención/identidad/grupo
antes de GO, con `preparation_id` y sin run/job/attempt ficticios. La cancelación se sondea durante la CLI; timeout/
cancelación detienen/recolectan el grupo propio. Las guardias posteriores conservan bytes fuera de alcance y
rechazan cambios documentales/Git; cambios de modelos no sortean paridad. JUnit reutiliza captura segura y fresca,
requiere casos correctos y rechaza fallo, XML inseguro o informe obsoleto.

La frontera continúa siendo nativa/cooperativa según D218 y ARCHITECTURE: un argv exacto puede ejecutar código
con UID del servicio; destinos HTTPS/scripts declarados no constituyen firewall ni aislamiento de filesystem.
No se añade terminal, sudo, escritura de TOML global ni ajustes del equipo. La preview/confirmación autorizan el
plan exacto y offline nunca cambia a red al fallar. Los límites del adaptador CLI original permanecen vigentes.

Al finalizar valida alcance/contenido, sella intención de commit técnico y usa CAS de HEAD/índice. Con cambio
versionado emite commit conciliable; sin cambio conserva HEAD, sin commit vacío. Recibo ligado a operación/plan,
configuración/perfil/comandos, herramientas/ruta/enlace/hash, archivos protegidos y conjunto completo, entorno
estable, idiomas, HEAD/commit y resultados/JUnit. Código ordinario y logs/reportes/home/temp transitorios no
invalidan por sí solos la evidencia; cambios de entorno/protegidos/herramientas/configuración sí bloquean.
`verify_configuration` entrega una primitiva del servicio para T009; emitir recibo no activa ni compone runtime
de tareas. La configuración original y los recibos se conservan inmutables.

Fallo/interrupción/cancelación conserva journal/bytes sin recibo. No hay replay de comandos/red por reiniciar o
repetir POST. Sucesor con confirmación nueva, escritor/grupos detenidos y prefijo DONE idéntico; un efecto parcial
no acreditado bloquea, sin limpieza automática. La conciliación de commit conserva hash/autor/fecha y no repite
comandos. Las reservas inciertas mantienen cerrada la admisión.

## API y paridad

Mismas rutas `/projects/{p}/preparation` y `/preparations/{id}`. Preview/confirmación admiten DTO genérico estricto,
separado del de recetas mediante `contract`; exige revisión/hash de configuración y propuesta, versión de registro,
modo y, al confirmar, `confirmed: true` y motivo. Desconocidos/forma inválida → 422; conflictos → 409 con diagnóstico
propio en/es. Sesión local, Host/Origin y CSRF conservados; cancel/confirm-stopped siguen CAS/idempotentes. Lectura
verifica la referencia guardada antes de afirmar prepared. OpenAPI y tipos regenerados; `recipe` admite null en
plan genérico. Sin componentes UI nuevos (T009), sin migración ni segunda autoridad TOML en SQLite.

## Validación

- Suite completa `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 4`: **1951 correctos y
  29 subtests**, **dos opt-in omitidas**, sin fallos. Concurrencia limitada para evitar saturar los procesos
  falsos con timeout de 0,2 s. Avisos conocidos de TestClient y ZIP duplicado deliberado. Esta suite precede
  a los últimos ajustes acotados de locks generados, enlaces explícitos de herramientas y minimización del
  contexto del ejecutor; esos ajustes se verifican con la regresión focalizada final, sin repetir toda la suite.
- Primera suite con concurrencia automática: 1943 correctos, 29 subtests, dos opt-in omitidas y cuatro fallos.
  Uno era la búsqueda textual de «reports» dentro de prompts al comprobar ausencia de campos JUnit legacy:
  ahora comprueba las claves serializadas de las entradas, conservando round-trip y formato 4. Otro pedía
  catalogar dos invariantes nuevos, añadidos al listado técnico con categoría `invariant`. Dos timeouts
  terminaban antes de que arrancara el proceso falso bajo carga. **18 regresiones en serie correctas** tras
  corregir los dos primeros casos; la suite completa posterior con cuatro workers también pasa los timeouts.
- Regresión focalizada final sobre el código definitivo: **38 correctos**. Cobertura: plan/propuesta desde ambas entradas,
  archivos Go y herramienta sintética ajenos a recetas, preview pasiva, CAS/replay/confirmación, guardias de
  configuración/documentos/herramientas/HEAD/índice/configuración y refs Git, ámbito y datos inválidos, red
  rechazada sin destinos, fallos con evidencia parcial, locks generados por hash, entorno estable/transitorio,
  alias de herramientas y rechazo externo, JUnit fallido/obsoleto, prefijo acreditado, lease/propietario incierto,
  cancelación/timeout y conciliación sin repetir comandos. CLI falsas Codex/Claude registran procesos sin
  run/attempt, incluida preparación sin cambios versionados. TestClient verifica sesión, Origin/CSRF, DTO
  estricto, clave requerida y reenvío exacto. El fixture siembra explícitamente el handoff T009 pendiente.
- **8 unittest y 136 Node correctos**. OpenAPI exportado, tipos regenerados; tipos y build correctos, con aviso
  conocido de chunks grandes. Sin componentes UI nuevos; integración/QA visual pendientes T009/T012.
- Alembic `upgrade head` y `check` en SQLite temporal: sin diferencias, **54 tablas** de producto. Sin migración
  ni modelos nuevos. Formatos/fuentes de recetas e historia anterior intactos.
- Parsers: **13 fases, 15 tareas y 225 decisiones**; **830 enlaces/anclas en 13 documentos** y presupuestos D088 correctos.
  D001–D224 intactas por comparación con HEAD; en/es con el mismo conjunto de claves. Mermaid del flujo de
  configuración y DDBB: **tres flowcharts, dos secuencias y trece ER**, cero errores con el checker archivado
  citado por T001. Solo sintaxis/stub DOMPurify, sin renderizado ni QA visual. `git diff --check` correcto y diff
  revisado antes del commit. Snapshots/docs archivados y baseline pública sin cambios.

## Límites y siguiente tarea

Archivos/Git/SQLite temporales, ejecutores falsos y herramientas Go sintéticas. El transporte usa procesos falsos
de Codex/Claude; no se lanzan proveedores/modelos, descargas, servicios instalados, navegador/QA visual, smokes,
harness sobre este checkout, red, bases privadas ni cambios globales del equipo. Sin wheel/candidato nuevo,
CI remota, push, tag o publicación. P001–P012/D214 y sus artefactos intactos. T009 debe unir la nueva carpeta/commit
raíz o B, el guardado de configuración, esta preparación y activación confirmada con interfaz en/es.
