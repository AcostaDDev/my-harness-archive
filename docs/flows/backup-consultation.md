# Consulta de backups y restauraciones (D040, D202)

P012-T012 añade UI a las lecturas por id que ya ofrecía D040. No cambia el bundle, la marca persistente,
las tablas o las guardias. [Contrato y pruebas](../archive/phase-012/P012-T012_VISTA_CONSULTA.md).

1. Con escritores detenidos, el operador crea/verifica el backup o restaura en un destino nuevo con el
   procedimiento D040. La continuación UI de T003 reutiliza su restauración conservada; no repite ese paso.
2. El servicio valida el bundle y reconoce `PRAGMA user_version=0x483532`: abre SQLite con `query_only`,
   omite configuración ambiental y explícita, proyectos operativos, puertos y supervisor. Las mutaciones
   siguen rechazadas con 409 `restored_read_only`, incluso si se accede directamente a la API.
3. Tras la sesión local, la UI lee `GET /api/managed/supervisor`. `read_only_archive` procede de esa marca;
   no se deduce de agentes ausentes, `ports_configured=false`, `supervisor=false` o `project_id=null`.
   Hasta resolverla no monta páginas operativas ni `ProjectWorkspace` y no lee solicitudes pendientes.
4. La copia muestra contexto permanente de consulta. Inicio permite introducir un id del manifiesto y
   abre `/runs/:id`, codificado por el router. No hay inventario global ni lectura del manifiesto en navegador.
   Un id desconocido muestra recurso ausente; la URL puede abrirse directamente o recargarse.
5. El detalle conserva raíz/fase/tarea como contexto histórico, estado, commit y evidencia proyectada.
   Lee jobs, intentos, ciclos y eventos por páginas; los eventos conservan los cursores exactos, incluso con
   saltos de secuencia. El diff se carga bajo demanda y conserva hash/páginas. JUnit reutiliza casos paginados
   y enlace al original; los logs muestran su estado conservado/purgado/ausente bajo demanda.
6. El consumo usa `GET /metrics/attempts?run_id=…` con páginas y procedencia. No requiere `project_id`;
   null se conserva distinto de cero y modelo solicitado distinto de reportado. Un fallo de lectura muestra
   error, no un resultado vacío. Se reutilizan la presentación y los formatos del modo ordinario.
7. Los estados QUEUED/ACTIVE/RECOVERY_REQUIRED son históricos. No hay polling de ejecución: lectura inicial,
   páginas bajo demanda y recarga explícita. El sondeo de sesión/autenticación sigue independiente. La UI no
   monta permisos, recuperación, ejecución, commit, chat, configuración ni reenvío de solicitudes guardadas,
   aunque los datos anuncien acciones. Las rutas operativas directas muestran un mensaje y vuelta al archivo.
   La navegación ofrece archivo y estadísticas globales; los enlaces de run van a `/runs/:id`.
8. Cerrar el servicio elimina su clave efímera; comprobar parada, puerto y conservación del bundle y filas.
   Consultar nunca certifica muerte de escritores, libera locks ni reanuda jobs históricos.

Las lecturas reutilizan D144/D145: proyección acotada, sin seleccionar/decodificar `history_json`, reconstruir
proyección o acceder al checkout. Sin marca, `/runs/:id` conserva la redirección canónica al proyecto y el
estado vacío anterior si no hay proyecto. [Flujo operativo de run](task-run.md#lectura-del-run-d144).

## Ampliación diseñada en P013-T001

El [contrato P013](../phase/P013-T001_CONTRATO.md) y el [flujo de configuración](configuration-setup.md)
concretan el recorrido futuro sin composición previa, guardado/activación versionados, preparación y backup.
**Diseñado, no implementado:** este documento conserva el flujo vigente hasta las entregas T004–T011.
Commit documental previo al técnico; perfil/recibo confirmado antes de tareas en el carril nuevo; formatos,
jobs, snapshots y recibos existentes intactos. La aplicación guarda TOML privado fuera de checkouts;
ningún agente obtiene escritura general de configuración global. Consulta D040 no adquiere mutaciones.


## Configuración entregada en P013-T011

[D228](../DECISIONS.md#d228--p013-t011-conversión-explícita-y-backup-de-configuración),
[validación](../phase/P013-T011_COMPATIBILIDAD.md). El formato 2 añade inventario de ámbitos/revisiones/operaciones,
TOML inmutables/copias de trabajo y publicaciones parciales referenciadas, además de evidencia CLI de asistencia/
preparación. Originales bajo roots explícitos y permisos privados; conjunto revalidado antes de COMPLETE.
Intenciones/estados inciertos se conservan, sin repararlos. Formato 1 anterior sigue permitido sin configuración nueva.

La marca y UI de consulta descritas arriba permanecen. La API autenticada permite consultar global guardada y
`GET /api/managed/configuration/revisions/{scope}/{revision}` desde el bundle; no lee ni valida herramientas,
configuración original o checkout. Guardado, detección, asistencia, preparación, recuperación y activación siguen
rechazados. No hay promoción a base operativa ni publicación en las rutas locales históricas.
