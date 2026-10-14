# Siguiente paso: H6.2 E2, registro de proyectos (D076)

Estado al 2026-10-14:

- **H6.2 E1 implementada y verificada offline (D077).** [Entrega, diseño y límites](discovery/H6.2_E1_SHELL.md).
  Incluye:
  - Enrutador propio con las URLs de D072 §7 y enlace corto `/runs/:id`.
  - Fallback de la UI en el servidor del wheel.
  - Lecturas por código de fase y resumen de tareas por fase.
  - Shell con migas, supervisor, tema y sesión.
  - Sistema de diseño claro y oscuro con el raíl del ciclo de vida de la fase.
  - Las pantallas anteriores repartidas por URL.

  QA con Chrome sobre la demo sintética, en el build y en Vite.
- [Alcance de H6.2](discovery/H6.2_SCOPE.md): E2 registro → E3 documentación → E4 creación y planificación → E5
  chat global → E6 estadísticas.

## Decisión pendiente del usuario (hallazgo de E1)

La guardia de sesión H5.6 rechaza con `origin_rejected` toda petición con `Sec-Fetch-Site: cross-site`, también la
carga de la propia página. Un enlace a una URL del harness pulsado desde otro sitio (correo, chat) no la abre; escribir
la URL, usar un marcador o recargar sí funcionan. Opciones:

- mantenerlo así;
- admitir solo navegaciones `GET` de documento (`Sec-Fetch-Mode: navigate`) fuera de `/api/`, que solo entregan la
  página estática sin datos.

No se ha cambiado nada.

## Tarea concreta propuesta, no iniciada

**H6.2 E2 — Registro de proyectos** ([alcance §E2](discovery/H6.2_SCOPE.md#e2--registro-de-proyectos-d054)).

1. Formato `local-config-3`: composiciones con nombre (ejecutables, entorno, límites y comandos autorizados del
   perfil), raíces bajo las que la UI puede registrar y `bootstrap_enabled`. `local-config-1` y `-2` se siguen
   leyendo; sus `[[projects]]` no se editan desde la UI.
2. Migración nueva: registro de proyectos versionado y auditado, con baja lógica.
3. API de alta, cambio y baja con vista previa y confirmación ligadas a hash y versión, y la confianza como
   confirmación aparte. Sin ids repetidos con el TOML; raíz canónica bajo una raíz autorizada, sin enlaces y fuera
   del estado del servicio.
4. El hash de la composición congelada incluye la versión del registro; cambiar un proyecto con jobs pendientes se
   rechaza. El runtime incorpora el proyecto sin reiniciar, sin romper la congelación por job ni la exclusión de un
   escritor por checkout.
5. UI en `/projects/new` y en ajustes del proyecto.

Criterios: registro de una carpeta sintética desde la UI hasta su primera tarea sin editar archivos; rechazos
probados (raíz fuera de las autorizadas, enlace, id duplicado, confianza sin confirmar, versión obsoleta);
configuraciones anteriores intactas; QA con navegador. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
