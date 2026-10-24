# P012-T011 — Presets de agentes en la UI con local-config-8

Fecha: 2026-10-24. Base: `a7d8b33`. **Estado: corregida y verificada offline.**
Decisiones: D194/D195 y [D196](../DECISIONS.md#d196--p012-t011-paridad-del-selector-de-presets-ui-con-local-config-8).
Origen: [parada de T002 antes del alta](P012-T002_PROPUESTA_T010.md#8-preparación-aprobada-y-parada-por-selector-de-presets-v8).

## 1. Defecto y corrección

El backend admite presets en `local-config-8`, pero el componente compartido `DraftFields` de Registry conserva
una lista de formatos limitada a v5/v6/v7. En el wheel de T010 la UI interpreta v8 como formato sin selección
por proyecto: oculta el selector y conserva la pareja heredada. T002 necesitaba los presets propios del clon
para que el ejecutor recibiera su PATH/TMPDIR aprobado, por lo que se detiene antes de registrar o llamar modelos.

La corrección añade **v8** a esa lista y actualiza el aviso de formatos admitidos en **en/es**. No cambia el
contrato de D194: devuelve a la UI la selección que el backend ya soporta. El formulario compartido cubre
registro, creación y actualización; no se introducen rutas API, flags o capacidades nuevas. No se cambia la
pareja, política, permisos, entorno, huellas, recetas o interpretación del TOML del servicio.

Se exporta el componente existente `DraftFields` para comprobar su render real. No se extrae su lógica ni se
expone una API HTTP nueva. Un helper de tests usa `node:module.registerHooks` y el TypeScript ya instalado para
transpilar los módulos UI locales y cargar sus catálogos; no añade dependencias ni participa en la aplicación.

## 2. Verificación

Ocho regresiones en `frontend/tests/registry.test.mjs`, usando React/ReactDOM reales y el proveedor de idioma:

- Formulario v8 en **registro/creación/actualización × en/es**: muestra los presets seleccionados por rol,
  modelo y esfuerzo; cada preset solo se ofrece en su selector y desaparece el aviso de formato incompatible.
- V5/v6/v7 siguen mostrando presets; v1–v4, formato ausente y v9 desconocido conservan el aviso/fallback.
- V8 sin presets conserva el aviso de ausencia de presets del operador; no aparenta tener una pareja elegible.

El render es de servidor, no monta efectos y bloquea cualquier `fetch`: ni navegador, servicio ni proveedores.
Se comprueba el formulario real, no una copia de la constante o una búsqueda textual sobre su implementación.

```sh
node --test frontend/tests/registry.test.mjs
node --test frontend/tests/*.test.mjs
npm --prefix frontend run build
```

Resultado: **8 regresiones y 103 tests Node correctos**; **TypeScript y build Vite correctos**. Aviso existente
de chunks mayores de 500 kB, sin fallo. No se repiten suites Python/unittest/Alembic: no cambia backend, datos
o migraciones. El verificador de distribución que pasó durante T002 corresponde al wheel anterior a esta
corrección; no se le atribuye la UI nueva. Sin build/instalación de otro wheel, servicio, modelos o QA de navegador
tras la corrección. El build frontend es un check local, no una instalación operativa.

## 3. Conservación y documentos

T002 conserva B/B2, sus dos diffs, 13.785 filas SQLite previas idénticas, configuraciones y distribuciones;
servicio parado, 7 DONE/9 STOPPED/0 locks. Consumo **Claude 7/12, Codex 2/3**, sin llamadas nuevas en el tramo.
El clon preparado `managed-b-t010` está limpio, sin registro, fase o commits nuevos; su venv/TMPDIR y TOML
quedan conservados. No se repara, formatea o revalida ningún resultado fallido de los agentes.

STATE, NEXT_STEPS, ROADMAP y DECISIONS reflejan el resultado parcial y esta corrección. No cambia el flujo
implementado: se mantienen `flows/project-agents.md`, documentos/fases/tarea y DDBB-DIAGRAM; baseline pública
pendiente de T005. Los artefactos históricos y D001–D194 no se reescriben. La propuesta de T010 mantiene sus
parámetros históricos y añade consentimiento/resultados con procedencia.

Comprobación documental: **12 fases, 7 criterios P012, 11 tareas, 196 decisiones y 603 enlaces/anclas**
relativos válidos en los seis Markdown modificados/nuevos. STATE/base/NEXT_STEPS: **14.035/24.576**,
**8.914/12.288**, **26.575/49.152 bytes**. Cuerpos D001–D194 y archivos históricos/públicos conservados;
diff revisado y `git diff --check` correcto. El criterio de ROADMAP cita v8 conforme a D194, con v7 conservado.

## 4. Próximo paso, todavía sin autorizar

T002 necesita una propuesta de reanudación revisable desde el commit de esta corrección, con nueva distribución
**`AREA/dist-t011`** y venv **`AREA/venv-t011`**, sin sobrescribir los anteriores. Puede conservar el clon limpio
`managed-b-t010` y el TOML v8 de hash **`e0e95abb…fbb6db`**: el alta nunca se envió, no hay tarea ni resultado
nuevo que reutilizar. Verificar sus manifiestos/hash/modos, estado SQLite y ausencia de registro antes de usarlos;
si difieren, parar. No crear otro clon o cambiar nombres/presets por defecto sin concretarlo antes.

Revisar comandos/hashes y pedir consentimiento para build/verificador/instalación offline, preflight y ocho
checks iniciales del clon, servicio 8024, registro/P001, los dos commits documentales y una única tarea conforme
a la propuesta anterior. Mismas selecciones/rutas/guardias, cero correcciones, máximo nuevo **2 Claude/1 Codex**,
acumulado máximo **9/12 y 3/3**. Una pregunta del producto que no pueda deducirse exige HITL antes del paso
dependiente. Sin otro B, T003/T004, reparación de resultados anteriores, descarga, cambio global, tag/push o
publicación. Ni esta corrección offline ni el saldo de llamadas autorizan reiniciar la operación detenida.
