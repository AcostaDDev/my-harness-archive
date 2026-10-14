# Siguiente paso: H6.2 E3, documentación (D076)

Estado al 2026-10-14:

- **H6.2 E2 implementada y verificada offline (D078).** [Entrega, API y límites](discovery/H6.2_E2_REGISTRY.md).
  Incluye:
  - `local-config-3` con raíces de registro, techo de bootstrap y composiciones con nombre; v1/v2 intactos.
  - Registro en SQLite (`0016_project_registry`), versionado, auditado y con baja lógica.
  - API de vista previa y confirmación ligada a hash y versión, con la confianza aparte.
  - Incorporación en caliente con la versión del registro en el hash congelado.
  - UI en `/projects/new` y en los ajustes del proyecto.

  QA con Chrome sobre `scripts/dev` con datos sintéticos: alta → primera tarea → aceptada, cambio y baja.
- [Alcance de H6.2](discovery/H6.2_SCOPE.md): E3 documentación → E4 creación y planificación → E5 chat global → E6
  estadísticas.

## Decisión pendiente del usuario (hallazgo de E1)

La guardia de sesión H5.6 rechaza con `origin_rejected` toda petición con `Sec-Fetch-Site: cross-site`, también la
carga de la propia página. Un enlace a una URL del harness pulsado desde otro sitio (correo, chat) no la abre; escribir
la URL, usar un marcador o recargar sí funcionan. Opciones:

- mantenerlo así;
- admitir solo navegaciones `GET` de documento (`Sec-Fetch-Mode: navigate`) fuera de `/api/`, que solo entregan la
  página estática sin datos.

No se ha cambiado nada.

## Tarea concreta propuesta, no iniciada

**H6.2 E3 — Documentación** ([alcance §E3](discovery/H6.2_SCOPE.md#e3--documentación)).

1. Dependencias nuevas fijadas: `markdown-it` (`html: false`) y `mermaid` (`securityLevel: "strict"`, carga diferida
   solo en la documentación), con versiones de al menos dos semanas. La instalación necesita red una vez y actualiza
   `package-lock.json`; medir el bundle con la carga diferida.
2. Árbol `/projects/:p/docs/*path` y visor. Enlaces solo relativos y `http(s)`; imágenes del repositorio servidas por la
   API, nunca hacia fuera.
3. Editor con hash base, vista previa del diff y confirmación de `document_edit`: conflictos de CAS, deriva («cambios
   locales sin confirmar»: confirmar o regenerar), bloques gestionados bloqueados, `archive/**` en solo lectura y los
   bloqueos que provoca la deriva.
4. Ruta nueva en el enrutador y en la navegación del proyecto.

Criterios: Markdown sin HTML ejecutable, probado con casos hostiles (`<script>`, `javascript:`, `on*=`, SVG/Mermaid
con HTML incrustado) con `node --test`; edición confirmada sin repetir efectos al recargar; QA con navegador en claro,
oscuro y estrecho. Actualizar STATE, NEXT_STEPS y DECISIONS al terminar.

D071 y los consentimientos anteriores siguen agotados. Cualquier prueba real requiere una propuesta y un
consentimiento nuevos. Sin push ni publicación.
