# P009-T019 — El ejecutor sin shell puede cumplir el formato del perfil

Fecha: 2026-10-21. Decisión [D133](../DECISIONS.md#d133--p009-t019-el-harness-formatea-con-la-herramienta-del-perfil-tras-cada-turno-del-ejecutor).
Origen: parada de T009 ([evidencia](P009-T009_PILOTO_CODEX_CLAUDE.md), D132). Sin proveedores ni piloto.

## 1. Defecto

El ejecutor Claude trabaja con `Read`, `Edit`, `Write`, `Glob` y `Grep`, sin shell (D121). No puede ejecutar Ruff, así
que formatea a mano, y en T009 lo hizo con 88 columnas cuando el hijo fija 100. `ruff format --check .` solo nombra el
archivo. El revisor recibe esa salida, pero el ejecutor solo recibe la revisión, sin la línea ni el cambio. Dos
ciclos de corrección no podían cambiar el resultado, y el run `bb29b133` acabó en `revision_limit`.

## 2. Decisión del usuario

El usuario eligió entre tres opciones (bucle HITL de esta tarea):

- **Elegida: el harness formatea.** Tras cada turno del ejecutor, y antes de capturar la evidencia, el motor ejecuta
  el formateador del perfil sobre los archivos del contrato. El revisor ve y se acepta el contenido ya formateado.
  Implementa el `formatter_argv`/`formatter_paths` que el perfil declaraba desde H2.1 (D015) sin ejecutarlo nunca.
- Descartada: dar al ejecutor el diff de `ruff format --diff`. Cada error de formato seguiría costando al menos un
  ciclo REVISE, y el resultado dependería de que el modelo aplicara bien el diff.
- Descartada: conceder `Bash(ruff format …)` al ejecutor Claude. Le daría un shell parcial, chocaría con D121 y
  obligaría a versionar el adaptador (`cli-14`).

Sobre `bb29b133`, el usuario decidió dejarlo como evidencia, igual que `fc340afb` (D129). Ver §5.

## 3. Diseño

- **Dónde se declara.** El perfil `python-django-recipe` recibe `formatter_argv = ("ruff", "format", "--")` y
  `formatter_paths = ("*.py",)` en `services/local_config.py`, donde se registra, y no en `recipes/django.py`. El texto
  de ese archivo es la huella de la receta (`implementation_sha256`), y el recibo de preparación solo se vincula si
  coincide (`project_preparation.bind`). La huella sigue en `f511c00a…0e191`, así que el hijo del piloto sigue
  preparado. Un test fija ese valor.
- **Perfil.** Un formateador declarado necesita un argv que termine en `--` y al menos un patrón. Las rutas nunca se
  leen como opciones. El TOML no admite `formatter_*`, igual que antes (D095). Hoy solo lo declaran el perfil de la
  receta y `reference_project`, que es solo de biblioteca.
- **Autorización nativa.** `CommandConfig.formatter_argv` (de `authorize_profile_commands = true`; sin ella, la
  configuración se rechaza) autoriza el argv del formateador seguido solo de archivos regulares que existen en el
  checkout. `context.path` rechaza enlaces y escapes. No admite rutas que empiezan por `-`, otro `cwd` ni entorno
  extra. El spec del proceso registra `authorization: "formatter-paths"`; los demás comandos siguen siendo
  `exact-command`. Sin formateador, `config_payload` omite el campo y `command_config_sha256` no cambia. El adaptador
  sigue en `commands-1`, porque fuera del formateador se comporta igual.
- **Motor** (`_review_loop`). Solo después de un turno del ejecutor (`execute-task`, `revise-task` o un reintento
  explícito), nunca al revalidar, porque una persona puede haber editado el checkout. Formatea
  `changed_paths` que casan con `formatter_paths`, existen como archivo y pasan la política de rutas del contrato
  (allowlist, prohibidas, protegidas y sensibles). Si no hay ninguno, no se lanza nada y el ciclo conserva su forma
  anterior. Un único comando con límite de 120 s, con intención y proceso en el journal como cualquier validación.
- **Fallos.** Si el formateador no llega a ejecutarse bien (error de lanzamiento, timeout o sin código de salida),
  el run se para en la etapa `formatter` antes de validar y revisar, sin gastar la revisión. Un código distinto de
  cero, como un error de sintaxis, sí llega a la validación y al revisor: el ejecutor puede corregirlo.
- **Trazabilidad.** El ciclo guarda `formatting_json` (comando, `command_id`, rutas, resultado y una nota). El revisor
  lo recibe como clave `formatting`, solo cuando hubo formateo. El historial pasa a formato 8 solo si algún ciclo lo
  tiene, y lee 1–8. La API añade `formatting` (opcional) a cada ciclo, y la página del run lo muestra.
- **Instrucciones del ejecutor.** Con formateador, `PROFILE_INSTRUCTIONS` añade que el harness ejecuta
  `ruff format --` sobre los archivos cambiados después de cada turno, y que no hay que reformatear a mano con otro
  estilo. Las plantillas no cambian.

## 4. Compatibilidad

| Elemento | Efecto |
|---|---|
| Huella de la receta y recibos de preparación | sin cambios; el hijo del piloto sigue «Django preparado» |
| Proyectos con la receta | cambian `local_config_sha256` (perfil) y `command_config_sha256`; un job pendiente quedaría en cuarentena (hoy no hay ninguno) |
| `typescript-web`, perfiles declarados y TOML v1–v5 | sin formateador: mismos hashes y mismo flujo |
| Runs y contextos congelados | conservan su perfil, sin formateador; el códec lee los formatos 1–7 igual |
| Ejecutor Codex con el perfil Django | el formateador corre igual y, si Codex ya formateó, no cambia nada |
| `reference_project` (solo biblioteca) | su formateador declarado solo se activa si el ejecutor cambia `src/**/*.py` |
| Contrato del ejecutor | no gana shell, red ni rutas: el harness formatea solo archivos que el contrato ya le permite |

## 5. Run `bb29b133` y reanudación de T009

Por decisión del usuario, `bb29b133` queda en `revision_limit` como evidencia. Tampoco podría avanzar: agotó las
correcciones, y su contexto congelado no tiene formateador. Para reanudar T009 hacen falta:

1. Wheel reconstruido desde esta tarea, verificado con `check_distribution.py` e instalado en el área.
2. Hijo limpio en `98f4611`. Hay que retirar las 7 rutas del diff de `bb29b133` (§2 de la evidencia de T009), con
   copia privada en el área y sin tocar `.venv`, TOML ni SQLite. Después, comprobar «Django preparado» en la UI.
3. **Autorización nueva del usuario** con techo. Queda 1 de 7 invocaciones de T009, y un run nuevo de P001-T002
   necesita al menos 3 (planificador, ejecutor y revisor).

## 6. Verificación

- `tests/product/test_profile_formatter.py` (9 tests). La caracterización de T009 sin formateador llega a
  `revision_limit` con el mismo check fallido. Con formateador, ACCEPT en la primera revisión, con el contenido
  formateado acreditado, la clave `formatting` del revisor, las instrucciones del ejecutor y el formato 8 de ida y
  vuelta. Solo se formatean archivos del contrato que casan: no se formatean los borrados, los protegidos ni los que
  no casan, y cada turno vuelve a formatear. La revalidación no formatea, y sin archivos la forma del ciclo no
  cambia. Un formateador que no se ejecuta para en `formatter`; un código de salida llega al revisor. Runner nativo:
  autoriza archivos existentes y rechaza ausentes, enlaces, `..`, opciones, directorios, `cwd`, entorno y otro argv;
  el hash sin formateador no cambia. Configuración: el perfil de la receta declara el formateador, la huella de la
  receta queda fijada y un formateador sin `authorize_profile_commands` se rechaza.
- Ensayo Django (`test_django_journey.py`, variante sintética): en la tarea Codex→Claude, el ejecutor falso escribe
  `core/synthetic_format.py` con comillas simples. La herramienta sintética, que emula esa regla de `ruff format`, lo
  rechaza en `--check`. El formateador lo corrige antes de validar y la primera revisión acepta. El proceso queda con
  `formatter-paths`. En las otras tres parejas solo cambia HTML: no hay formateo y el ciclo conserva su forma.
- Suite pytest completa: 1585 pasan y 1 se omite (Django real), en 4 min 4 s. unittest: 12 OK. `node --test`: 79 OK.
  `npm run check` y `npm run build` correctos. OpenAPI y tipos regenerados. `alembic check` sin operaciones nuevas:
  no hay modelos ni migraciones.
- **No probado:** Ruff real sobre el hijo (la variante real del ensayo se omite sin wheels preparados), el ejecutor
  Claude real y un wheel reconstruido. Las tres cosas quedan para la reanudación de T009.
