# Siguiente paso: H6.2 E1, shell, navegación y sistema de diseño (D076)

Estado al 2026-10-14:

- **Alcance de H6.2 fijado con el usuario (D076).** [Alcance, entregas y criterios](discovery/H6.2_SCOPE.md).
  Registro híbrido TOML + SQLite, `markdown-it` y Mermaid diferido, chat global con backend sin lock en
  entrega propia, y enrutador y CSS propios. Seis entregas en orden: E1 shell → E2 registro → E3
  documentación → E4 creación y planificación → E5 chat global → E6 estadísticas.
- H6.3–H6.5 implementados offline (D073–D075); sus contratos son la base de la UI. Ninguna entrega de H6.2
  se ha iniciado.

## Tarea concreta propuesta, no iniciada

**H6.2 E1 — Shell, navegación y sistema de diseño** ([alcance §E1](discovery/H6.2_SCOPE.md#e1--shell-navegación-y-sistema-de-diseño)).
Usar el plugin de diseño (`frontend-design`) desde el principio.

1. Enrutador mínimo propio sobre History API con las rutas de D072 §7, enlace directo, recarga, historial
   y un 404 útil. Resolución de `PNNN` y `PNNN-TNNN` a ids (con una lectura por código si las existentes
   obligan a traer listas completas).
2. Fallback del servidor del wheel: `index.html` en `GET` fuera de `/api/`. Los 404 de la API siguen en JSON.
3. Sistema de diseño con tokens, modo claro y oscuro, tipografía, tablas, estados (vacío, carga, error,
   bloqueado) y cabecera con sesión.
4. Pantallas actuales (fases, permisos, logs, tests, prompts y bootstrap v1) trasladadas a sus URLs con carga
   por recurso. La legacy H1 va a `/legacy` y las simulaciones salen de la navegación. Agentes (H6.1) en
   solo lectura en ajustes.

Criterios: cada URL de E1 se abre por enlace directo y recarga en `scripts/dev` y desde el wheel. Ninguna
acción repite efectos al recargar. Pruebas `node --test` del enrutador y pruebas pytest del fallback. QA
visual con navegador sobre la demo sintética en claro, oscuro y ancho estrecho. Siguen en verde pytest,
`tsc`, el build y las pruebas Node. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar. No avanzar a E2.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
