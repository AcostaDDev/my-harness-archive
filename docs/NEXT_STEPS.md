# Siguiente paso — preparar diagnóstico de la persistencia de confianza Codex

Estado al 2026-10-14:

- **D066 implementado y verificado offline:** controles explícitos de memoria
  automática en todos los roles como `cli-8`.
  [Entrega y límites](discovery/AGENT_PERSISTENCE.md),
  [inventario estático](discovery/AGENT_PERSISTENCE_INVENTORY.py) y
  [evidencia](discovery/AGENT_PERSISTENCE.json).
- Codex solicita memories desactivadas, sin generación/inyección ni historial;
  Claude autoMemoryEnabled=false, además de sesiones nuevas sin persistencia.
  Un override ambiental Claude conflictivo rechaza antes de efectos.
  HOME/USER/auth conservados. Jobs cli-7 bloqueados antes de preflight/efectos.
- 20 casos nuevos, 215 pytest pertinentes correctos y 941 recolectados. Las
  cuatro combinaciones pasan con CLI sintéticas que exigen esos controles.
  Sin CLI real, version/help, login, credenciales reales o inferencia.
- **Persistencia externa completa sin certificar.** Confianza Codex D061/D062,
  estado auxiliar, carga implícita de instrucciones y auth/refresh pendientes.
  No se borran memorias existentes ni cambian configuraciones personales.
- D065 conserva su dictamen: candidata de contención externa sin calificación
  para integrar. No hay nuevo backend OS ni local-config-3. El núcleo, esquemas,
  codec, permisos/modelos y congelados se conservan.
- El usuario exige contexto duradero en los Markdown de docs/, historial por
  fase y STATE/NEXT_STEPS frescos. La desactivación de auto memory no acredita
  todavía continuidad/archivado documental real; no se cambia SQLite como
  autoridad operativa del harness.
- Flujos reales: Codex→Claude D057 y Codex→Codex D061 llegaron a COMMITTED;
  este último causó parada por cambio global. Claude→Claude falló antes de
  D058; corrección tipada real pendiente. Claude→Codex nunca lanzada.

## Tarea concreta propuesta, no iniciada

**Preparar un diagnóstico de arranque Codex sin inferencia, con HOME/auth
ficticios y red denegada, para observar la persistencia de confianza.**

1. Fijar binario/hash, comandos/argv y parámetros de memoria de cli-8, raíces
   sacrificiales, entorno completo, aislamiento y artefactos. No reutilizar
   CODEX_HOME/HOME reales ni copiar/enlazar credenciales.
2. Definir controles que impidan lectura de auth/config/llavero reales y
   efectos remotos; no basta cambiar HOME o confiar en una ausencia de tokens.
   Mantener las limitaciones D065 y rechazar una vía no calificada.
3. Delimitar comparación sin override y, si hay base suficiente, confianza
   solo en memoria en el transporte. No precrear/restaurar confianza global.
   Si el fake auth impide alcanzar thread/start, registrar ese límite: no
   serviría como prueba de que la ruta observada en D061 no persiste.
4. Concretar número de procesos, timeouts, salida filtrada/capturas, originales
   protegidos y sacrificiales, comprobación de parada, errores sin fallback y
   criterios que distingan sintaxis, arranque y efectos observados.
5. Entregar propuesta reviewable y ensayar su controlador únicamente con
   procesos sintéticos. No ejecutar la CLI real durante la preparación ni
   certificar autenticación o refresh por ese ensayo.

Criterios: propuesta acotada con objetivo útil y límites explícitos, o dictamen
preciso si el diagnóstico no puede alcanzar esa ruta con seguridad. Ningún
proveedor/modelo, cambio global, secretos reales, modificación del sandbox
interno, ampliación de raíces, redirección/copia de auth ni fallback. Actualizar
STATE/NEXT_STEPS/DECISIONS antes de darla por terminada.

La ejecución real, incluso sin inferencia, necesita una autorización nueva
para la propuesta concreta y controles suficientes. No la autoriza D066 ni
se reutilizan D050/D055/D057/D060, agotados. No preparar o ejecutar otra matriz,
recuperar jobs/liberar locks, publicar/push o iniciar H6.2. La fase de
comprobaciones sigue abierta. Archivado/continuidad documental y los flujos
Claude pendientes son tareas separadas posteriores; ninguna iniciada aquí.
