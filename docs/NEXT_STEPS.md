# Siguiente tarea — H2.5: migración a modo gestionado

H2.4 completado y verificado offline el 2026-10-12 (D026): captura Git completa
vinculada a árboles, worktree por tarea y commit determinista conciliable tras
caídas, con intención/resultado en `managed_commits` (`0006_git_commits`).
[Informe](discovery/H2.4_GIT.md), [alcance completado](discovery/H2.4_SCOPE.md).
253 pruebas y 121 subtests, 12 checks ligeros correctos. Sin proveedores, smoke
nuevo ni commits de producto reales.

**H2.5 no iniciado.** Los consentimientos de smokes anteriores están agotados;
esta tarea es offline y no autoriza proveedores, login ni recuperación de D020/D022.

## Objetivo

Implementar la migración controlada de un checkout legacy a modo gestionado según
el backlog H2.5 y la especificación: vista previa de importación, copia consistente
y comprobación de modo exclusivo, con reglas de autoridad para documentos y base
de datos. Trabajo local con checkouts y SQLite sintéticos.

## Alcance acotado

1. Revisar especificación (autoridad de datos, migración controlada), backlog H2.5,
   D012–D016/D026 y el estado legacy observado (H1). Señalar contradicciones
   materiales antes de cambiar diseño; definir qué dato pasa a ser autoridad de
   SQLite y cuáles siguen como documentos de lectura.
2. Vista previa de importación sin escribir: qué runs/tareas/fases se activarían,
   qué quedaría como histórico de solo lectura y qué ausencias/incertidumbres
   existen. Reutilizar el índice H1.1 sin crear intentos inferidos.
3. Copia consistente: capturar el estado legacy con identidad/hash de cada fuente y
   detectar cambios durante la copia; sin modificar el origen ni la base legacy.
4. Comprobación de modo exclusivo: el motor legacy y el gestionado no pueden operar
   a la vez sobre el mismo checkout (incluyendo raíces canónicas/alias y worktrees
   derivados). Reglas explícitas y persistidas; un fallo no activa nada.
5. Regresión offline con Git/SQLite sintéticos: activación atómica y reanudable,
   históricos importados accesibles, rechazo ante escritor legacy/gestionado
   concurrente, reinicio y fallos inyectados. No usar runs privados.
6. Ejecutar checks pertinentes, revisar diff y actualizar STATE/NEXT_STEPS/
   DECISIONS e informe. Conservar H0/H1/H2 y locks/artefactos históricos.

## Criterios de aceptación

- Motor legacy y gestionado no pueden gestionar simultáneamente el mismo checkout;
  el intento de hacerlo falla con diagnóstico y sin efectos parciales.
- La vista previa no escribe; la activación es atómica, idempotente y conserva
  autoridad/procedencia de cada dato importado sin duplicarla.
- Los históricos importados siguen accesibles tras activar; ausencias, null y cero
  se distinguen como en H1.
- Tests offline pertinentes pasan y contratos/versiones/migraciones necesarios
  documentados; no presentar diseño como implementación.

## Fuera de alcance

Sin proveedores reales ni otro smoke, login/refresh, secretos, recuperación de
D020/D022, integración automática en rama destino, push/publicación, H3,
entradas gestionadas API/CLI/UI, permisos vivos, SDK, chat o distribución.
No modificar ReferenceProject, configuración global ni lanzar agentes de colaboración.
