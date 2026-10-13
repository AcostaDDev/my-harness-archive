# Siguiente tarea — H5.1 Importación JUnit y detalle de tests

H4.3 segundo perfil se completó offline el 2026-10-13 (D038).
`typescript-web` declara preparación npm offline desde lock, tipos, tests y build
estático, comandos y reglas. Fixture con Node 24.15.0, npm 11.12.1 y TypeScript
5.9.3; procesos reales por el puerto de prueba, agentes falsos y Git/SQLite
temporales hasta COMMITTED. Sin condiciones de stack nuevas en el núcleo.
Ver [entrega y límites](discovery/H4.3_TYPESCRIPT_PROFILE.md).

Estado verificado:

- esquema `0013_bootstrap` y codec conservados;
- 526 pruebas pytest y 121 subtests (16 nuevas de H4.3);
- 12 checks ligeros y 4 pruebas Node;
- check TypeScript del frontend; checks existentes de esquema/OpenAPI;
- preparación → tipos → tres tests Node → build con evidencia Git intacta;
- tarea corregida en worktree → ACCEPTANCE_READY → commit exacto → COMMITTED;
- fallos de tests/tipos/build/política, caché, engines y lock impiden continuar;
  permisos y snapshots conservados, cambios externos bloquean commit.

No se usaron proveedores ni se migró la SQLite de trabajo. El runner real es de
prueba para fixture confiable; no añade un ejecutor de comandos al servicio. La
plantilla de bootstrap H4.2 sigue siendo documental. **H5.1 no está iniciado.**
Los consentimientos de smokes siguen agotados.

## Objetivo y alcance (primer incremento del hito 5)

1. Importar reportes JUnit XML de validaciones y conservar el original con hash y
   procedencia vinculados al comando, intento y evidencia de contenido exacto.
2. Exponer detalle por test (id/suite/resultado/duración/error), distinguiendo
   datos observados, ausentes y parciales; no sumar duraciones como tiempo real.
3. Declarar rutas de reportes y cobertura de validación por perfil, sin introducir
   condiciones específicas de frameworks en el núcleo.
4. Incorporar consulta API/UI y pruebas offline con reportes sintéticos válidos,
   parciales e inválidos. Acotar el incremento a JUnit; otros trabajos del hito 5
   permanecen pendientes.

## Criterios de aceptación

- Un run conserva el reporte original y muestra detalle por test con procedencia
  y cobertura declarada; no presenta datos ausentes como éxitos o ceros.
- Reporte inválido/ausente/parcial produce diagnóstico explícito, sin fabricar
  casos ni reemplazar resultados observados del comando.
- El parser no lee rutas externas ni ejecuta contenido XML. Tests y review siguen
  vinculados al contenido exacto, sin aceptar ni hacer commit por el reporte solo.
- Pasan las regresiones offline pertinentes y se actualiza la documentación.

## Fuera de alcance

- Backup/restore, retención, empaquetado/distribución y demás incrementos de H5.
- Proveedores reales/smokes: autorización específica (D033 punto 8).
- App Server/SDK, sesión local, SSE gestionado, push y publicación.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.
