# Ejecutor de validaciones de producto — alcance previo

Elegido explícitamente por el usuario el 2026-10-13, sobre `3bb9541`, Git limpio.
Sustituye la elección pendiente de NEXT_STEPS; no inicia un piloto.

## Diseño acotado

- Adaptador POSIX opt-in de `CommandRunner`, conectado por `ports_factory` del
  servidor y ligado al journal del job. Reutiliza cola, propietario, lease,
  compuerta de lanzamiento, grupos POSIX y recuperación H2.2/H2.3.
- Configuración inmutable: checkout confiable explícito, autorización de comandos
  exactos (argv/cwd/entorno/timeout), mapa de ejecutables absolutos, entorno base
  completo y límites de tiempo/captura. Hash/versiones congelados al admitir el
  run; discrepancia o configuración antigua sin esa identidad impide ejecutar.
  No se cambian snapshots anteriores. No se hereda el entorno del servicio.
- Confianza en código/scripts/configuración externa, autorización del comando y
  política de prefijos del perfil son decisiones separadas. No se conceden
  permisos H3.2 a agentes ni red por permitir un comando. Ejecución nativa con UID
  del servicio: sin sandbox físico; solo repositorios y programas confiables que
  no daemonizan ni escapan del grupo. npm puede ejecutar shell dentro de scripts
  autorizados; el adaptador no introduce shell.
- Registro propio por command_id mediante eventos `command_process_*` bajo el
  mismo job: intención, identidad antes de GO, fragmentos de bytes acotados y
  resultado observado. Es una proyección del journal existente, sin otra cola,
  tabla o migración. SQLite conserva los prefijos exactos en base64; no se añade
  otro almacén ni retención de comandos. Preparación y validación lo comparten.
- stdout/stderr acotados por stream, truncamiento e incompletitud explícitos,
  exit observado nullable, duración monotónica, timeout/errores y estado del
  grupo. Captura incompleta/truncada no acredita éxito. Fallo de journal o grupo
  incierto aborta el motor y conserva el lock. No relanzamientos automáticos.
- Recuperar exige la confirmación existente con job/token/versión, propietario
  cerrado o ausente y todos los grupos ausentes. Ni caída, ni lease, ni exit del
  líder prueban muerte de hijos. No se señalizan PIDs recuperados. La recuperación
  no adopta validaciones parciales ni las repite; revalidar es una acción nueva.
- Resultado aditivo con metadatos de captura y codec nuevo solo donde se usen;
  formatos anteriores mantienen su serialización. JUnit, review, evidencia Git
  exacta y commit siguen siendo puertas independientes. Backup/retención deben
  reconocer grupos de validación para comprobar parada.

## Criterios de aceptación

1. Probar argv literal, cwd/entorno/autorización/configuración congelada; rechazar
   ejecución no compuesta, discrepancias, symlinks/escape y comandos no autorizados.
2. Procesos sintéticos: éxito, exit no cero, ejecutable ausente, timeout, stdout y
   stderr excesivos, bytes no UTF-8 y descendientes vivos tras salir el líder.
3. Intención e identidad preceden efectos; fallo antes/después de GO, caída real
   del supervisor, lease vencido y reinicio con grupo vivo mantienen exclusión.
   Confirmación explícita solo tras ausencia comprobada, sin duplicar ejecución.
4. Recorrido TypeScript real offline en Git/SQLite temporales con agentes falsos:
   preparación, tipos, tests, JUnit, build, aceptación y commit exacto. Fallos y
   cambios posteriores no permiten commit; historial y evidencia sobreviven reinicio.
5. Regresión offline pertinente, diff revisado, STATE/NEXT_STEPS/DECISIONS y
   README/AGENTS sincronizados, commit solicitado y Git final comprobado.

Fuera: proveedores, login/smokes, red/instalación online, UI nueva, configuración
completa de uso real, sandbox de código hostil, procesos escapados, GC/rotación,
publicación/push y cambios globales. No se ejecuta ReferenceProject ni el harness para
el desarrollo. No hay contradicción material con D016/D017/D031/D038/D039;
se implementa ahora la brecha expresamente aplazada por D038/D046.
