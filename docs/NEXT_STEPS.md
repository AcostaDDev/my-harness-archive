# Siguiente paso: H6.2 E5, chat global (D076)

Estado al 2026-10-15:

- **H6.2 E4 implementada y verificada offline (D081–D082).** [Entrega, verificación y límites](discovery/H6.2_E4_SETUP.md).
  Incluye:
  - `/projects/:p/setup`: brief, turnos de `definition`, borradores (aplicar, descartar y editar con CAS y diff),
    preguntas aplazadas con motivo, aceptación con bloqueos y archivos del commit raíz, y primera tarea.
  - `/projects/:p/phases/:code/plan` y transición con plan propuesto en la fase terminada.
  - D081 (decisión del usuario): en v2 las rutas protegidas del perfil limitan al ejecutor, no a las escrituras
    documentales confirmadas; `typescript-web` + v2 ya puede crearse y pasar de fase.

  QA con Chrome sobre `scripts/dev` y datos sintéticos: recorrido completo del hito desde la UI (alta → creación →
  primera tarea → revisión → commit → cierre → transición con plan propuesto), claro, oscuro y 386 px.
- [Alcance de H6.2](discovery/H6.2_SCOPE.md): E5 chat global → E6 estadísticas.
- Límites conocidos: 2 avisos *low* de KaTeX (dependencia de Mermaid) hasta poder fijar Mermaid 12 con dos semanas; un
  proyecto `typescript-web` recién creado no tiene `package.json` y el ejecutor no puede crearlo (ruta protegida), así
  que su preparación real fallaría. Esto último necesita una decisión aparte.

## Tarea concreta propuesta, no iniciada

**H6.2 E5 — Chat global** ([alcance §E5](discovery/H6.2_SCOPE.md#e5--chat-global)).

1. Backend: turnos de chat sobre una instantánea de solo lectura del HEAD (worktree temporal o árbol exportado), sin el
   lock del checkout, comparando la evidencia de la instantánea antes y después. Las propuestas aceptadas siguen creando
   tareas normales. Cambia D035 de forma deliberada: registrar la decisión.
2. Comandos deterministas (`/estado`, `/tests`, `/siguiente`, `/lote`, `/check`, `/cerrar`, `/exportar`,
   `/abrir-fase`, `/tarea <texto>`), reconocidos por sintaxis, sin modelo, con las mismas confirmaciones que el botón
   equivalente. Ninguno concede permisos ni se salta una confirmación.
3. UI `/projects/:p/chat[/:conversation]` con varias conversaciones y contexto de fase o tarea.

Criterios: la instantánea no deja worktrees huérfanos tras una caída (recuperación probada); ninguna acción repite
efectos al recargar; confirmaciones ligadas a hash y versión; turnos con agentes falsos; QA con navegador en claro,
oscuro y estrecho. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
