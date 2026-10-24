# P012-T002 — Continuación con fixture limpio de T009

Fecha: 2026-10-24. Base documental: `2944231`; producto instalado: `6efbd82`.
**Estado: incorporación COMMITTED; tarea REVISION_LIMIT por Ruff; tramo detenido, T002 parcial.**
Antecedentes: [registro inicial](P012-T002_INCORPORACION_REAL.md),
[propuesta elegida](P012-T009_DIAGNOSTICO_ENTORNO_CODEX.md#5-consentimiento-posterior-propuesto-y-paradas)
y [D192](../DECISIONS.md#d192--p012-t009-entorno-del-escritor-y-continuidad-con-fixture-limpio).
Resultado de esta continuación: [D193](../DECISIONS.md#d193--p012-t002-fixture-limpio-incorporado-y-rechazo-por-ruff).

## 1. Autorización y preparación

HITL de esta sesión: **«Autorizar esta continuación de T002»**, sobre creación de B2 y su venv offline,
copia TOML, presets/composición propios, preflight, servicio 8024 e incorporación/tarea nuevas por UI en la
misma SQLite. Máximo adicional previsto **4 Claude y 1 Codex**, cero correcciones y parada al primer fallo;
sin T003/T004. No se repone el consumo anterior de 4 Claude y 1 Codex frente al techo acumulado 12/3.
El usuario pide además obtener e introducir la clave local; se lee directamente del archivo privado al
formulario, sin imprimirla ni conservarla aquí.

Área: `$HOME/Documents/harness-validation/p012-20261024`. Nuevos destinos:

- `projects/onboarding-b-t009`: clon local sin optimización/hardlinks ni checkout inicial del original;
  se retira origin y se hace checkout detached de `f6a2d9dc054725b2cd1f9e323bf387ce092925c2`.
  Árbol `fd1bd4754a5bf7109702f8570fc4853d0fbca467`, sin remotos, alternates ni enlaces.
- `.venv` propio Python 3.13.13, instalado offline con los mismos 17 wheels verificados por hash y el lock
  completo, sin dependencias nuevas ni builds. `.local/codex-tmp` ignorado, dentro del checkout y 0700.
- `config/harness-local-t009.toml`, 0600, SHA-256
  `b11cce3d02fa3138127243e5cb4f634a45b75c4d836ca7b324afebded47e3cc9`.
  Conserva literalmente el TOML original y añade solo `claude-t009`, `codex-t009` y `django-t009`.

Se verifican hashes de las CLI/intérprete, ambas distribuciones y 17 wheels; TOML original
`d882c42d…3843`. Sin reconstrucción o reinstalación del harness: wheel T008 SHA-256 `5df9e000…15e0b`.
Check puro sobre el paquete instalado, con creación de procesos bloqueada: versiones de la composición del
proyecto original iguales; solo PATH/TMPDIR distintos para el escritor nuevo. Python resuelve al venv nuevo;
el entorno del validador sigue separado. Defaults, guardias, modelos/esfuerzo y permisos sin cambios.

Una primera comprobación pura se adelantó a la creación del venv y rechazó su ejecutable aún inexistente.
Se completa la preparación offline ya autorizada antes de repetir esa comprobación. Es un error de orden del
guion de esta sesión, previo al preflight, sin invocar agentes ni modificar el producto para eludir un rechazo.

## 2. Preflight, checks y registro por UI

`check-config …/harness-local-t009.toml --preflight` del venv instalado: **exit 0**, Claude **2.1.310** y
Codex **0.164.0**, mismas identidades/política `1156d0c9…`, compatibilidad condicionada D174, sin valores
requeridos ausentes. No acredita inferencia por sí solo.

Las dos preparaciones y las seis validaciones de `python-django` terminan con exit 0 sobre B2 antes del alta:
Python/Django version, pytest (**2 passed**, JUnit), Ruff check/formato, mypy (**10 fuentes**), Django check y
makemigrations check (**sin cambios**). Comandos exactos del TOML; sin formateador ni pruebas del fixture fallido.
Logs privados `state/operator/t009-*`; se conservan originales y resultados completos fuera del repositorio.

Antes de arrancar: 4 jobs DONE, 0 locks y 5 procesos de agentes STOPPED en copia SQLite/WAL/SHM de consulta;
puerto libre. Servicio fuera del checkout en 8024, mismo entorno explícito T001 y misma SQLite.
Se vincula la pestaña existente sin navegación desde otro origen; login correcto y preferencias es/es conservadas.

Registro UI **`p012-b-t009`**, preview `9a6725e883a2…`, trabajo **es**, bootstrap false,
composición **django-t009 / python-django**, presets **claude-t009 / codex-t009**, sonnet/low,
catálogo único gpt-6-luna/low, plan agent y 0 correcciones. Confianza sintética y motivo confirmados desde UI.
Conversación B **`d6335fd1…`**, inventario **`370c964f…dc2e27e`**, mismo HEAD/árbol inicial.
Primer turno **`d67607ff…`** solicitado con criterios funcionales de D191 ya confirmados y sin ampliar alcance.

## 3. Incorporación documental COMMITTED

Un turno Claude **`31cc98f4…`** completo, con doce propuestas sin preguntas bloqueantes; decisiones D001–D005
inferidas expresamente del código. Los criterios de conversión de `limit` ya elegidos en D191 quedan en la
especificación, tarea y flujo. Se revisan y aplican las **12 propuestas APPLIED** desde UI, por hash y CAS,
sin editar manualmente sus bytes. AGENTS **37 líneas**, wrappers CLAUDE/GEMINI **3/3**.

Vista previa **`62174a7711600def8b34e61feb8d257c66541f11aa1d5b824168777065d58fce`**;
perfil **`8585911d18924c35ae2211a7725e1870fc3bce504409e7d749ed66908fd3e4e1`**.
Run documental **`54820357…` COMMITTED**, commit único
**`9808fd97d349c6eeacb766be8ff5e5603b6e974c`**, P001 ACTIVE, definición 1 y una tarea.
Los **15 archivos originales conservan bytes y permisos de disco**; README idéntico en su ruta original,
sin sustitución ni copia adicional en `onboarding-originals` (`preserved=[]` en la vista previa).
No se atribuye a este hijo el archivo de README del primer B. Checkout limpio tras incorporar, 28 archivos
versionados; manifiesto privado guardado antes de la tarea. No se repite el reenvío ya acreditado en D191.

La UI reinicia las casillas de revisión tras cada aplicación. Un intento de aplicar varias casillas previamente
marcadas encuentra el siguiente botón deshabilitado y no lo envía; se comprueba el estado y se confirma cada
propuesta individualmente, esperando su retirada de pendientes. Sin rechazo CAS, mutación duplicada o turno extra.

## 4. Tarea implementada pero rechazada por las validaciones

P001-T001 seleccionada desde NEXT_STEPS, fuente CAS **`a980e2402de2…`**, con notas acotadas a las mismas tres
rutas y pruebas funcionales de D191. Job **7**, run **`f98b16d9-7895-4edf-be50-d8cfe0405bf2`**, base `9808fd9`.

| Intento | Selección congelada | Resultado |
|---|---|---|
| `0da1b6d2…`, planificador | Claude sonnet/low | COMPLETE; contrato acotado |
| `72f152c9…`, ejecutor | Codex gpt-6-luna/low | COMPLETE, exit 0; vista, tests y flujo modificados |
| `185e1d46…`, revisor | Claude sonnet/low | COMPLETE, REVISE por Ruff |

Las tres llamadas Claude nuevas reportan **claude-sonnet-5-5**; no hay fallback de modelo o esfuerzo.
Versiones por intento Claude **2.1.310**, Codex **0.164.0**, **cli-14**, política **`1156d0c9…`**, perfil
declarado python-django, sin receta/formateador. El entorno congelado del escritor contiene ahora TMPDIR,
SHA-256 **`671fc7366cf0fbc50b017494de744dde8272f5041a8cc793f348e77178e06415`**.
El propio ejecutor ejecuta Python y resuelve el temporal dentro de B2; sus tres archivos mantienen contenido
(vista 751, tests 2039 y flujo 1144 bytes). Esto no demuestra la causa del truncamiento del intento anterior.

El diff implementa `int`, rango 1–20, defecto 5 y errores JSON 400; conserva los dos tests originales y añade
11 casos observados. El flujo documenta lo implementado y la procedencia histórica. El ejecutor intenta las seis
validaciones con `&&`: pytest pasa y Ruff detiene esa cadena. No corrige el formato antes de terminar.
El motor, por su parte, ejecuta y conserva **las seis validaciones**, también después del primer exit no cero:

| Validación del motor | Exit | Evidencia |
|---|---|---|
| pytest con JUnit | 0 | **13 passed**, dos originales incluidos; reporte completo |
| ruff check . | **1** | **E501** en test_views.py:23 y :44; 96/97 caracteres frente a 88 |
| ruff format --check . | **1** | El archivo de tests se reformatearía |
| mypy . | 0 | Sin errores |
| manage.py check | 0 | Sin errores |
| makemigrations --check --dry-run --noinput | 0 | Sin cambios |

JUnit del motor: **1770 bytes**, SHA-256
**`d517d6faa1e7c44b21eab1c29a9f771026e9597b4c16e11d9b469870dd4e383d`**.
Diff revisado: **5130 bytes**, SHA-256 **`b59ccb89a996144f1500992ef6f593151d03e8389d95fd7ebb850bf0f50a641d`**;
fingerprint **`edd71d81411486e8836b70062f3d1d219cbca53cda71f620b2cfa3b3976540e6`**.
El revisor detecta ambos fallos bloqueantes y una duplicación menor del mensaje de error; devuelve REVISE con
una propuesta de corrección. **No se aplica su next_prompt**. Cero correcciones deja **REVISION_LIMIT**,
sin aceptación, revalidación, reintento o commit de tarea. Los checks funcionales aprobados no equivalen a aceptación.

## 5. Parada y alcance acreditado

Servicio detenido mediante SIGINT al PID propio verificado, terminación normal exit 0, puerto 8024 cerrado y
clave efímera eliminada. **7 jobs DONE**, **9 procesos de agentes STOPPED**, **0 locks** y ningún job activo o en
cola. Tres runs nuevos (B conversacional, commit B y tarea); ninguna ejecución pendiente.

Consumo nuevo **3 Claude + 1 Codex**, acumulado **Claude 7/12, Codex 2/3**; saldo **5/1**, sin reiniciar
presupuesto ni usar el margen como permiso de reintento. Ambos proyectos conservan P001 ACTIVE; B2 HEAD `9808fd9`
y los tres cambios sin commit. No se arreglan a mano, formatean, restauran o revalidan resultados.

Comparación de copias SQLite/WAL/SHM inicial/final: integridad correcta y **8186 filas previas conservadas
íntegramente**, sin ninguna ausente o modificada (se excluye sqlite_sequence, contador mecánico).
Manifiesto original: B anterior, diff fallido, TOML original y ambas distribuciones intactos; B2 solo cambia
las tres rutas permitidas, sin archivos nuevos no ignorados. Historiales e intenciones previas sin reescribir.
La copia TOML nueva conserva su hash. Evidencia completa y captura permanecen en el área privada.

**Acreditado adicionalmente:** incorporación B nueva con presets/composición propios y código original intacto;
ejecución que escribe el cambio funcional, Python disponible y trece tests con JUnit; validación/revisión que
rechazan correctamente Ruff. **Pendiente:** tarea COMMITTED con las seis validaciones aprobadas y flujo básico
exitoso completo. T002 sigue parcial. No se acredita defecto del producto ni se abre una corrección de código
con esta evidencia; el fallo observado pertenece al resultado del ejecutor.

La siguiente acción de T002 es **concretar offline una propuesta de continuidad y someterla a HITL**.
El run agotado y el checkout sucio no autorizan reutilización bajo otra política, reparación manual o nueva
ejecución. La propuesta de T009 ya se ha ejecutado y su consentimiento queda agotado con esta parada; no autoriza
otro fixture ni otro intento. T003/T004, descargas, cierre de fase, cambios globales y publicación siguen fuera.

## 6. Verificación documental

Solo se actualizan documentos vivos de este repositorio y esta entrega saneada; sin cambios del producto,
esquema, flujos, configuración global o baseline pública. No se repiten suites completas del producto ni tests
de los fixtures detenidos.

- Parsers puros: **12 fases, 7 criterios P012, 9 tareas y 193 decisiones**.
- **580 enlaces/anclas relativos** válidos en los cinco Markdown modificados/nuevos.
- Presupuestos STATE/base/NEXT_STEPS: **12.335/24.576**, **8.700/12.288**, **21.403/49.152 bytes**.
- Base acumulada y cuerpos D001–D192 conservados; originales T001/T002/T009, archivos históricos, producto,
  flujos, esquema y baseline pública intactos. Hash/modo del TOML nuevo comprobados al finalizar.
- Diff de los cinco documentos revisado y `git diff --check` correcto. No se confunde esta comprobación
  documental con el fallo Ruff del hijo, que sigue conservado sin corregir.
