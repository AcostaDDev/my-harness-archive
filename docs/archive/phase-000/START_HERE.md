# Empezar con Codex y alternar con Claude Code

## 1. Abrir el proyecto correcto

En la aplicación Codex, añade o abre la carpeta `$HOME/Documents/projects/my_harness` como proyecto local y crea un chat dentro de ese proyecto. Para empezar, trabaja sobre la carpeta local, sin crear otro worktree vacío.

Alternativa desde una terminal, con Codex CLI instalado:

```sh
cd $HOME/Documents/projects/my_harness
codex
```

Codex CLI estaba disponible en el equipo al preparar estos archivos. Esto no prueba que la cuenta esté autenticada; si solicita acceso, sigue su inicio de sesión normal. No copies tokens a archivos del proyecto.

Codex carga automáticamente `AGENTS.md` al iniciar en el proyecto. Ya está creado: no hace falta generar otro con `/init`. [Documentación oficial de AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Codex CLI](https://learn.chatgpt.com/docs/cli).

## 2. Primer mensaje

Copia este mensaje:

> Lee AGENTS.md, docs/STATE.md, docs/NEXT_STEPS.md y docs/DECISIONS.md. Ejecuta H0.1 completo: inventario de la referencia y fixtures sintéticos, siguiendo sus criterios de aceptación. Puedes crear los archivos y realizar las comprobaciones offline necesarias en este repositorio. No ejecutes el harness de ReferenceProject ni llamadas a proveedores. Actualiza el estado y la siguiente tarea al terminar. No avances todavía a H0.2 ni H0.3.

Este mensaje solicita trabajo real: Codex puede leer, editar y comprobar, como Claude Code. No es necesario usar modo Plan para esta tarea ya definida. Conserva los permisos normales de trabajo local; no necesitas acceso irrestricto.

La referencia ReferenceProject queda fuera de esta raíz. Si la nueva sesión no puede leerla, concede acceso de lectura mediante los mecanismos de la aplicación; no amplíes escritura ni traslades sus runs al proyecto.

## 3. Revisar la primera entrega

Comprueba el resumen, el diff, las verificaciones y el estado actualizado. Puedes pedir a Codex que explique cualquier decisión o ajuste la entrega. Antes de empezar otra tarea, guarda un checkpoint Git cuando estés conforme.

El repositorio se ha preparado sin commits automáticos. Puedes guardar la documentación inicial antes de trabajar:

```sh
git add README.md AGENTS.md CLAUDE.md .gitignore docs
git commit -m "docs: establish local harness development baseline"
```

Si Git requiere identidad, configura la identidad que tú utilices; no inventar nombre/correo ni cambiar configuración global automáticamente.

## 4. Alternar con Claude Code

Cuando Codex termine y no siga editando, abre Claude Code en la misma raíz. `CLAUDE.md` le indica leer las mismas instrucciones y estado.

Mensaje de revisión recomendado:

> Lee CLAUDE.md y revisa la entrega H0.1 contra docs/NEXT_STEPS.md y el backlog. Comprueba los criterios originales de H0.1, aunque NEXT_STEPS ya señale otra tarea. Señala defectos concretos con evidencia. No modifiques archivos todavía ni ejecutes agentes/proveedores.

Si quieres que Claude implemente la siguiente tarea, pídeselo directamente tras la revisión. Evita dos sesiones implementando los mismos archivos a la vez. El trabajo en paralelo requerirá tareas y worktrees separados; no es necesario al comenzar.

## 5. Continuar

Después de aceptar H0.1, pide completar H0.2; después H0.3. Cada sesión debe dejar STATE y NEXT_STEPS actualizados. Puedes abrir chats nuevos porque el contexto duradero vive en el repositorio, no solo en la conversación.

No necesitas ahora Celery, broker, Docker del servicio, claves API nuevas ni una configuración Codex especial. La comprobación de cuentas/integraciones llega en H0.2; la primera llamada de prueba real requerirá autorizar su consumo.
