---
tipo_nodo: meta
domain: meta
creation_date: 2026-10-29
última_actualización: 2026-11-22
naturaleza: backlog_arquitectónico_vivo
---

# Aeternea — Desafíos Pendientes

Backlog arquitectónico vivo. Problemas conocidos sin solución implementada, riesgos a vigilar y decisiones aplazadas conscientemente. Léelo **antes de cada decisión arquitectónica grande** para no reabrir trade-offs ya resueltos.

---

## ⚠️ Riesgo central: eficiencia vs. esencia

La optimización de tokens, la atomización severa y los techos cuantitativos sirven a la escalabilidad. Riesgo continuo: que el sistema se vuelva tan eficiente que pierda la voz del autor.

**Salvaguardas activas:**
- Citas verbatim obligatorias en nodos personales
- Subtipo `literaria` con `inmutable: true`, exento de fragmentación y techos
- Clasificación fail-safe: ante la duda, preservar intacto
- `_archivo_versiones_pasadas/` como cementerio honorario (coste 0)

**Señales de alerta — si pasa cualquiera, PARAMOS y rediseñamos:**
- Cuando releyendo nodos personales no reconozcas tu voz
- Cuando los nodos parezcan documentación técnica en vez de memoria viva
- Cuando dudes en abrir Aeternea porque "todo está demasiado ordenado"

---

## Desafíos diferidos con plan

### Embeddings vectoriales (discovery semántico)
- **Qué resolverían:** búsqueda por significado ("esa persona que me hizo sentir así"), no por palabras clave.
- **Por qué se difieren:** con los dos índices, aliases exhaustivos y el descubrimiento en tres capas (SCHEMA §7), el grep basta: L1 y L2 no crecen con el tamaño del vault, y L0 solo con el número de hubs.
- **Cuándo retomar:** cuando una búsqueda real falle por no compartir palabras con el nodo que buscabas. El tamaño solo no basta: el vault del que sale esta plantilla pasó de 200 nodos sin que fallara ninguna.
- **Forma preferida:** un buscador local híbrido (BM25 + vectores) con CLI o MCP, para que el agente lo llame sin sacar los datos de la máquina.

### Fragmentación sin demonio
- **Limitación:** sin proceso de fondo, el chequeo de umbrales solo ocurre en el ingest del LLM o en el Lint, no en tiempo real (SCHEMA §9).
- **Mitigación actual:** `_herramientas/lint_estructura.py` al cerrar cada sesión.

---

## Decisiones conscientes (NO son problemas)

- BAUL_TEMPORAL: gestión 100 % manual del usuario, sin automatización.
- Coleccionar pasado: NO. El archivo histórico vale solo si tiene coste 0 Y valor para el yo futuro. Cuando un desafío se resuelve, se borra o se reduce a una línea aquí.
- `frecuencia` de contacto: no se almacena, se deduce de los timestamps de los eventos.
- `ambito`/`aporte` de personas: texto libre, no enumeración (orígenes múltiples).

---

## Cómo usar este documento

Cuando emerja un problema sin solución inmediata, se añade aquí. Cuando se resuelve, se elimina o pasa a "Decisiones conscientes". **Aquí el pasado no se acumula** — el tamaño de esta nota es un termómetro de deuda arquitectónica, no un patrimonio a conservar.
