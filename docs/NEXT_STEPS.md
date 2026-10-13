# Siguiente tarea — H5.5 Assets web empaquetados y comando único de inicio

H5.4 diagnósticos locales de compatibilidad se completó offline el 2026-10-13
(D042). CLI explícita `diagnose-cli` y biblioteca, compartiendo preflight con el
adaptador: versión/help acotados, entorno explícito, resultados desconocidos o
incompatibles con pasos de corrección. No revela salidas libres ni credenciales;
no consulta autenticación ni inicia inferencia. Ver [entrega y límites](discovery/H5.4_DIAGNOSTICS.md)
y [alcance original](discovery/H5.4_SCOPE.md).

Esquema `0013_bootstrap`, codec 6, adaptador `cli-4` y locks conservados.
Pruebas offline sintéticas y regresión en STATE. Sin CLI reales, proveedores,
smokes, cambios globales ni SQLite de trabajo. **H5.5 no está iniciado.**
Los consentimientos de smokes siguen agotados.

## Objetivo y alcance (siguiente incremento del hito 5)

1. Empaquetar los assets web compilados con el producto para servirlos sin el
   checkout de desarrollo ni Node en ejecución.
2. Ofrecer una entrada local única de inicio, reutilizando FastAPI/Uvicorn,
   configuración explícita, guardias y comportamiento opt-in existentes.
3. Documentar instalación reproducible y arranque, verificando un paquete en un
   entorno temporal limpio con datos sintéticos y sin proveedores.

## Criterios de aceptación

- El paquete contiene los assets necesarios y sirve la UI y API desde loopback
  sin depender del cwd ni del checkout de desarrollo.
- Un comando documentado inicia el servicio; configuración/errores de esquema
  tienen diagnóstico claro, sin migraciones destructivas o correcciones silenciosas.
- No se activan proveedores, proyectos, observadores ni supervisor sin opt-in;
  restauraciones conservan la guardia de consulta.
- Locks y versiones explícitos; construcción e instalación temporal verificadas,
  sin cambios globales, publicación ni uso de datos privados.
- Pruebas pertinentes y documentación de requisitos y límites actualizada.

## Fuera de alcance

- Sesión local (incremento posterior del hito 5), SSE gestionado, App Server/SDK,
  reactivación de restauraciones, backup Git, push y publicación.
- Proveedores/smokes y diagnóstico real de autenticación: requieren autorización
  específica (D033 punto 8). No incorporar una instalación global automática.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.
