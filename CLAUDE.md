# Aeternea — reglas de operación

Wiki personal mantenida por un agente LLM. Obsidian es el IDE, tú eres el programador, el wiki es el código base. El usuario cura las fuentes y dirige; tú haces el resto: resumir, referenciar cruzado, archivar y mantener la consistencia.

> **Antes de escribir cualquier cosa en el wiki, lee `SCHEMA.md` entero.** Contiene las reglas duras — arquetipos, techos de palabras por nodo, vocabulario cerrado de ejes, versionado de identidad, salvaguarda fail-safe de contenido emocional y formato del log. No es opcional, y no se carga solo.

## Tres capas

- `01_Buffer_de_entrada/` — fuentes en crudo. **Inmutables**: se leen, nunca se modifican. Tras un ingest exitoso se **mueven** a `_procesados/` con prefijo `YYYY-MM-DD - `.
- `02_Wiki/` — nodos markdown generados por el LLM. Esta capa es tuya por completo.
- `SCHEMA.md` — las convenciones. Se co-evoluciona con el usuario.

## Regla de enrutado de índices

El wiki **no tiene índice maestro único**. Está bifurcado en dos silos estrictos:

1. `02_Wiki/index_tecnico.md` — arquitectura de software, código, IA, workflows, lógica de negocio.
2. `02_Wiki/index_personal.md` — diarios, reflexiones, relaciones, poesía, humanidades.

En cada ingest, evalúa la naturaleza de la fuente y enlaza la página nueva **solo** en el índice que le corresponde. El cross-linking entre silos está prohibido salvo petición explícita; la única excepción autorizada es el "hilo fino" de fuente mixta (SCHEMA §2).

**No busques ni crees un archivo llamado `index.md`.** No existe.

## Frontmatter obligatorio

Toda página creada o actualizada en el wiki empieza, como mínimo, con:

```yaml
---
tipo_nodo: hub | faceta | evento | insight | concepto | fuente | etapa   # uno solo — SCHEMA §3
domain: technical | personal   # uno solo. meta: solo los archivos del propio sistema (overview, backlog)
creation_date: YYYY-MM-DD
última_actualización: YYYY-MM-DD   # la fecha de hoy cada vez que el nodo cambia
---
```

Cada campo lleva **un único valor**, nunca una lista. Los nodos con padre añaden `padre: "[[...]]"` — **siempre entre comillas** — y `origen_enlace: explícito | inferido` (SCHEMA §13). El resto de campos, por tipo de nodo, en `SCHEMA.md` y en `_plantillas/`.

## Operaciones

`ingest` · `query` · `lint`. Los flujos completos, el pre-flight obligatorio antes de cualquier operación y el formato de entrada del log están en `SCHEMA.md` §7 y §15.

Antes de cerrar una sesión que haya escrito en el wiki, ejecuta la comprobación determinista y corrige lo que marque en rojo:

```bash
python3 _herramientas/lint_estructura.py
```

Si el usuario activó el hook `pre-commit` (`git config core.hooksPath _herramientas/hooks`), la repite en cada commit y lo bloquea si hay algún 🔴, si se toca un nodo `inmutable: true` o si un nodo cambia sin `última_actualización` de hoy. Si te bloquea, arregla el nodo: no uses `--no-verify` para saltarlo. Detalle en SCHEMA §12.

## Primera sesión

Si `02_Wiki/log.md` no tiene ninguna entrada, el vault está recién creado:

1. Pregunta al usuario en qué idioma quiere los nodos y si quiere ajustar los vocabularios cerrados (SCHEMA §14) antes del primer ingest. Es más barato ahora que con cien nodos escritos.
2. Si no lo ha visto, señálale `_ejemplo/ingest-de-ejemplo.md`: muestra un ingest completo de principio a fin.
3. Registra la creación en el log: `## [fecha] schema | vault creado desde la plantilla`.

## Privacidad

Este vault acaba guardando lo más personal del usuario. Si te pide hacer `push`, sincronizarlo o publicarlo, comprueba antes que el destino es privado y avísale si no lo es.
