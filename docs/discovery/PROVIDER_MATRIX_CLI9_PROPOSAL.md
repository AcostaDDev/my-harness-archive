# Comprobación de los cuatro flujos con cli-9 (D069)

2026-10-14. Petición nueva del usuario: «Comprueba el flujo para dejarlo cerrado
y luego seguimos con el resto de pasos». Alcance: una matriz funcional real,
sin reutilizar los consentimientos anteriores y sin avanzar a H6.2 ni archivado.

Antes de consumir se ha verificado la supresión específica de confianza en
fuente del pin (D068), implementado cli-9 y preparado el wheel instalado fuera
de este checkout. No se integra el sandbox experimental D063/D067, no se cambia
HOME/USER/auth ni se copian credenciales. No login ni actualización de CLI.

## Ejecución acotada

- Área nueva `/private/tmp/harness-provider-matrix-4`, cuatro checkouts
  desechables, configuración local-config-2 y estado separado por par.
- Wheel/sdist/pins offline en `/private/tmp/harness-provider-matrix-4-package`;
  venv propio, comprobación de distribución y check-config sin proveedores.
- Codex 0.162.1 `gpt-6-luna`, Claude 2.1.296 `claude-sonnet-4-6`.
  Planificador/revisor medium, ejecutor low; catálogo, cero ciclos de corrección.
  Se conservan tools, permisos, comandos, entornos y límites de D060.
- Orden: Codex→Codex, Claude→Claude, Claude→Codex, Codex→Claude. La primera
  comprueba la corrección del escritor antes de continuar. Se repiten los dos
  éxitos históricos para verificar los controles actuales de memoria.
- Máximo doce invocaciones de modelo, tres por combinación. Preflight
  version/help, no auth status. Timeouts: lector 600 s, escritor 900 s;
  controlador 1800 s por combinación, máximo total de dos horas. Sin retry,
  fallback, modelos alternativos, grants, revalidate, cierre/tag o recuperación.
- El ejecutor escribe solo `src/estimate.ts`, devolviendo `tasks * 45` a
  `tasks * 30`. El revisor debe emitir ACCEPT; el harness hace el commit exacto.
  npm offline/check/test/build y tres casos JUnit deben pasar. Docs del fixture
  permanecen intactos: este ensayo verifica código, no continuidad documental.

## Guardias y evidencia

`/private/tmp/h69_flow_check.py prepare` congela hashes del paquete, transporte,
binarios, scripts y TOML, HEAD/árbol/documentos y muestras globales. No lanza
proveedores. `run PAR` comprueba esos hashes y estado vacío antes de lanzar una
combinación con `run_pairing.sh` desde el paquete instalado.

El controlador compara cada segundo hashes de config Codex, settings Claude,
gitconfig y archivos de memoria automática bajo las raíces habituales. Solo
registra hashes/metadatos, nunca contenidos privados ni auth. Cambio observado
detiene el servicio y toda la matriz; los siguientes pares exigen éxito y
originales conservados. Cualquier fallo del par también detiene esta comprobación
sin reintentar. Puerto ocupado aborta sin detener otro servicio.

Éxito requiere tres COMPLETE/exit 0 con roles/proveedores solicitados, listas y
objetos tipados en el original del planner, edición real y solo de la ruta
permitida, validaciones/JUnit aprobados, ACCEPT vinculado a la misma huella y
un único commit nuevo con ese árbol. Al cerrar: jobs DONE, owners cerrados,
procesos/grupos ausentes, cero locks, servicio detenido y clave retirada.

No se presenta el muestreo como aislamiento físico ni auditoría exhaustiva:
logs/cachés/SQLite auxiliares de las CLI y refresh interno no están certificados
como ausentes. Memorias generadas/inyectadas están desactivadas; sesiones son
nuevas. No se prohíbe ni altera la autenticación instalada. Una prueba funcional
correcta no acredita todo contexto exclusivamente documental ni archivado
automático de fases. Estos límites se conservan al informar el cierre del flujo.

## Órdenes

Una vez preparado el manifiesto, cada orden ejecuta su combinación una vez;
revisar evidencia antes de la siguiente. La autorización del usuario para
comprobar el flujo no permite cambiar selecciones/permisos ni ignorar una parada.
El mecanismo de permisos de herramientas debe permitir los procesos reales,
red de proveedores y el servicio loopback fuera del sandbox de desarrollo.

```sh
python3 /private/tmp/h69_flow_check.py run codex-codex
python3 /private/tmp/h69_flow_check.py run claude-claude
python3 /private/tmp/h69_flow_check.py run claude-codex
python3 /private/tmp/h69_flow_check.py run codex-claude
```
