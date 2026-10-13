# Siguiente tarea — H4.3 Segundo perfil

H4.2 bootstrap guiado se completó offline el 2026-10-13 (D037).
Desde una carpeta vacía autorizada por el servidor recoge brief y decisiones,
ofrece una propuesta Codex opcional de solo lectura, previsualiza documentos y
crea un commit inicial conciliable, primera fase y tarea documental acotada.
Una carpeta no vacía conduce a importación, conservando sus bytes.
Ver [entrega y límites](discovery/H4.2_BOOTSTRAP.md).

Estado verificado:

- migración `0013_bootstrap`; codec anterior conservado;
- 510 pruebas pytest y 121 subtests (48 nuevas de H4.2);
- 12 checks ligeros y 4 pruebas Node;
- OpenAPI/tipos, TypeScript/build, `alembic check` en SQLite temporal;
- recorrido Chrome sintético: brief → propuesta → decisiones → preview → crear
  → fase ACTIVE → primera tarea → ACCEPTANCE_READY → commit → COMMITTED;
- reinicio/recarga con resultado conservado, y destino no vacío derivado a
  importación sin sobrescribir.

No se usaron proveedores ni se migró la SQLite de trabajo. La plantilla inicial
es documental, conserva el perfil configurado y no prepara ni instala un stack.
**H4.3 no está iniciado.** Los consentimientos de smokes siguen agotados.

## Objetivo y alcance (backlog H4.3)

1. Añadir un stack distinto del Django original, preferentemente un proyecto web
   TypeScript sencillo.
2. Declarar preparación, validaciones, comandos y reglas en un perfil separado.
3. Verificar preparación y tests con fixtures/checkouts sintéticos por los puertos
   existentes, sin condicionales específicos nuevos en el núcleo.
4. Documentar comandos reales, dependencias/locks y límites de la verificación.

## Criterios de aceptación

- Preparación y tests funcionan mediante el nuevo perfil.
- El núcleo no incorpora condiciones específicas del stack.
- Se conservan contratos, permisos, snapshots y evidencias del flujo gestionado.
- Pasan las comprobaciones offline pertinentes y se actualiza la documentación.

## Fuera de alcance

- Hito 5 y tareas posteriores.
- Proveedores reales/smokes: autorización específica (D033 punto 8).
- App Server/SDK, sesión local, SSE gestionado, push y publicación.

No lanzar colaboración automática ni usar el harness para desarrollar el repo.
