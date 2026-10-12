# Siguiente tarea — H2.4: Git y aceptación offline

H2.3 verificado offline y smoke real completo el 2026-10-12 (D025), autorizado
por «Procede con el smoke»: planificador Codex, ejecutor Claude y revisor Codex
COMPLETE, terminal/exit 0/JSON `smoke-ok`, con USER validado. Sin herramientas
ni cambios de checkout. [Informe](discovery/H2.3_ENV_SMOKE.md),
[alcance completado](discovery/H2.3_ENV_SMOKE_SCOPE.md).
57 eventos, configuración/capturas/hashes exactos tras reabrir SQLite, job DONE,
run STOPPED por fin deliberado del smoke, owner cerrado y procesos STOPPED/dead;
lock nuevo liberado por finalización normal. D020/D022 y sus locks intactos.
Doce checks ligeros correctos; suite previa del mismo código: 219 pruebas y
121 subtests. Transporte real acreditado, sin aceptación/commit de tarea real.

**H2.4 no iniciado.** La autorización del smoke se satisfizo con una ejecución;
no permite otro consumo, login o recuperación de históricos.

## Objetivo

Implementar Git y aceptación según el backlog H2.4 y la especificación:
worktree por tarea, baseline/fingerprint del contenido completo y commit
limitado a lo validado/revisado, con recuperación idempotente tras caída.
Trabajo local offline con repositorios temporales sintéticos, sin proveedores.

## Alcance acotado

1. Revisar especificación (consistencia frente a caídas y Git), backlog H2.4,
   D015–D017/D025 y puertos del motor, aceptación, journal y persistencia.
   Señalar contradicciones materiales antes de cambiar diseño.
2. Implementar captura Git real: base SHA, contenido/diff completo, staged,
   unstaged, untracked y borrados relevantes. Vincular validación/review al
   contenido exacto; no certificar Git mediante SyntheticWorkspace.
3. Preparar worktree por tarea y conservarlo durante revisiones; preservar
   cambios ajenos y mantener la exclusión de escritor. Integrar en la rama de
   destino sigue siendo una acción separada, fuera de esta entrega.
4. Crear commit solo del conjunto revisado/autorizado y actualizaciones
   mecánicas identificadas. Persistir intención/evidencia antes del efecto y
   resultado después; conciliar commit creado antes de guardar resultado sin
   repetirlo tras reinicio ni aceptar contenido modificado externamente.
5. Añadir regresión offline con Git/SQLite y agentes falsos: invalidación tras
   modificación externa, staged/untracked, límites del commit, preservación de
   cambios ajenos y caída antes/después de crear commit. No usar runs privados.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE/NEXT_STEPS/
   DECISIONS e informe. Conservar H0/H1/H2 y locks/artefactos históricos.

## Criterios de aceptación

- Una modificación externa posterior a validación/review invalida aceptación;
  no se crea un commit de contenido distinto del revisado.
- Fingerprint/diff incluye archivos nuevos, staged y cambios pertinentes;
  baseline y evidencia conservados con procedencia y hash.
- Worktree aislado por tarea y conservado durante revisiones, sin limpiar
  modificaciones desconocidas ni tratarlo como sandbox de seguridad.
- Commit acotado a lo revisado; una caída después del efecto Git y antes del
  resultado SQLite se recupera sin duplicar commits ni reescribir historial.
- Tests offline pertinentes pasan y contratos/versiones/migraciones necesarios
  documentados; no presentar diseño como implementación.

## Fuera de alcance

Sin proveedores reales ni otro smoke, login/refresh, secretos, recuperación de
D020/D022, integración automática en rama destino, push/publicación, H2.5,
entradas gestionadas API/CLI/UI, permisos vivos, SDK, chat o distribución.
No modificar ReferenceProject, configuración global ni lanzar agentes de colaboración.
