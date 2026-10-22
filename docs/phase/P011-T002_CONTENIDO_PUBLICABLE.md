# P011-T002 — Licencia y revisión del contenido publicable

Fecha: 2026-10-22. Base: `b31b720e3d861560bac1b349c7b7fc960511663d`, checkout limpio al iniciar.
Tarea completada en su alcance de revisión estática del origen y preparación de derechos/avisos.
**No hay candidato publicable ni auditoría final de su árbol/historial/paquete.** T019 y T003–T017 conservan
sus entregas; no se publica este historial ni se reutilizan los paquetes locales antiguos. Decisión: [D160](../DECISIONS.md#d160--p011-t002-licencia-mit-y-frontera-del-contenido-publicable).

## Autoridad, licencia y soporte

El encargo autoriza ejecutar la siguiente tarea y terminar con commit local en inglés. En el HITL, el usuario
delega explícitamente la elección de licencia y canal, y confirma David Acosta como nombre público del titular.
Se elige **MIT**, con copyright 2026 David Acosta: términos breves que permiten reutilizar/distribuir conservando
el aviso. No se incluye su correo en los archivos públicos ni se inventa una entidad o una cesión de terceros.
La delegación expresa resuelve la reserva de elección humana de T002 antes de redactar términos/metadatos.

Entregados: `LICENSE`, `NOTICE.md`, `NOTICE-THIRD-PARTY.md`, `CONTRIBUTING.md`, `SECURITY.md`, licencia/autor
en `pyproject.toml` y licencia en `frontend/package.json`. Sin cambio de versión o dependencias. Se añaden
exclusiones preventivas de claves/certificados y variantes SQLite a `.gitignore`; no se elimina nada rastreado.
`.gitattributes` permite el espacio final original de un aviso MPL solo en NOTICE-THIRD-PARTY, conservando
su texto upstream sin desactivar controles de whitespace del resto del repositorio.

Canal elegido: **GitHub private vulnerability reporting** del futuro repositorio público. SECURITY explica
la ruta y el fallback de pedir un canal privado mediante issue sin detalles. No hay URL/contacto inventado,
SLA, bounty, soporte de ramas publicado ni reporte enviado. El propietario debe habilitar/verificar el canal
al preparar la apertura: escribir SECURITY no lo activa. T015/T017 lo incluyen en el expediente remoto y no
pueden declarar el canal operativo hasta comprobarlo, sin cambiar ahora ajustes remotos.

Consultas de solo lectura a fuentes primarias, necesarias tras la delegación del usuario:
[texto MIT de OSI](https://opensource.org/license/mit),
[reporte privado de GitHub](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately) y
[activación por el propietario](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).
El escaneo de repositorio/dependencias/archivos comprimidos es local; no se enviaron contenidos del repositorio.
Esta consulta documental es la única red usada; no hubo descargas/instalaciones o ejecución remota.

## Método y cobertura del origen privado

[Script reproducible](P011-T002_audit.py), biblioteca estándar Python y lecturas Git locales, sin importar el
producto. [Inventario por archivo](P011-T002_INVENTARIO.tsv) con ruta, SHA-256, modo, disposición, propietaria,
categorías y condición. Es evidencia **privada**, excluida del corte, y no un manifiesto de exportación aprobado.

```sh
python3 docs/phase/P011-T002_audit.py --revision b31b720 \
  --inventory docs/phase/P011-T002_INVENTARIO.tsv \
  --dependencies docs/phase/P011-T002_DEPENDENCIAS.tsv \
  --notices NOTICE-THIRD-PARTY.md > /tmp/my-harness-p011-t002-audit.json
```

Los argumentos de generación escriben solo los destinos indicados; sin ellos, el script solo lee y emite JSON
saneado, sin valores coincidentes. El inventario de origen fija la revisión indicada; las dependencias/avisos
usan los locks y metadatos locales actuales, comprobando versiones npm. El historial usa los refs alcanzables
**al ejecutarlo**, y `dist/` los artefactos entonces presentes; sus conteos/hashes no se atribuyen a una revisión
histórica distinta. Repetir posteriormente no implica igualdad de refs/cachés/artefactos.

| Superficie | Cobertura y resultado de esta ejecución |
|---|---|
| Árbol de base | 690 archivos, 9.900.157 bytes; 689 modo 100644 y uno 100755, sin symlinks/gitlinks/binarios gráficos rastreados |
| Historial alcanzable | 4.009 objetos únicos, 94.942.901 bytes: 145 commits, 1.384 trees, 2.480 blobs; cuatro refs (main, origin/main y dos checkpoints Codex), sin tags |
| Contenido Git | Todos los blobs, trees y commits alcanzables leídos por `cat-file --batch`, incluidos blobs borrados/reemplazados; commits incluyen mensajes/identidades. Una identidad autor/committer distinta, sin copiar su valor |
| Nombres históricos | `git log --all --format= --name-only -z`; sin nombres de credencial/estado de las extensiones detectadas; el árbol actual tampoco los tiene |
| Detectores | Claves privadas, tokens de proveedores/GitHub/Slack/Google/AWS, JWT, URL con credencial, literales de credencial, hogares personales, correos y referencias documentales internas |
| Secretos de alta especificidad | Cero coincidencias de los patrones de claves/tokens/JWT/URL con credencial, tanto en árbol como en historia |
| Literales genéricos | Seis coincidencias en tres archivos actuales; 36 en 13 blobs históricos. Revisión de las funciones de prueba/contexto: centinelas sintéticos de no exposición de entorno y preparación Codex; sin credenciales reales identificadas |
| Privacidad/contexto | Árbol: 69 referencias de hogar en 27 archivos, 47 correos en 23 y 4.805 candidatos de referencias internas en 359. Historia: 492/534/95.171 respectivamente; son coincidencias por objeto, no cuentas/personas/documentos únicos |
| Cambios de T002 | Lectura adicional del contenido nuevo/modificado, metadatos y avisos; copyright autorizado y correos/atribuciones públicos de terceros conservados; sin valores sensibles nuevos identificados |

No se leen entorno, auth de proveedores, configuración Git/global, estado operativo ignorado, backups/runs reales
o proyectos externos. La lectura de `dist/` y de licencias/METADATA instalados es una excepción explícita de
evidencia estática, sin ejecutar o instalar sus paquetes. Quedan fuera reflogs, objetos inalcanzables, LFS remoto,
refs no presentes localmente y otros repositorios; no se garantiza detectar secretos arbitrarios, codificados o
con formatos desconocidos. No hay análisis de entropía, validación de credenciales ni dictamen jurídico universal.

## Hallazgos y disposición del corte inicial

El historial privado **no es publicable por este informe**. Los hallazgos de rutas/identidad/evidencia tienen
resolución explícita en D157/D160: conservarlos privados y construir un árbol revisado con Git nuevo. No borrar
refs, reescribir commits o asumir que `.gitignore`/borrar archivos de un clon sanea su historia.

| Hallazgo/grupo | Disposición y responsable |
|---|---|
| `docs/**` privados, fases/ADR/archivos/evidencia y guiones `examples/first_use/**`, `provider_matrix/**` | 244 archivos excluidos del corte inicial; originales intactos. T014 escribe contexto técnico público nuevo, sin enlaces privados imprescindibles; no se prohíbe la futura evolución pública de docs |
| `tests/fixtures/legacy/**` | 99 archivos exclusivos a retirar en T019 tras comprobar dependencias. Incluyen un hogar personal en baseline y streams sintéticos: no reutilizarlos en el candidato |
| Instrucciones raíz/README y `tests/fixtures/cli_help/**` | Siete archivos a sustituir: cuatro de contexto público nuevo (T014) y tres de ayudas reales de CLI (T006/T012). Que una ayuda sea pública no prueba por sí solo derecho a relicenciarla; usar cobertura sintética en el corte, conservando estos originales privados |
| Resto del árbol | 340 archivos candidatos a revisión posterior, cero archivos aprobados para copiar automáticamente. T001 sigue identificando módulos/entrypoints legacy exclusivos y piezas compartidas; T019 determina su eliminación/reubicación antes de traducir o empaquetar |
| Hogares fuera de docs | Instrucciones raíz y guiones históricos excluidos/sustituidos; baseline legacy a T019. `examples/local_config.example.toml` contiene un placeholder de usuario, no una cuenta real: ejemplo sintético nuevo en T014 |
| Correos e identidades | Mayoritariamente ejemplos/pruebas sintéticos y evidencia histórica; no sustituir ciegamente valores técnicos. La identidad pública elegida en LICENSE está autorizada; no copiar identidad/configuración Git del origen al candidato |
| DNNN, fases y enlaces internos en código/UI/tests | Candidatos, con falsos positivos técnicos; T003–T006/T014 proporcionan explicación pública autocontenida. No renombrar protocolos ni alterar fuentes congeladas por eliminar un identificador |
| Extracción histórica de reglas de perfil/proveedores | No se lee ni copia ReferenceProject. El perfil contiene comandos de stack, no datos operativos; T019/T003 contrastan necesidad y contexto público. Streams propios identificados como sintéticos conservan su tratamiento T001 |

Lista positiva para T015: partir de **rutas exactas** del inventario, resolver disposición/hallazgos de cada una
contra los bytes finales y registrar privadamente origen/destino/hash. Los nuevos `LICENSE`, `NOTICE*`,
`CONTRIBUTING.md` y `SECURITY.md` son entradas candidatas adicionales, junto con docs nuevas T014 y workflows T015;
sus hashes finales se fijan allí. Nada queda permitido por un glob recursivo ni porque no lo detecte el scanner.

Excluir además `.git`/objects/refs/tags/checkpoints, `.local`, `.harness`, worktrees/submódulos con datos Git,
venv, node_modules, cachés, SQLite/backups/runs/credenciales, build/dist antiguos y artefactos no revisados.
Antes de abrir, comprobar ocultos, symlinks, enlaces/anclas, suficiencia de docs para forks/agentes y ausencia de
referencias privadas también en JS/CSS generados. Manifiesto público sin hashes de commits/rutas privadas;
correspondencia privada separada. Este informe/inventarios/script no se exportan como documentación pública.

## Atribuciones y dependencias

[Inventario de dependencias](P011-T002_DEPENDENCIAS.tsv): 247 entradas, separadas por ámbito y evidencia:
29 dependencias del lock Python, 199 del lock frontend, 17 de receta Django, un backend de build y un TypeScript
de fixture/receta. No se importan módulos para obtener metadatos ni se ejecutan gestores de paquetes.

- Python: METADATA de 28 versiones instaladas exactas; MIT, BSD-2/3-Clause, Apache-2.0, PSF-2.0 y MPL-2.0
  (certifi). Colorama de plataforma no instalada carece de evidencia local de términos. Son dependencias
  externas, no fuentes copiadas en el wheel del harness; conservar sus propios avisos al instalarlas/distribuirlas.
- Frontend: 123 entradas runtime y 76 de desarrollo/build. El lock declara MIT, Apache-2.0, ISC, BSD-2/3-Clause,
  PSF-2.0, Unlicense y opciones compuestas; build añade MPL-2.0/Python-2.0/CC0 como alternativas declaradas.
  Khroma 2.1.0 carece de `license` en lock/package.json: el archivo local `license` acredita MIT. No se cambia lock.
- `NOTICE-THIRD-PARTY.md` conserva 129 textos de aviso (69 contenidos distintos) de todas las 123 entradas
  runtime: 127 archivos de licencia/avisos más las dos secciones MIT completas en README de fastdom/strictdom.
  Se preservan copyrights/textos de upstream, incluidos los dos textos alternativos de DOMPurify. SHA-256 del
  lock y enlaces por contenido permiten comprobar procedencia y evitar atribuir todo el bundle al MIT propio.
- Hay 19 entradas sin términos de versión exacta disponibles localmente: colorama, 17 paquetes de receta Django
  y uv_build. Se declara la ausencia en vez de asignarles una licencia de memoria. No están vendorizados: las
  recetas descargan/instalan sus distribuciones aparte, y el backend es herramienta de build. T015 documentará
  su evidencia y conservará sus avisos si los incluye en cualquier artefacto público, sin revalidarlos mediante red
  o instalar por efecto de esta tarea. El inventario no certifica esos términos ni acredita su redistribución.
- No hay imágenes/fuentes binarias rastreadas. Los assets compilados pueden incluir fuentes KaTeX/otros
  recursos transitivos: T015 debe contrastar asset → paquete/términos/avisos del candidato exacto, incluyendo
  fuentes y licencias de código incorporado por el bundler. Los avisos del origen no sustituyen esa comprobación.

No se borra ni traduce una atribución upstream. No se añade una dependencia, logo/marca o contacto. Los avisos
son material público nuevo candidato; el censo privado no es su sustituto. No se afirma compatibilidad jurídica
de toda posible combinación de dependencias o distribución futura.

## Wheel/sdist previstos y archivos locales existentes

Revisión de `pyproject.toml`, locks y `scripts/build_distribution.py` **sin ejecutarlo**: el staging copia
pyproject y `src/` sin pycache/pyc, y `frontend/dist` a `src/harness_local/web`; construye wheel/sdist con uv.
No copia la documentación privada ni examples/tests/.git. Sí puede copiar archivos no rastreados bajo src y
todos los assets de frontend/dist: T015 impondrá lista/manifiesto y comprobación de contenido exacto.

El staging actual **no copia LICENSE/NOTICE**. Se añade `license = "MIT"` y autor a metadatos fuente, sin fingir
que el script empaqueta ya los avisos; integrar los archivos en el staging y fijar recursos/metadatos coherentes
es trabajo explícito de T015, antes de distribuir. No se declara todavía `license-files` obligatorio apuntando
a un archivo ausente del staging actual. La coherencia final de lock/metadatos npm también se revisa allí.

Los dos comprimidos locales preexistentes se abren solo en lectura, sin extraer o ejecutar miembros:

| Artefacto anterior, no candidato | SHA-256 | Archivos/registros |
|---|---|---|
| `dist/harness_local-0.1.0-py3-none-any.whl` | `a97c4995a4ccee1c0e6baafd43b1408441ebaabc2c79202ae29c2eb8861768d6` | 109 archivos, 123 entradas ZIP contando directorios |
| `dist/harness_local-0.1.0.tar.gz` | `a2a43af3525c5f5951b419f85b1293ffb707b005166725e56c4af930d42446fe` | 108 archivos, 123 entradas tar contando directorios |

Ambos contienen código legacy/observación y cuatro candidatos de referencias internas; no contienen
LICENSE/NOTICE y el sdist incluye `pyproject.toml.orig`. Sin nombres absolutos/traversal ni coincidencias de
claves/tokens detectadas. Son artefactos locales antiguos, no evidencia de los bytes actuales ni el candidato
P011. Se excluyen, sin borrarlos/reconstruirlos ni trasladarles el dictamen P010. T015 construye el candidato
y T016 verifica su contenido exacto; T017 emite dictamen de preparación pública.

## Validación y límites de entrega

Checks estáticos: cobertura/hash/modes del inventario, escaneo completo local descrito, clasificación de las
coincidencias, procedencia/igualdad de los 129 avisos, parseo TOML/JSON/Python, selección sintética de detectores,
reglas ignore sobre nombres sintéticos, enlaces/anclas, índice/estructura ADR y presupuestos D088; integridad
de fases cerradas/recetas/snapshots, diff revisado y `git diff --check` antes del commit. Resultados finales
de esta entrega:

| Check | Resultado |
|---|---|
| Conjunto de rutas y SHA-256 contra `git ls-tree`/blobs de base | 690/690 coinciden, sin duplicados o ausencias |
| Regeneración de censo/avisos con las versiones locales comprobadas | TSV y Markdown idénticos; 247 entradas, 123 runtime frontend y 69 hashes de contenido |
| Parseo de pyproject/package.json/script | Correcto; MIT y titular esperados |
| Selección de detectores con muestras sintéticas solo en memoria | Nueve categorías de secreto positivas y texto ordinario negativo |
| `git check-ignore --quiet --no-index` sobre nombres sintéticos | 13 casos ignorados, sin crear credenciales o estado |
| Escaneo del contenido nuevo/modificado | Sin categorías de secreto detectadas; avisos públicos upstream conservados |
| Regex D088 obtenidas por AST, sin importar/ejecutar el producto | 160 ADR con estado/índice, 19 tareas (dos completadas), presupuestos STATE/base/NEXT_STEPS e instrucciones correctos |
| Enlaces y anclas locales en Markdown de esta tarea/seguimiento | 591 correctos |
| Diff contra base de src/tests/scripts/examples/archive, UI fuente/tests/OpenAPI y locks | Sin cambios; cuerpos D001–D159 idénticos, índice ampliado aparte |
| `git diff --check` y revisión del diff | Correctos, alcance de T002; excepción de espacio final solo para avisos upstream, conservados por contenido |

No se ejecutan suites unittest/pytest/Node, Alembic, builds, smokes, servicios, CLI de proveedores/agentes o
el harness, ni se instala nada. El producto no cambia comportamiento, modelos, API o flujos. Sin nueva copia,
repositorio/tag/push/Release/publicación, modificación global o reescritura de historia. La consulta documental
web ya descrita no constituye un escaneo remoto. Tras el commit, siguiente tarea **P011-T019**; no se encadena.
