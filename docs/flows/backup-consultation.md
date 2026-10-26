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
