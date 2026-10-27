# P013-T013 — Candidato público y paquete verificados

Fecha: 2026-10-27. **Completada**, con evidencia sintética offline sobre el árbol exacto.
Decisión: [D230](../DECISIONS.md#d230--p013-t013-candidato-público-y-paquete-aislado-verificados).
Siguiente: T014, revisión de salida y expediente; P013 continúa abierta y la publicación aplazada.

## Alcance y autorización

El encargo de siguiente tarea, commit en inglés y autorización general del usuario se acota aquí a exportación,
construcción/instalación offline, suites y servicios con agentes falsos en un área nueva fuera del checkout.
No se ejecuta el harness sobre este repositorio, proveedores reales, login, configuración global del equipo,
bases operativas, red, CI remota, tag, push ni publicación. No cambia código de producto, modelos, API,
dependencias ni flujos. La versión sigue siendo `0.1.0` según D178/D215; `0.2.0` sigue reservada.

La entrega permite revisar y publicar posteriormente un árbol que incluye P013, con identidad y comprobaciones
propias. No atribuye los hashes ni las pruebas instaladas de P012/T012 a los bytes nuevos.

## Árbol y procedencia

- Fuente exacta: `984c287ab9f21ba7976fc7cdb5df86b4f235b118`, último commit de T012, checkout inicialmente limpio.
- Candidato nuevo: `$HOME/Documents/projects/my_harness_dist_p013`.
  **445 archivos / 6.389.580 bytes**, 26 archivos de baseline pública, sin Git, enlaces simbólicos, cachés,
  entornos ni datos operativos. Scripts `install`/`start` conservan modo 0755.
- [Manifiesto público](P013-T013_MANIFIESTO_PUBLICO.sha256): SHA-256
  **`ea0f74e9099f1383128ba5e6e2e92ac298447cab54bd7336909d66f0f800c428`**.
  [Correspondencia privada](P013-T013_MANIFIESTO_PRIVADO.tsv): 853 fuentes clasificadas, 408 exclusiones razonadas;
  el manifiesto privado no se publica.
- [Diff frente a D214](P013-T013_DIFF_PUBLICO.json): **325 idénticos, 44 añadidos, 76 modificados, cero eliminados
  y cero cambios de modos** entre archivos compartidos. Altas de configuración, preparación, instalación,
  migraciones 0026/0027, UI/pruebas y documentación corresponden a las entregas T002–T012.
- Los archivos públicos provienen de las mismas rutas/lista positiva congeladas de P012; `docs/public/` se
  mapea a raíz y el resto de documentación privada queda excluido. Este commit solo añade evidencia/herramientas
  privadas y actualiza documentos vigentes: no cambia ningún byte exportado desde la revisión fuente.

No se sustituye `my_harness_dist`: D214, P011 y P012 quedan en sus destinos originales. Los tres se verificaron
contra sus manifiestos canónicos (401/387/401 archivos), antes de cualificar el nuevo candidato.
[Conservación](P013-T013_CONSERVACION.json) acredita nombres, bytes y modos antes/después de los tres árboles,
todo `docs/archive/`, los dos paquetes P011, el paquete P012 y `dist/` local. No se reescribe ningún snapshot,
expediente, paquete o historial anterior. El inventario completo original queda en el área de verificación.

## Paquete nuevo

Área propia: `$HOME/Documents/projects/my_harness_p013_t013_verification`.
El subdirectorio `verification-copy/` parte de una copia exacta, comparada por archivos/directorios, modos y
hashes; solo allí se instalan dependencias y se generan resultados. El árbol candidato permanece limpio e idéntico.
`package/` contiene wheel, sdist, lock, scripts/fixture autocontenidos y manifiesto `distribution-1`.

| Artefacto | SHA-256 |
|---|---|
| wheel `harness_local-0.1.0-py3-none-any.whl` | `2416672d69b54524544d8560b41a54f49cb9747164faa1c82ac777672ad47076` |
| sdist `harness_local-0.1.0.tar.gz` | `31c9ab33a50a196ff7c2b0852d90bdf98eeabfb3f5ead427713c4b5049b5b22c` |
| `pylock.toml` | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |
| `distribution-1.json` | `35931df4ac58bb51104edd4ed0c1b30e1730d5055d964310a0c51a02aadc6827` |
| `SHA256SUMS` | `0d7cab5e3901985962c39b95cb621d8e2024141f6b3b7d9f6e312be14bae2edb` |

[Checksums completos](P013-T013_PAQUETE.sha256), incluidos scripts/fixture. Lock regenerado desde `uv.lock`;
su contenido sigue siendo idéntico porque no cambian dependencias. El verificador contrasta miembros exactos,
fuentes/recursos UI, migraciones, metadatos/licencias, versiones de paquete/API/UI y hashes.

## Validación del candidato exacto

macOS ARM64, Python 3.14.4, uv 0.12.19, Node 24.15.0 y npm 11.12.1; cachés existentes, sin descargas.
[Resultados](P013-T013_RESULTS.json) y [logs saneados](P013-T013_LOGS/pytest.log), con tiempos y salidas sin rutas
personales ni espacios finales; originales íntegros retenidos en el área de verificación.

| Comprobación | Resultado y alcance |
|---|---|
| pytest sobre copia exacta | **2048 pasadas, 29 subtests pasados, 2 opt-in omitidas**, 218,63 s. Once avisos: diez de Starlette/httpx y uno del ZIP duplicado sintético que prueba rechazo. |
| unittest | **8 correctas**. |
| Node | **155/155**, sin omisiones. |
| Frontend | Dependencias del lock offline, tipos y build Vite correctos; aviso habitual de tamaño de bundle. |
| Alembic temporal | `upgrade head` hasta `0027_profile_proposals`, `check` sin operaciones nuevas. Ninguna base del operador. |
| Documentación exportada | **50 Markdown / 403 enlaces** incluyendo plantillas/fixtures, parsers y presupuestos correctos; 93 decisiones públicas, 67 referencias DNNN de código acreditadas. P001 pública sin tareas. Escáner privado sin hallazgos. |
| Distribución instalada | UI/assets/API, sesión, migración/backup previo, definición D088/tarea/commit/reinicio con agentes falsos y consulta restaurada correctos; sin acceso a fuentes de desarrollo ni Node en runtime. |
| Instalador desde árbol exportado | `scripts/install --dist` offline en rutas con espacios, sin Node/proveedores en PATH. READY tras verificar el paquete; repetición sin cambiar `current.json`. También se verifica el checker autocontenido del paquete. |
| Arranque del paquete | Dos arranques con wrapper `scripts/start` del paquete, UI 200, API protegida sin TOML, `UNCONFIGURED` y supervisor deshabilitado. Reinicio conserva DB; no crea configuración. SIGTERM reenviada, hijos esperados y salida 143 del wrapper según contrato. |
| Conservación | Candidato final idéntico antes/después; ocho entradas protegidas sin cambios de bytes, rutas o modos. Servicios propios detenidos al terminar. |

La instalación desde clon completa y las altas guiadas Go/formulario/QA Chrome conservan su evidencia T012.
T013 construye desde el árbol exportado y verifica instalador desde paquete, sin repetir esa matriz visual ni
las altas v9 completas. El recorrido del verificador usa fixtures propios. No acredita proveedores reales,
otras plataformas/navegadores, accesibilidad completa, creación Django v2 real ni una Release/CI remota.

## Incidencias de la verificación conservadas

1. La primera exportación se rechazó por `logs/reports/home/temp` en dos plantillas: el scanner congelado
   confundía `/home/t` dentro de prosa con una ruta personal. [Adaptador P013](P013-T013_EXPORT.py) conserva
   clasificación y controles, exige límite de ruta antes de `/home/` y comprueba que rutas personales absolutas
   siguen rechazadas. No cambia las plantillas ni el exportador archivado. Árbol y ensayo rechazados conservados
   en los destinos hermanos `my_harness_dist_p013_rejected_scan` y `my_harness_p013_t013_rejected_scan`;
   [log original saneado](P013-T013_LOGS/export-initial-rejected.log).
2. El primer comando Node precedía a la instalación npm: seis archivos de pruebas no podían importar
   TypeScript/markdown-it. [Fallo original](P013-T013_LOGS/node-initial-missing-dependencies.log) conservado.
   Se corrigió el orden del guion: build con `npm ci` offline antes de Node. Se retomó desde ese punto, conservando
   pytest/unittest válidos y verificando otra vez los bytes de candidato/copia contra la revisión exacta.
   No se repitió backend ni se cambió código de producto para obtener el resultado correcto.

## Reproducción y límites de cierre

[Guion](P013-T013_CANDIDATE.py): exige destinos nuevos, registra checkpoints y preserva logs fallidos al retomar
con `--resume`; tras una interrupción operativa se debe comprobar primero que los escritores anteriores están
detenidos. No infiere su muerte ni recupera instalaciones parciales automáticamente.

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P013-T013_CANDIDATE.py \
  --revision 984c287ab9f21ba7976fc7cdb5df86b4f235b118 \
  --out <candidato-nuevo> --area <área-nueva-fuera-del-checkout> \
  --preserve ../my_harness_dist \
  --preserve ../my_harness_dist_p011_74cc9141 \
  --preserve ../my_harness_dist_p012_cf191a40 \
  --preserve docs/archive --preserve .local/p011-t015/package \
  --preserve .local/p011-t015/package-repeat --preserve .local/p012-t005/package --preserve dist
```

Los placeholders representan rutas elegidas por el operador. La reproducción operativa requiere su autorización
propia; no reutilizar el área ya cualificada. El exportador admite exportación sola con `--revision`, `--out`,
`--private-manifest` y `--public-manifest`, como su predecesor. [Checker vigente](P013-T013_CHECK_DOCS.py) comprueba
parsers, enlaces/presupuestos y conservación de los cuerpos D001–D229. Diff revisado y `git diff --check` correcto.
Una exportación del checkout final reproduce exactamente el manifiesto público cualificado: los cambios de
esta tarea quedan fuera del árbol público. Se conservan también directorios, modos y hashes del candidato.
T014 debe dictaminar la evidencia y actualizar el expediente antes de T015; esta entrega no cierra P013 ni publica.
