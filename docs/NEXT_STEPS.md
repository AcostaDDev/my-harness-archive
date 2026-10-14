# Siguiente paso — diagnóstico offline y revisión de la frontera candidata

Estado al 2026-10-14:

- **Calificación sintética D064 completada.** [Dictamen y matriz](discovery/CODEX_CONTAINMENT_QUALIFICATION.md),
  [evidencia](discovery/CODEX_CONTAINMENT_QUALIFICATION.json) y
  [sonda reproducible](discovery/CODEX_CONTAINMENT_QUALIFICATION.py).
- **Candidata D063 no calificada para integración tal como está.** Escrituras
  directas contenidas, pero fd heredado, hardlink preexistente y delegación
  por pipe modifican fixtures exteriores. Control con fd cerrado correcto;
  precheck de raíces no certifica ausencia de carreras. Socket Unix propio
  denegado no prueba aislamiento IPC general.
- Sandbox anidado escritor sintético correcto; lector rechazado por el SO
  antes del objetivo. No se ejecutó el perfil interno real de Codex.
- 27 escenarios finales completos y 14 pytest focales correctos. HOME/auth
  ficticios conservados; sin CLI real, red externa ni integración de producto.
  cli-7, local-config-2, permisos D024/D059 e historiales conservados.
- D060 cerrada con parada preventiva (D061): 2 Codex→Codex COMMITTED
  (`585a35c`), 3/4 no lanzadas. La 1 D057 ya completa; Claude real con esquema
  tipado D058 sigue pendiente. D062 acreditó delta de confianza de 93 bytes;
  atribución al proceso original inferida. Configuración global conservada.

## Tarea concreta propuesta, no iniciada

**Diagnosticar offline el rechazo del sandbox anidado lector y concretar una
frontera revisada, antes de decidir cualquier integración en producto.**

1. Aislar el rechazo observado en D064 mediante perfiles y procesos sintéticos
   mínimos. Distinguir limitación del SO, composición y condición del perfil;
   no trasladar conclusiones a la CLI real sin evidencia.
2. Evaluar si existe una composición viable conservando sandbox interno,
   HOME/auth en origen y prohibición de escritura global. No eliminar capas,
   ampliar permisos ni cambiar el almacén para hacer pasar el ensayo.
3. Delimitar medidas y criterios verificables para descriptores, hardlinks/
   carreras y delegación. Usar únicamente servicios propios y datos ficticios;
   no tocar llavero, launch services, Mach/XPC reales ni credenciales.
4. Emitir propuesta revisada o incompatibilidad precisa. Señalar cualquier
   cambio material de aislamiento/auth/efectos aceptados antes de implementarlo.
   Mantener separado el problema de refresh remoto, no resuelto por denegar save.

Criterios: reproducción con datos exclusivamente sintéticos, errores sin
fallback, originales conservados salvo fixtures sacrificiales explícitos,
observaciones separadas de hipótesis y límites de red/IPC/auth documentados.
Ningún cambio al adaptador, TOML operativo, jobs, baseline/modelos/permisos o
historiales. El núcleo permanece independiente del SO. Actualizar
STATE/NEXT_STEPS/DECISIONS y registrar el dictamen.

La integración será otra tarea solo tras resolver el dictamen. Una comprobación
real requiere propuesta y consentimiento específicos nuevos, incluyendo el
límite de refresh de D063/D064; no está autorizada aquí. No iniciar otro
smoke/matriz, CLI real (ni version/help), jobs, recuperación, liberación de
locks, publicación, push o H6.2. D050/D055/D057/D060 siguen agotados.

Después, y aparte: hito de interfaz de producto (D054, H6.2). Alternativas
pendientes: `forbidden_paths` frente a prosa; instalación de operación
reutilizable (D051); `memory/` vacío de Claude; endurecimientos de D048.
Ninguna iniciada en D064.
