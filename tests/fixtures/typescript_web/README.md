# Fixture web TypeScript — H4.3

Web estática sintética: un campo de tareas calcula una estimación de treinta
minutos por tarea. Sin backend, Docker, credenciales ni proveedores.

Node 24.15.0, npm 11.12.1 y TypeScript 5.9.3 (única dependencia, fijada en el lock).
`check` verifica tipos sin emitir; `test` compila y ejecuta tres tests con Node;
`build` compila y copia módulos e HTML a `dist/`. No hay bundler ni framework.
El test de interacción usa un DOM mínimo de prueba; no certifica un navegador.
Desde H5.1, `test` mantiene TAP en stdout y conserva el XML original del reporter
JUnit Node en `.local/junit.xml`, declarado por el perfil; no mide cobertura de código.

Las pruebas Python copian esta carpeta a un checkout temporal; una regresión de
45 minutos se introduce solo en esa copia para verificar ejecución, revisión y
commit. La fixture versionada pasa sus tests sin modificarla. `node_modules/`,
`.build/`, `dist/` y `.local/` se ignoran y no entran en la evidencia Git.

Recorrido completo, desde la raíz del repositorio:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q tests/product/test_typescript_profile.py
```

Requiere la caché `.local/npm-cache` poblada por la instalación documentada del
frontend (comparte el pin TypeScript 5.9.3). Una caché vacía provoca una parada
`ENOTCACHED`; las pruebas no descargan paquetes. Ver
[perfil, reproducción y límites](../../../docs/discovery/H4.3_TYPESCRIPT_PROFILE.md).
