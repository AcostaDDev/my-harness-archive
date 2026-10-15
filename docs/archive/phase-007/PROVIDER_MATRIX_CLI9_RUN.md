# Cuatro combinaciones reales comprobadas (D071, cli-9)

2026-10-14, sobre `1d2de43` con cambios locales acotados de esta entrega.
El usuario pidió cerrar el flujo; tras la parada por timeouts D070 autorizó
expresamente **«Autorizar una nueva matriz»**. Propuesta y límites (archivo `docs/discovery/PROVIDER_MATRIX_CLI9_FINAL_PROPOSAL.md` retirado en P008-T001; recuperable con `git show 8622a43:docs/discovery/PROVIDER_MATRIX_CLI9_FINAL_PROPOSAL.md`),
[manifiesto de resultados y hashes](PROVIDER_MATRIX_CLI9_RESULT.json).

**Comprobación funcional de las cuatro combinaciones completada.** Los cuatro
pares recorrieron planificación → edición real → validación → revisión ACCEPT
→ commit del contenido exacto. No se avanza a otra tarea de producto.

| Revisor/planificador → ejecutor | Run | Resultado/commit |
|---|---|---|
| Codex → Codex | `712b2679-cd22-4c41-a2e0-5bc07740bd8b` | COMMITTED `75bef356` |
| Claude → Claude | `39d71112-79b6-46ed-a9f2-69d1b96cc2a4` | COMMITTED `293643f2` |
| Claude → Codex | `43714cce-8754-444c-ae09-c6597a38f2b9` | COMMITTED `347f4a7d` |
| Codex → Claude | `e4ae0d0b-c9ae-4022-abad-15d430914961` | COMMITTED `584ed7e0` |

## Qué se comprobó

Área nueva `/private/tmp/harness-provider-matrix-6`, checkouts sintéticos
TypeScript web y estado separado. Wheel corregido de D070 y 18 pins instalados
offline en venv propio; código del producto contrastado byte a byte contra el
wheel. El harness se ejecuta desde ese paquete, fuera del checkout de desarrollo.
Cada preflight coincide con Codex 0.162.1 / Claude 2.1.296, sin flags ausentes.

Doce invocaciones de modelo completas, seis por proveedor, tres por par:
gpt-6-luna / claude-sonnet-4-6, planner/reviewer medium y executor low.
Sesiones nuevas y prompts/contexto/permisos/esquemas congelados y hashes
contrastados. Claude reporta modelo sonnet; Codex no reporta modelo/esfuerzo
efectivos. Selecciones solicitadas y telemetría observada se conservan separadas.
Costes nominales reportados por Claude no se presentan como factura de suscripción.

- Los cuatro planners devuelven listas y executor_selection como objeto.
  forbidden_paths=[]; no hay contrato contradictorio. Los dos planners Claude
  acreditan el esquema tipado D058 con salida real, sin convertir texto JSON.
- Codex escribe en ambas combinaciones: file_change en Codex→Codex y comando
  Python registrado con exit 0 y diff exacto en Claude→Codex. El primer
  verificador esperaba solo file_change; se amplió después de inspeccionar el
  original para aceptar esa otra edición acreditada, sin repetir el recorrido.
- Claude escribe con herramientas Edit/Write, sin Bash. Única ruta cambiada:
  src/estimate.ts, tasks*45 → tasks*30, conservando validaciones y RangeError.
  Documentos del fixture intactos, ninguna edición atribuida a lectores.
- Veinticuatro comandos nativos completos: Node/npm, npm ci offline y
  check/test/build por par. Exit 0, capturas completas por hashes y grupos
  ausentes. Cuatro originales JUnit completos, tres casos aprobados cada uno.
- Review ACCEPT y aceptación eligible; base/fingerprint/árbol coinciden con
  validación y la intención de commit. HEAD es exactamente expected_commit,
  padre igual a la regresión preparada y único commit nuevo. Autor
  Harness Provider Matrix; solo src/estimate.ts y Git limpio. **El ejecutor no
  hace commit: acepta el revisor y lo realiza mecánicamente el harness.**
- Ocho jobs DONE/owners cerrados, doce procesos CLI STOPPED y grupos ausentes,
  cero locks. Servicios terminan normalmente con TERM/143, claves retiradas,
  puerto :8013 sin listener después. Sin recuperación o liberación manual.

## Confianza, memoria y límites

El escritor Codex recibe la tabla projects untrusted de [D068](CODEX_TRUST_SUPPRESSION.md),
además de workspace-write/raíces explícitas. Conserva escritura real sin el
cambio de confianza global que detuvo D061. Codex recibe memorias/generación/
inyección desactivadas e historial none/ephemeral; Claude autoMemoryEnabled=false
y no-session-persistence. HOME/USER/auth y versiones instaladas conservados.

Las muestras de config Codex, settings Claude y gitconfig mantienen hashes/modos
en las cuatro comprobaciones y al terminar. No aparecen archivos de memoria
nuevos ni cambian los existentes en las raíces habituales muestreadas; cero
archivos en Codex/memories y siete previos en Claude permanecen iguales. No se
observan entradas bajo Claude/projects cuyo nombre contenga el identificador
de esta área. Solo hashes, nunca contenidos privados/auth, quedan en evidencia.

**Esto cierra el flujo funcional; no certifica aislamiento físico completo.**
Logs/cachés/SQLite auxiliares de las CLI, refresh interno, IPC, cuota/factura y
retries internos siguen sin auditoría exhaustiva. Las sesiones nuevas y apagar
auto memory no prueban que todo contexto provenga exclusivamente de docs/.
Archivado por fase y continuidad documental real quedan pendientes: los docs
del fixture se preservaron y no se evaluó ese recorrido. No se integra un
sandbox D063/D067 ni se elimina estado auxiliar para simular un resultado.

Los [ensayos detenidos D069/D070](PROVIDER_MATRIX_CLI9_STOPS.md) se conservan:
contrato contradictorio corregido y timeouts observados, cuatro invocaciones
previas en total. D071 añade doce autorizadas, sin retry/fallback del harness.
Consumo de esta autorización satisfecho y agotado; no se autoriza otro run,
matriz, login, fase/tag, publicación o push.

## Verificación de entrega

948 pytest y 121 subtests aprobados (319,43 s), 12 checks estándar, 217 tests
de transporte y 155 de contratos/motor/permisos/prompts. Siete casos nuevos.
Build frontend, wheel/sdist y comprobación instalada offline correctos. Warning
existente de deprecación TestClient/httpx; sin modificar dependencias para ocultarlo.
Primer pase completo falló solo en una aserción que no admitía la descripción
nueva del esquema; corregida y suite completa repetida con éxito.

Se verifican hashes del paquete/TOML/binarios/prompts/streams/JUnit, integridad
SQLite/FK, commit exacto y ausencia de procesos/grupos/locks. Scripts de
control/verificación en el manifiesto, originales retenidos bajo el área y
resumen durable en este repositorio. Sin QA visual nueva: no cambia UI ni API.
STATE/NEXT_STEPS/DECISIONS actualizados; siguiente alcance separado y no iniciado.
