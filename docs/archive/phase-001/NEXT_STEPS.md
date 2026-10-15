# Plan archivado — P001 Contratos y prueba de viabilidad (antes H0)

Reconstruido en P008-T001 (D088) a partir de la sección del backlog y de los alcances que `docs/discovery/*_SCOPE.md` conservaba de `docs/NEXT_STEPS.md` antes de cada entrega (hasta `8622a43`). Los enlaces apuntan al archivo de cada fase.

## Plan del backlog

### Hito 0 — Contratos y prueba de viabilidad

#### H0.1 Inventario reproducible

- Registrar el commit de referencia del repositorio original y hash de archivos locales relevantes; distinguir cambios sin commit.
- Clasificar código reusable, reglas ReferenceProject y formatos legacy.
- Crear fixtures sintéticos de tarea aceptada, revisión, bloqueo, interrupción y cierre.
- Criterio: los fixtures contienen los formatos necesarios y ningún secreto, prompt privado o dato de aplicación real.

#### H0.2 Decisiones y compatibilidad

- Fijar versiones de Python, dependencias y herramientas de frontend compatibles.
- Comprobar las versiones instaladas de Codex/Claude y sus interfaces de salida.
- Documentar modos de autenticación por adaptador y cuentas previstas, sin extraer credenciales.
- Probar offline parsers de streams truncados, errores y campos desconocidos.
- Criterio: matriz de capacidades documentada; no se presenta permiso interactivo donde solo existe denegación.

#### H0.3 Esqueleto y límites

- Crear núcleo Python, API local mínima, UI React, persistencia y adaptadores falsos.
- Definir modelos Pydantic y contratos HTTP; generar tipos frontend desde OpenAPI cuando se introduzca el cliente.
- Criterio: aplicación arranca localmente y muestra una ejecución simulada sin acceso a modelos.

## Alcances conservados

### H0.1 — Alcance y criterios originales

_Origen: `docs/discovery/H0.1_SCOPE.md`._

#### Objetivo

Documentar la base reusable del harness de ReferenceProject y preparar fixtures sintéticos para desarrollar el importador sin agentes reales.

#### Alcance

1. Registrar commit de referencia, estado de cambios locales y hashes de archivos relevantes; no modificar el origen.
2. Inventariar operaciones, formatos y dependencias específicas de ReferenceProject.
3. Documentar contratos mínimos de tarea, intento, revisión, validación, bloqueo y fase.
4. Crear fixtures sintéticos en `tests/fixtures/legacy/` para aceptación, REVISE, BLOCKED, interrupción y cierre. Añadir un README que explique qué representa cada fixture.
5. Añadir una comprobación offline proporcional de coherencia/parseo si aporta verificación real.
6. Actualizar estado y siguiente tarea con evidencias.

#### Entregables

- `docs/discovery/BASELINE.md`: procedencia y separación de núcleo/perfil.
- `docs/discovery/LEGACY_FORMATS.md`: formatos, campos opcionales y límites históricos.
- Fixtures sintéticos y sus comprobaciones.

#### Criterios de aceptación

- Es posible rastrear los formatos a archivos/funciones del origen y a una revisión identificada.
- Ningún fixture contiene datos reales, secretos o transcripciones copiadas.
- Casos completos, incompletos y campos no registrados se distinguen.
- Ningún agente, instalación ni test de ReferenceProject se ejecuta.
- Se informa de verificaciones realizadas y límites del inventario.

#### Fuera de esta tarea

Construir API/UI, portar el motor, instalar toda la infraestructura, definir todos los esquemas futuros o lanzar llamadas a modelos. H0.2 y H0.3 vienen después.

### Siguiente tarea — H0.2 (pendiente)

_Origen: `docs/discovery/H0.2_SCOPE.md`._

Alcance conservado desde NEXT_STEPS antes de iniciar H0.2. Los criterios no
han cambiado; los enlaces se ajustan a la ubicación de este archivo.
La entrega completada figura en [H0.2_COMPATIBILITY.md](H0.2_COMPATIBILITY.md).

H0.1 completado el 2026-10-11. [Alcance y criterios originales](NEXT_STEPS.md)
conservados para revisión. Evidencias en [BASELINE.md](BASELINE.md),
[LEGACY_FORMATS.md](LEGACY_FORMATS.md) y los
[fixtures](../../../tests/fixtures/legacy/README.md). La entrega H0.1 no inició H0.2 ni H0.3.

#### Objetivo

Resolver versiones, capacidades y autenticación de las interfaces previstas antes
de crear el esqueleto. Usar el inventario de H0.1 como referencia histórica;
no asumir que su configuración o esquemas prueban compatibilidad actual.

#### Alcance de la siguiente sesión

1. Fijar versiones compatibles de Python, dependencias y herramientas frontend,
   verificando disponibilidad y documentación oficial; no anunciar scripts inexistentes.
2. Comprobar versiones e interfaces de salida de Codex/Claude instalados sin lanzar
   agentes ni el harness. Documentar capacidades CLI y las dudas de App Server/SDK.
3. Documentar modos de autenticación y cuentas previstas sin extraer credenciales.
   Solicitar al usuario solo la información que no pueda comprobarse en lectura.
4. Añadir muestras y checks offline pequeños de streams truncados, errores y campos
   desconocidos. Conservar ausencia de telemetría; evitar una suite costosa.
5. Registrar decisiones y actualizar STATE/NEXT_STEPS al completar esa tarea.

#### Criterios de aceptación

- Matriz de versiones/capacidades documentada con fuentes y límites de comprobación.
- Autenticación por adaptador aclarada sin secretos en repositorio/logs/fixtures.
- No presentar permiso interactivo donde solo existe denegación (`dontAsk`).
- Parsers offline verifican muestras truncadas, errores y campos desconocidos sin
  llamadas reales ni reintentos/fallback silenciosos.

#### Fuera de alcance

API/UI, base de datos y esqueleto H0.3; portar el motor; ejecutar el harness o
tests/instalaciones en ReferenceProject. Cualquier smoke real con proveedores requiere
autorización explícita de consumo en una tarea posterior.

### Siguiente tarea — H0.3 (pendiente)

_Origen: `docs/discovery/H0.3_SCOPE.md`._

Alcance conservado desde NEXT_STEPS antes de cerrar H0.3. Los criterios no
han cambiado; los enlaces se ajustan a esta ubicación. Evidencias de la entrega
en [H0.3_SKELETON.md](H0.3_SKELETON.md).

H0.2 completado el 2026-10-11. [Alcance y criterios originales](NEXT_STEPS.md)
conservados para revisión. Evidencias en
[compatibilidad y autenticación](H0.2_COMPATIBILITY.md),
[snapshot de versiones/resolución](h0.2-version-metadata.json) y
[streams sintéticos](../../../tests/fixtures/streams/README.md).
Esta entrega no inicia H0.3.

#### Objetivo

Crear el esqueleto mínimo y verificar los límites del núcleo con una ejecución
simulada local, sin acceso a modelos ni adaptadores reales.

#### Alcance de la siguiente sesión

1. Crear paquete de núcleo Python independiente de API, proveedores y perfiles;
   API FastAPI mínima y UI React/TypeScript/Vite.
2. Incorporar las dependencias necesarias con los pins de H0.2 y generar locks
   reales mediante uv/npm. Verificar instalación, arranque y build; los pins
   de tests futuros no obligan a añadir suites o dependencias sin uso ahora.
3. Añadir persistencia mínima SQLite/SQLAlchemy/Alembic y adaptadores falsos
   suficientes para mostrar una ejecución simulada. No portar aún el motor.
4. Definir modelos Pydantic y contratos HTTP; generar tipos frontend desde
   OpenAPI al introducir el cliente, sin duplicar contratos manualmente.
5. Documentar únicamente comandos comprobados en README/AGENTS; actualizar
   STATE/NEXT_STEPS y registrar decisiones duraderas al terminar.

#### Criterios de aceptación

- Aplicación arranca localmente y muestra una ejecución simulada sin modelos.
- Núcleo no importa FastAPI, SDKs ni reglas específicas de proyectos.
- Persistencia y migración mínimas funcionan con datos sintéticos locales.
- Locks, comandos de arranque/build y checks pertinentes se han comprobado;
  distinguir instalación/ejecución del producto de la resolución de H0.2.

#### Fuera de alcance

Importación legacy H1, extracción del motor H2, adaptadores reales, chat,
permisos interactivos, SDKs y distribución. No ejecutar harness, agentes,
tests/instalaciones en ReferenceProject ni modificar configuración global.
Las cuentas previstas siguen siendo suscripciones propias mediante CLI;
cualquier smoke real con proveedores exige autorización explícita de consumo
en una tarea posterior.
