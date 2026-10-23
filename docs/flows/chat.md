# Flujo — chat del proyecto

Preguntas sobre una instantánea de HEAD sin esperar al ejecutor, comandos deterministas y propuestas que solo se
convierten en tareas con confirmación (D035, D083).

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant API as API chat
    participant DB as SQLite
    participant L as Carril de chat
    participant R as Revisor (chat, solo lectura)
    U->>API: mensaje
    alt comando /estado /tests /siguiente /lote /check /cerrar /exportar /abrir-fase
        API-->>U: vista previa sin efectos (gramática cerrada, sin modelo)
        U->>API: misma confirmación que el control equivalente de la UI
    else comando /tarea texto
        API->>DB: turno QUEUED (chat_command) con propuesta determinista congelada
        L->>DB: ANSWERED con esa propuesta, sin exportar HEAD ni invocar al revisor
    else pregunta o petición
        API->>DB: turno QUEUED con contexto congelado
        L->>L: exporta el árbol de HEAD a una carpeta privada (sin .git ni enlaces)
        L->>R: chat-turn (sesión nueva)
        R-->>L: respuesta y propuesta opcional
        L->>L: compara la evidencia antes y después
        L->>DB: ANSWERED, FAILED, UNKNOWN o REFUSED
    end
    U->>API: aceptar propuesta (hash y versión)
    API->>DB: tarea normal en la fase activa (plan, ejecución, revisión, commit)
```

Las preguntas no toman el lock del checkout; las tareas aceptadas siguen el [flujo de tarea](task-run.md).
Los nombres de comando son tokens de protocolo y no se traducen; la respuesta de `/tarea` sigue el idioma visual
y el texto de la tarea propuesta, el idioma de trabajo (D169). Un turno cuyo escritor se confirma detenido queda
`UNKNOWN`, y uno rechazado antes de efectos, `REFUSED`; ninguno se reintenta solo.
Cada turno sella el idioma visual vigente al admitirlo ([preferencias de idioma](language-preferences.md)).

## Fuente en el código

- `core/engine/chat.py`, `core/engine/chat_commands.py`, `storage/chat.py`, `adapters/chat_snapshot.py`.
- Plantilla `chat-turn.md`.
