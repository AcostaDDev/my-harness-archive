# Siguiente tarea — H0.3 (pendiente)

H0.2 completado el 2026-10-11. [Alcance y criterios originales](discovery/H0.2_SCOPE.md)
conservados para revisión. Evidencias en
[compatibilidad y autenticación](discovery/H0.2_COMPATIBILITY.md),
[snapshot de versiones/resolución](discovery/h0.2-version-metadata.json) y
[streams sintéticos](../tests/fixtures/streams/README.md).
Esta entrega no inicia H0.3.

## Objetivo

Crear el esqueleto mínimo y verificar los límites del núcleo con una ejecución
simulada local, sin acceso a modelos ni adaptadores reales.

## Alcance de la siguiente sesión

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

## Criterios de aceptación

- Aplicación arranca localmente y muestra una ejecución simulada sin modelos.
- Núcleo no importa FastAPI, SDKs ni reglas específicas de proyectos.
- Persistencia y migración mínimas funcionan con datos sintéticos locales.
- Locks, comandos de arranque/build y checks pertinentes se han comprobado;
  distinguir instalación/ejecución del producto de la resolución de H0.2.

## Fuera de alcance

Importación legacy H1, extracción del motor H2, adaptadores reales, chat,
permisos interactivos, SDKs y distribución. No ejecutar harness, agentes,
tests/instalaciones en ReferenceProject ni modificar configuración global.
Las cuentas previstas siguen siendo suscripciones propias mediante CLI;
cualquier smoke real con proveedores exige autorización explícita de consumo
en una tarea posterior.
