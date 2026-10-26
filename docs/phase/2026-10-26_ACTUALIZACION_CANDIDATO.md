# Actualización local del candidato público tras la corrección de CI

Fecha: 2026-10-26. Encargo del usuario: actualizar `my_harness_dist` con la corrección de mantenimiento Git y
su regresión. Decisión: D214. Commit documental posterior autorizado por el usuario. Sin fase nueva, push,
CI remota ni publicación en esta tarea.

Este suplemento actualiza la identidad del árbol del
[expediente de apertura P012](../archive/phase-012/P012_EXPEDIENTE_APERTURA.md). Su procedimiento remoto y sus
permisos pendientes siguen vigentes, pero el árbol corregido usa el manifiesto de este suplemento. El expediente
y los manifiestos originales permanecen congelados como evidencia del candidato anterior.

## Identidad y alcance

- Fuente exacta: commit `08f27bcdaae3d2b2b9c197a071976f8ee6a46def`.
- Destino actualizado: `$HOME/Documents/projects/my_harness_dist`, sin Git ni symlinks.
- Original P012 conservado en `$HOME/Documents/projects/my_harness_dist_p012_cf191a40`: 401 archivos,
  5.480.755 bytes, manifiesto `cf191a40914095aeb3fbbeea0e6485878cc3218754361fa78d314b87dc19362a`.
- Nuevo árbol: **401 archivos / 5.481.629 bytes**; manifiesto público SHA-256
  **`5ef17ff3043d1b5842608528fb272e5b9184ef71a5e5382d5fd781a9954d4c55`**.
- [Manifiesto público nuevo](2026-10-26_CANDIDATO_MANIFIESTO_PUBLICO.sha256),
  [correspondencia privada](2026-10-26_CANDIDATO_MANIFIESTO_PRIVADO.tsv) y
  [diff con el original](2026-10-26_CANDIDATO_DIFF.json).
- Solo cambia `tests/product/test_project_onboarding.py`: supresión de mantenimiento automático por invocación
  y regresión Trace2. **400 archivos idénticos; cero añadidos o eliminados; modos conservados.**
- Los 25 archivos de documentación pública y todos los archivos de producto, frontend, dependencias, CI y
  empaquetado conservan sus bytes. No se copia documentación privada ni historia Git al candidato.

## Reproducción

El [adaptador local](2026-10-26_REFRESH_PUBLIC_CANDIDATE.py) carga el exportador congelado de P012, conserva su
lista positiva y sus controles y ajusta únicamente su raíz de lectura a este repositorio. No edita el archivo.
Desde la raíz, elegir destinos nuevos para el árbol y los dos manifiestos:

```sh
python3 docs/phase/2026-10-26_REFRESH_PUBLIC_CANDIDATE.py \
  --revision 08f27bcdaae3d2b2b9c197a071976f8ee6a46def \
  --out <destino-nuevo> \
  --private-manifest <manifiesto-privado-nuevo> \
  --public-manifest <manifiesto-publico-nuevo>
```

La salida debe indicar 401 archivos, 5.481.629 bytes, el hash completo anterior y cero problemas. Antes de
cualquier operación remota, comparar lista exacta de archivos/directorios, bytes y modos del árbol actual con
esta nueva exportación, sin tolerar extras, Git ni symlinks. El manifiesto privado no se publica.

## Verificación y sustitución

- Antes de actualizar, el original P012 se contrastó con sus manifiestos público y privado: rutas exactas,
  bytes, modos y ausencia de symlinks correctos.
- Exportación nueva por lista positiva: cero problemas; diff acotado al archivo de pruebas previsto.
- Pruebas en una copia aislada del candidato, con dependencias instaladas offline desde la caché existente;
  ni `.venv`, cachés ni resultados de las pruebas entran en el árbol final.
- Primer ensayo completo: **40 fallidas, 1721 pasadas, 2 omitidas y 29 subtests pasados** en 136,18 s.
  La copia de verificación carecía de `.local/npm-cache/_cacache`: npm rechazó la preparación TypeScript con
  `ENOTCACHED` al estar prohibidas las descargas. Un ensayo en serie con parada al primer fallo conservó el
  mismo error de preparación. Se copió únicamente la caché de contenido ya existente en este checkout a la
  copia de verificación y se repitió la suite, sin cambiar código ni candidato.
- Tras preparar la caché, `UV_CACHE_DIR=<caché-uv-existente> uv run --frozen --offline pytest -q`:
  **1761 pasadas, 2 opt-in omitidas, 29 subtests pasados**, en 167,29 s; diez avisos de deprecación
  Starlette/httpx. unittest: **8 pasadas**.
- Sustitución completada con [registro verificable](2026-10-26_CANDIDATO_SUSTITUCION.json): el original se
  renombró al destino de conservación y el árbol nuevo pasó a `my_harness_dist`. Antes y después se
  verificaron listas exactas de archivos/directorios, hashes y modos, sin extras, symlinks ni Git.
- Parsers documentales: 214 decisiones, 12 fases, sin tareas activas; enlaces relativos y presupuesto STATE
  correctos. Diff revisado y `git diff --check` correcto; D001–D213 y `docs/archive/` intactos.

## Paquete y límites

La única diferencia pertenece a `tests/`, fuera de las entradas del wheel y sdist que selecciona
`scripts/build_distribution.py` (`src/`, recursos UI y `PROJECT_FILES`). Los artefactos de T005 siguen como
referencia de producto, sin reconstruirlos ni atribuirles una nueva ejecución real. SHA256SUMS y los hashes
originales de wheel, sdist y pylock se han comprobado sin cambios. La sustitución afecta al árbol publicable
y su manifiesto.

No se repiten frontend, Alembic, navegador ni instalación/recorrido del wheel; sus entradas permanecen idénticas.
Sin servicios, smokes, proveedores ni ejecución del harness sobre este repositorio. Sin acciones remotas;
la CI de `my-harness-archive` comunicada por el usuario no acredita la CI del nuevo candidato público.
