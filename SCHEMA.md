# Schema — Aeternea Wiki (v3)

Referencia canónica para el agente LLM que mantiene esta wiki.
CLAUDE.md describe el patrón general; este archivo describe *esta* implementación.
Si hay conflicto, **manda este archivo**.

> **Naturaleza del sistema:** Aeternea es la memoria externa del usuario, no la memoria del LLM. El LLM no recuerda nada entre sesiones — "recuerda" exactamente lo que lee del grafo. Por eso el discovery (saber qué existe) es tan importante como el almacenamiento.

---

## 1. Estructura de directorios

```
Aeternea/
├── 01_Buffer_de_entrada/              ← fuentes en crudo
│   └── _procesados/                   ← fuentes ya ingestadas (movidas, no borradas)
├── 02_Wiki/
│   ├── index_tecnico.md               ← catálogo técnico
│   ├── index_personal.md              ← catálogo personal
│   ├── overview.md                    ← dashboard raíz (Dataview: FOCUS + PENDIENTE)
│   ├── log.md                         ← historial de operaciones
│   ├── aeternea-desafios-pendientes.md ← backlog arquitectónico vivo
│   ├── fuentes/                       ← fuentes técnicas procesadas
│   ├── conceptos/                     ← conceptos técnicos transversales
│   ├── entidades/                     ← hubs técnicos (proyectos) + hijos
│   ├── personal/
│   │   ├── identidad/                 ← hub + 17 casillas fijas (§8)
│   │   ├── entidades_sociales/        ← hubs de persona + sus hijos
│   │   ├── laboratorio/               ← hub + análisis de dinámicas sociales
│   │   ├── literatura/                ← contenido emocional/artístico INTACTO
│   │   ├── trayectoria/               ← evolución profesional (régimen acumulativo, por etapas)
│   │   ├── baul_temporal/             ← fallback (gestión manual del usuario)
│   │   ├── _historial_identidad/      ← versiones superadas por casilla (frío, solo bajo demanda)
│   │   ├── _historial_trayectoria/    ← detalle de etapas cerradas (frío, solo bajo demanda)
│   │   └── _trazabilidad/             ← historial de mutaciones (dormido)
│   ├── _assets/                       ← imágenes y capturas
│   ├── _log_archivo/                  ← particiones frías del log (§15)
│   └── _archivo_versiones_pasadas/    ← versiones antiguas (nostalgia, coste 0)
├── _plantillas/                       ← andamios de nodo (plugin Plantillas de Obsidian)
├── _herramientas/                     ← lint estructural, sus tests y el hook pre-commit (§12)
├── _ejemplo/                          ← un ingest resuelto de muestra; bórralo cuando lo hayas visto
├── _privado/                          ← (opcional) material íntimo aún sin leer: en .gitignore, no se sube
├── AGENTS.md                          ← puntero a CLAUDE.md para otros agentes
├── CLAUDE.md                          ← reglas de operación
└── SCHEMA.md                          ← este archivo
```

**Carpetas con prefijo `_`:** invisibles al sistema vivo (también `_plantillas/`, `_herramientas/`, `_ejemplo/` y `_privado/` en la raíz). El Lint las ignora, el pre-flight no las carga, no se enlazan desde índices. Solo accesibles a mano.

**Regla fundamental:** las fuentes en `01_Buffer_de_entrada/` no se modifican. Tras un ingest exitoso se **mueven** a `_procesados/` con prefijo de fecha (`YYYY-MM-DD - nombre.md`).

---

## 2. Los dos dominios y la fuente mixta

| Dominio | Índice | Contenido |
|---------|--------|-----------|
| `technical` | `index_tecnico.md` | Software, código, IA, sistemas, proyectos técnicos |
| `personal` | `index_personal.md` | Memoria episódica, relaciones, filosofía, identidad, literatura |

**Desempate:** materia prevalece sobre tono. Proyecto técnico con carga emocional → técnico.

**Fuente mixta:** una sola fuente que contiene material de ambos dominios se **bifurca**: los nodos técnicos van a su rama, los personales a la suya, y se conectan con **un hilo fino** — un único wikilink cruzado explícito (`relacionado_con: [[...]]`), no cross-linking masivo. Es la única excepción autorizada a la separación de dominios.

---

## 3. Arquetipos universales (técnico + personal)

La **estructura** es universal; el **frontmatter** se bifurca por dominio.

| Arquetipo | Rol | Personal | Técnico |
|-----------|-----|----------|---------|
| `hub` | Nodo índice de una entidad | persona, identidad | proyecto, curso |
| `faceta` | Subtema atemporal | rasgo, patrón | subsistema, módulo |
| `evento` | Snapshot datado inmutable | episodio | sesión, hito |
| `insight` | Análisis transversal | reflexión | decisión arquitectónica |
| `concepto` | Idea standalone no ligada a entidad | — | concepto técnico |
| `fuente` | Documento procesado tal cual | literaria, episódica | externa, legacy |
| `etapa` | **Agrupador temporal dentro de un hub acumulativo** | periodo vital | fase de proyecto |

**`etapa`.** Capa intermedia para hubs de **régimen acumulativo** — donde nada reemplaza a nada y los hijos crecen sin techo (trayectoria, y a futuro cualquier entidad con años de eventos). Sin ella, L1 sobre el hub devuelve cientos de hitos. Con ella devuelve **etapas**, que crecen una o dos por año.

- **No entra en L0** aunque agrupe: es navegación interna, no punto de entrada. L0 solo lleva el hub raíz.
- Ciclo: `activa` (eventos vivos, ventana §6) → `cerrada` (síntesis + hitos que importaron; el detalle baja a `_historial_<rama>/`).
- Las etapas **las revela el material**, no se definen a priori.

### Árbol por punteros-padre (NO por nombres concatenados)

Cada nodo guarda su **nombre atómico corto** + un puntero `padre`. El camino completo (breadcrumb) se **calcula** caminando los padres, nunca se almacena en el nombre de archivo.

```yaml
padre: "[[sensor-tiempo-aplicaciones]]"   # entre comillas: sin ellas Obsidian no lo lee como enlace
nivel: 5
```

- Profundidad arbitraria sin explosión de nombres
- Renombrar un nivel intermedio no rompe los hijos (apuntan por wikilink)
- **Carga perezosa de ancestros:** al entrar a un nodo profundo, cargar el nodo focal completo + solo los *títulos* de ancestros (breadcrumb), **nunca** los hermanos ni el contenido de la rama entera
- **El índice técnico no duplica el árbol:** `index_tecnico.md` lista SOLO la tabla de hubs (activos y archivados, una línea cada uno) — nunca el desglose interno de facetas/eventos/insights de cada proyecto. Ese desglose ya vive en los punteros `padre` de cada nodo y se reconstruye al vuelo — glob de `entidades/<hub>*` + lectura puntual de `padre`, el mismo mecanismo que el roster de personas (§4). Motivo: el árbol escrito a mano crece con el detalle acumulado de cada proyecto (sin techo), mientras que la tabla de hubs crece solo con el número de proyectos (lento, barato). Para el LLM el índice es capa humana: navega con L0/L1 (§7), no leyéndolo.

### Nomenclatura híbrida (anti-colisión)

Nombre de archivo = slug atómico con prefijo mínimo del padre inmediato cuando haya riesgo de colisión:
`aws-networking.md`, `azure-networking.md` (no dos `networking.md`).
El breadcrumb completo lo calcula Dataview.

---

## 4. Modelo de persona (dominio personal)

Una persona = **nodo-hub** ligero con dimensiones actuales + hijos por puntero-padre + trazabilidad dormida.

### Frontmatter del hub de persona

```yaml
---
tipo_nodo: hub
arquetipo_taxonomico: entidad_social
domain: personal
# ── EJES CERRADOS (rígidos — generan las vistas Dataview) ──
cercania: nucleo | cercana | orbita | distante
rol_dinamica: mentor | aliado | espejo | antagonista | dependiente | neutro
intensidad: baja | media | alta | Overclocking
# ── CAMPOS LIBRES (descriptivos) ──
ambito: "texto libre — orígenes/contextos múltiples"
aporte: "texto libre — qué aporta a tu vida"
aliases: [exhaustivos, para discovery — imperativo]
creation_date: YYYY-MM-DD
última_actualización: YYYY-MM-DD
---
```

- **`frecuencia` NO se almacena** — se deduce de los timestamps de los nodos-evento.
- `Overclocking` es el único valor capitalizado del sistema. Categoría cualitativamente distinta — el LLM no la asigna a la ligera.

### Qué mide `cercania`

`cercania` mide **vínculo operativo real**: cuánto pesa esa persona en la vida y las decisiones del usuario. **No mide convivencia ni frecuencia de contacto.**

Consecuencia directa: alguien con quien se convive a diario puede ser `orbita` o `distante` si no tiene peso operativo, y alguien a quien se ve poco puede ser `nucleo`. Ante el conflicto entre presencia física y peso real, **manda el peso real**.

### REGLA INVIOLABLE — Vocabulario cerrado (anti-alucinación)

Los tres ejes cerrados (`cercania`, `rol_dinamica`, `intensidad`) son **enumeraciones fijas**. El LLM SOLO puede asignar valores de la lista. **Prohibido inventar, derivar, traducir o aproximar.**

Si la realidad no encaja en ningún valor:
1. El LLM se DETIENE — no asigna nada provisional
2. Pregunta al usuario si ampliar el vocabulario o usar el más cercano
3. Ampliar el vocabulario es decisión del usuario y se registra aquí en SCHEMA
4. Validación post-asignación: si algún valor ∉ enum → rechazar y reasignar

Los campos libres (`ambito`, `aporte`) están **exentos** de esta regla.

### Trazabilidad desacoplada

El hub guarda SOLO valores actuales (ligero). El historial de mutaciones vive en `personal/_trazabilidad/<persona>.md`:

- NO enlazado, el Lint lo ignora, el pre-flight no lo carga
- El LLM NO lo lee jamás, **salvo petición expresa** ("¿por qué cambió mi relación con X?")
- Append-only:

```markdown
| Fecha | Eje | Antes → Después | Motivo |
|-------|-----|-----------------|--------|
| 2026-05-14 | rol_dinamica | aliado → espejo | discusión que me hizo verme reflejado |
```

Al cambiar una dimensión, el LLM hace dos cosas atómicas: actualiza el valor en el hub + añade línea a la trazabilidad con el motivo (lo pregunta en una línea si no se lo das).

### Vistas sociales = Dataview, no archivos

No existen sub-MOCs estáticos. Las agrupaciones (núcleo, antagonistas...) son consultas Dataview que filtran por los ejes cerrados. Cambias un valor → todas las vistas se actualizan solas. Cero mantenimiento estructural.

> **Capa máquina vs. capa humana:** Dataview renderiza para los ojos del usuario en Obsidian. El LLM NO ejecuta Dataview ni lee los índices en el pre-flight. Para enumerar personas/proyectos usa el descubrimiento en tres capas del **§7** (L0 mapa → L1 vecindario → L2 nodo), con filtrado en shell y lectura puntual de frontmatter sólo cuando necesita filtrar por dimensión.

---

## 5. Taxonomía personal (arquetipo_taxonomico)

Tag de naturaleza, ortogonal al tipo_nodo:

- `identidad` — psicología base → **estructura fija de 17 casillas** bajo el hub [[identidad]], versionada (§8)
- `entidad_social` — personas → modelo dimensional (§4)
- `laboratorio` — análisis de dinámicas sociales
- `trayectoria` — evolución profesional personal. Régimen acumulativo, navegado por etapas (§3)
- `baul_temporal` — fallback inclasificable (gestión manual del usuario, sin automatización)

**Taxonomías propias.** Se añaden cuando un dominio sostenido desborda a los demás, siempre con aprobación del usuario: se crea `personal/<taxonomía>/` con su hub y se registra aquí con fecha. Ejemplo típico: `gaming` — videojuegos como dominio de práctica sostenido; no es un proyecto (no va a `entidades/`, que es técnica) y su volumen desbordaría cualquier evento suelto. Régimen acumulativo: hub + eventos por periodo, con rollover §6.

Antes de añadir una, comprueba que no solapa con una casilla de identidad: una taxonomía `filosofia`, por ejemplo, duplicaría `id-valores-proposito` en cada ingest.

`literatura` es subtipo de `fuente` (§7), no taxonomía.

---

## 6. Techos y contrato de nodo-evento

### Techos (palabras)

| Nodo | Aviso | Techo duro |
|------|-------|-----------|
| Hub (persona/proyecto) | 250 | 400 |
| Faceta personal | 1500 | 2500 |
| Evento personal | 2000 | 2500 |
| Insight personal | 1200 | 2000 |
| Faceta técnica | 1000 | 1800 |
| Sub-faceta técnica | 600 | 1200 |
| Evento técnico (sesión) | 1500 | 2500 |
| Insight técnico (decisión) | 800 | 1500 |
| Fuente (legacy/externa) | 2000 | 3000 |

**Qué se cuenta:** las palabras del **cuerpo**. El frontmatter y los comentarios HTML no cuentan. La vara es la del lint (§12): `wc -w` cuenta también el frontmatter y da de más (un hub de 337 palabras de cuerpo mide 411 con `wc -w`).

Ventana activa del hub: **10 eventos**. Por encima → rollover por densidad (no por calendario): el bloque más antiguo se mueve **intacto** a una carpeta fría `_historial_<rama>/`, hermana de la rama (`personal/_historial_<rama>/`, `entidades/_historial_<hub>/`), y el hub lo sustituye por una línea con el rango real y los enlaces. Los eventos movidos conservan su `padre`: L1 los sigue listando, pero la ruta `_` los marca como fríos y no se abren salvo que la pregunta sea de ese periodo. El lint no los cuenta (ignora las carpetas `_`) y los enlaces que les llegan siguen resolviendo. Fundirlos en un solo nodo rompería esos enlaces y su contrato de evento.

> **Aplicación obligatoria.** Con importaciones masivas (p. ej., años de conversaciones exportadas), cualquier hub puede acumular decenas de eventos y **L1 sobre él se vuelve carísimo** — el coste no está en L0 sino en el vecindario. Vigilar especialmente `entidades_sociales/` y `entidades/`.
>
> Para hubs de **régimen acumulativo con muchos años** (trayectoria), el rollover no basta: se antepone la capa `etapa` (§3), y el archivo frío vive en `personal/_historial_<rama>/`.

**Excepción absoluta:** los nodos `literatura` con `inmutable: true` están EXENTOS de todos los techos.

### Contrato de nodo-evento (validado tras crear)

```markdown
## Contexto        ← SIEMPRE primero, ≤300 palabras
## Detalle         ← cuerpo denso
## Citas verbatim  ← SIEMPRE presente, ≥2 citas
## Reflexión post  ← SIEMPRE último, separable
```

Validación automática: si faltan cabeceras, si Contexto >300 palabras, o si hay <2 citas → reescribir. Esto hace la **lectura selectiva** determinista (el LLM puede cargar solo Contexto+Reflexión sin adivinar).

**Precisiones** (las comprueba el lint, §12):

- Las cuatro cabeceras son de nivel `##` y se llaman **exactamente** así. `## Contexto: el día que…` o `### Detalle` no valen: un subtítulo va en la línea siguiente.
- Van en ese orden. Puede haber otras secciones `##` entre medias (p. ej. `## Conexiones`), pero nada antes de `Contexto` ni después de `Reflexión post`.
- Cada cita es una línea que empieza por `> `. Las viñetas (`- "…"`) no cuentan.
- **Exención declarada.** Un evento que no puede cumplir sin inventar —una sesión técnica antigua sin citas literales en su fuente— lleva `contrato_exento: "motivo"` en el frontmatter. El lint lo da como 🟡 en cada pasada, con lo que le falta: la deuda queda a la vista, no escondida. No es una vía para nodos nuevos.

---

## 7. Flujos de Ingest

### PRINCIPIO DE DESCUBRIMIENTO

> **El coste lo marca lo que el LLM *trae* a su contexto, no lo que *hay* en el vault.**

Toda consulta al vault se filtra **en el shell**; sólo cruza a la ventana del LLM el resultado. Un `grep` sobre 900 nodos abre 900 archivos, pero si devuelve 20 líneas, cuesta 20 líneas. El trabajo pesado ocurre fuera del contexto.

Corolario, **regla de arquitectura**: el LLM **nunca** sabe qué *contiene* un nodo hasta que lo abre con motivo. Existencia ≠ contenido. Está prohibido cargar un archivo para averiguar qué hay dentro de otros — para eso está el filtrado en shell.

Por eso el LLM **no lee los índices en el pre-flight**: son **capa humana** (Obsidian), llenos de sintaxis Dataview que el LLM no puede ejecutar, y leerlos obligaría después a abrir el frontmatter de todo el vault para obtener los nombres reales. Se pagaría dos veces y la primera no serviría.

### Pre-flight en tres capas (antes de CUALQUIER operación)

**L0 — el mapa. Incondicional, una vez por sesión. Solo nombres de archivo: barato.**
Lista de nodos de rango hub: qué entidades y qué piezas estructurales de la personalidad existen. Nombres, no contenido.

```bash
cd 02_Wiki
{ grep -rl '^tipo_nodo: hub' --include='*.md' . | grep -v '/_' | grep -v 'overview.md'
  grep -rlE '^padre: "?\[\[identidad\]\]' --include='*.md' personal/identidad   # las 17 casillas fijas
} | sed 's|^\./||' | sort -u
```

> **Por qué las 17 casillas de identidad entran enteras en L0:** son **estructura fija que no crece nunca** — la información nueva actualiza una casilla, no crea otra. Su coste es constante por muchos ingests que se hagan, y la personalidad del usuario es la razón principal de existir de Aeternea: pesa más que la rama técnica. Los nodos que cuelgan *de* una casilla (manifestaciones datadas) **no** entran en L0 y se alcanzan por L1.

**L1 — el vecindario. Sólo del tema que se toca.**
Los hijos de un hub concreto, por puntero `padre`:

```bash
grep -rlE '^padre: "?\[\[<hub>(\]\]|\|)' --include='*.md' 02_Wiki
```

El patrón cierra el nombre (`]]` o `|`): sin eso, `[[identidad` también casa con `[[identidad-otra-cosa]]`.

Se paga un barrio, nunca la ciudad. El coste queda atado al número de hijos de esa entidad, no al tamaño del vault.

**L2 — el nodo.** Se abre entero, y sólo el que se va a usar o comprobar.

**Propiedad clave:** el coste del descubrimiento **no crece con el tamaño del vault**. Con 900 nodos, un ingest sobre una entidad sigue costando lo mismo que con 90, porque esa entidad sigue teniendo un puñado de hijos.

### REGLA DURA — Anti-solapamiento acotado

> **Antes de crear un nodo, revisar los nodos del tema correspondiente — nunca la base entera.**

El ámbito de revisión lo define L1: los hijos de su hub si cuelga de uno, o su carpeta si es de rango hub. Crear un nodo sobre una persona cuesta mirar sus pocos hijos, no 900 nodos. Es el procedimiento ejecutable del §12 (anti-duplicación de conceptos), que hasta ahora era una intención sin método.

Sin esta regla, el pre-flight barato degeneraría en ingestar a ciegas y duplicar. Con ella, la baratura no cuesta fidelidad.

### Ingest agresivo (por defecto)
Prohibido crear un nodo > 70% de su techo. Si una fuente lo justifica, dividir EN el ingest, no después. Atomización desde el origen.

### Ingest técnico
1. Leer fuente → 2. Atomizar en hub + facetas/eventos/insights con punteros-padre → 3. Enlazar en `index_tecnico.md` → 4. Actualizar `overview.md` si hay nuevo proyecto → 5. Log → 6. Mover fuente a `_procesados/`

### Ingest personal
1. Leer → 2. **Clasificación fail-safe (ver abajo)** → 3. Si episódico: atomizar en taxonomía + dimensiones → 4. Si literario: nodo único intacto → 5. Enlazar en `index_personal.md` → 6. Log → 7. Mover a `_procesados/`

### REGLA DE ORO — Salvaguarda fail-safe de contenido emocional
El modo de fallo debe ser "conservé de más", **nunca** "destruí una carta".

```
PASO 1 — Escaneo de marcadores: ¿1ª persona íntima? ¿apelación a un "tú"?
  ¿verso/métrica? ¿carga afectiva? ¿despedida/firma? ¿tono confesional?
PASO 2 — Decisión con sesgo a preservar:
  CUALQUIER marcador presente → subtipo: literaria → inmutable: true,
       fragmentación: prohibida, ingest íntegro, sin resumir, sin trocear
  CERO marcadores Y estructura claramente técnica/episódica → atomizar
  DUDA / señal débil → POR DEFECTO literaria. Conservar intacto.
PASO 3 — NUNCA preguntar como prerrequisito.
  Primero salvaguardar, DESPUÉS informar:
  "Lo guardé intacto en personal/literatura/. Si querías trocearlo, dímelo."
```

Una carta de 4000-5000 palabras con marcadores entra como UN nodo, exento de techos. La biblioteca de Alejandría no arde ni en los peores días del usuario.

### Ingest mixto
Bifurcar (§2): nodos técnicos a su rama, personales a la suya, unidos por un hilo fino.

### Flujo de Query

1. **Pre-flight L0**, como en cualquier operación → 2. **L1** del hub o de la casilla que toque la pregunta → 3. **L2**: abrir solo los nodos que van a sostener la respuesta → 4. **Responder citando los nodos** (`[[nodo]]`) y, si pesa, la cita verbatim con su fecha.

- Lo que el grafo no dice se declara `sin_datos`. No se rellena con lo plausible (§8).
- Cada nodo se lee como **cierto a fecha de su `última_actualización`**. Si la pregunta es sobre el presente y el nodo es viejo, se dice.
- **Una consulta que solo lee no escribe nada:** ni nodo, ni log, ni commit.
- **Si la respuesta merece quedarse** —una comparación, una síntesis que no existía—, se archiva como nodo `insight` por el flujo de ingest, anti-solapamiento incluido, y entonces deja entrada en el log con tipo `query` (§15).

### Ficha de proyecto — escritura en continuo

**Problema.** Los flujos de arriba son **por lotes**: un proyecto entra al grafo cuando se ingesta una fuente o al cerrarse. Uno que nace y vive fuera del vault (un repo, una carpeta de trabajo con su agente) no entra mientras vive. Segundo fallo: un hub que copia campos rápidos —la fase, el siguiente paso— se desfasa en semanas, porque nadie lo actualiza cuando cambian. En el vault del que sale esta plantilla pasaron las dos cosas: un proyecto vivió un mes sin hub y otro guardó en el suyo una fase que ya no era cierta.

**Por qué todos los proyectos vivos y no solo los grandes.** L0 es el único mapa del canon que tiene un agente en frío, y lista hubs. **Un proyecto sin hub no existe para quien lee el vault**: no aparece al razonar sobre la trayectoria o el patrón de inicio y cierre. Una ficha cuesta un nombre en L0 y se toca pocas veces al año.

**Principio: cada dato vive en un sitio y los demás apuntan.** Una copia solo se justifica si su lector no puede dar el salto. Una copia fuera del vault, además, no la vigila el lint ni sale en el diff del commit.

| Capa | Guarda | Se escribe |
|---|---|---|
| Documento de entrada del proyecto (fuera del vault) o, si no lo tiene, sus eventos aquí | detalle, fase, decisiones, siguiente paso | cada sesión |
| Ficha (hub con `ficha_viva: true`) | **qué es · por qué importa · estado · dónde vive**; el estado, en el frontmatter (`estado`, `prioridad`) | solo en eventos de ciclo de vida |
| Fila de `index_tecnico` | copia del estado para la capa humana | en el mismo commit que la ficha |

Las notas que el agente guarde fuera del vault (su memoria, el README del proyecto) **apuntan** a la ficha: no copian su estado.

1. **Quién tiene ficha:** todo proyecto vivo, desde que tiene nombre. Regla mecánica: no depende de juzgar si un proyecto «merece» entrar.
2. **Eventos de ciclo de vida:** nace · cambia de estado (`activo | pausado | completado | archivado`) · cambia de sitio · cambia su porqué. Un proyecto que solo es una idea a la espera de que el usuario lo arranque es `pausado`. Nada más dispara.
3. **Disparador: una regla en las instrucciones permanentes del agente** (p. ej., el `CLAUDE.md` de usuario, que se carga en todas las sesiones): cuando un proyecto nace o cambia, la ficha se toca en el mismo paso. Sin revisiones por calendario: se saltan, y una regla pegada a la acción no. El documento de entrada del proyecto puede apuntar a la ficha como segundo aviso.
4. **Escritura atómica:** ficha y fila del índice, en el mismo commit. Si no cambia ninguno de los cuatro campos, la ficha no se toca.
5. **Supervisión:** el agente escribe solo esos cuatro campos y el usuario ve el diff. Decisiones, eventos e insights del proyecto **no** suben solos: a petición, o con el ingest al cerrar.
6. **«Por qué importa» lo dicta el usuario**, con cita y fecha. Si no consta, `sin_datos`: el agente no lo infiere.
7. **`última_actividad`** = fecha del último cambio en el proyecto (su carpeta o su último evento), refrescada cada vez que se toca la ficha. Así el aviso de 90 días del lint (§12) hace la pregunta útil: *¿sigue vivo?*
8. **Reconciliación**, en cada mantenimiento o cuando el usuario la pida: `grep -rl '^ficha_viva: true' 02_Wiki` y comparar cada ficha con su fila del índice y con su proyecto. Lo que difiera se corrige con el usuario delante.

---

## 8. Versionado de identidad

La forma de ver el mundo cambia, a veces cada semana. **Nada se borra jamás.**

### Arquitectura

`personal/identidad/` es una **estructura fija de 17 casillas** bajo el hub [[identidad]] (§5). La información nueva **actualiza** una casilla; **nunca crea otra**. Consecuencia deliberada: el coste del pre-flight L0 es constante por muchos ingests que se hagan.

Cada casilla tiene su propio histórico en `personal/_historial_identidad/<casilla>.md` — mismo patrón que `_trazabilidad/` (§4) y que las particiones frías del log (§15): carpeta `_`, invisible al Lint y al pre-flight, **append-only**. El LLM **no lo lee jamás salvo petición expresa** ("¿cómo he cambiado?"). Entonces sí, se lee byte a byte, bajo demanda.

### Al actualizar una casilla

1. El fragmento que deja de ser cierto se **añade** al histórico de esa casilla, con `válido_desde`/`válido_hasta`, qué lo reemplaza y **qué evidencia lo disparó**.
2. La casilla se reescribe con lo nuevo, citando su evidencia.
3. **Si la casilla tenía hijos, se reasignan a la versión nueva.** *(Fallo real: al sustituir una casilla, sus facetas quedaron colgando de un padre muerto.)*
4. La síntesis no se regenera en cada cambio: sigue la regla de **síntesis por etapa**, abajo.

### Síntesis por etapa

[[id-sintesis]] no es un resumen único que se regenera: es **un router de síntesis, una por etapa de [[trayectoria]]** (nombre: `sintesis-etapa-<etapa>-<AAAA>-<AAAA>`).

- **Una por etapa, no por tamaño ni por sesión.** Las de etapas cerradas son `estado: cerrada`: no se editan; si entra evidencia nueva sobre ese periodo, se rehacen enteras y la anterior baja a `_historial_identidad/`. Solo la de la etapa actual está viva.
- **Una ranura por casilla** (~110 palabras), cada una con su rango *"evidencia: desde → hasta"*.
- **Se filtra por el periodo al que se refiere la evidencia, no por cuándo se dijo** (*"dejé el piano en marzo de 2023"* se dijo en 2026 y es de 2023).
- **Lo que no tiene periodo va al bloque "Sin fechar" de [[id-sintesis]]**, nunca a una etapa por aproximación.
- **Cada síntesis declara sus huecos** en cabecera (tramos sin corpus, fronteras con la etapa vecina).
- Son **derivadas**: no tocan las casillas. Cuelgan de [[id-sintesis]] por `padre` y quedan fuera de L0.

### REGLAS INVIOLABLES de escritura en identidad

- **Registrar, no evaluar.** Si el texto dice que se pone triste, se escribe *"se pone triste"* + cita. **Prohibido puntuar, escalar o agregar** en juicios tipo "tolerancia media-baja". La suma la hace el usuario, no el LLM.
- **Sin evidencia no se escribe.** Fecha + verbatim por afirmación. Un hueco se queda `sin_datos`; jamás se rellena con lo plausible.
- **Casillas sensibles** (`id-demograficos`, `id-historia-socio-familiar`, `id-biologico-salud`): solo afirmación directa del usuario o cita literal. **Prohibida la inferencia.**
- **Jerarquía de evidencia.** Afirmación explícita del usuario en el presente **>** patrón repetido en el corpus **>** afirmación aislada en el corpus.
  > ⚠️ Si el corpus incluye conversaciones con IAs, puede contener afirmaciones hechas **para probar modelos** (hipótesis, roles, datos inventados). Nunca mandan sobre lo que el usuario afirma directamente; ante la duda, se pregunta.
- **Sin marco clínico.** La estructura ordena, no diagnostica. No se usa nomenclatura diagnóstica ni se etiquetan vulnerabilidades.

Permite preguntar "¿cómo ha cambiado mi forma de pensar sobre X?" con respuesta temporal trazable, sin pagar un token por ello mientras no se pregunte.

---

## 9. Fragmentación automática

**Trigger:** tras cualquier escritura del LLM, contar palabras del nodo tocado. Si > aviso → proponer plan. Si > techo → fragmentar (con confirmación).

**Limitación honesta (sin demonio):** el LLM solo actúa cuando se le invoca. Si el usuario edita a mano en Obsidian, nadie vigila en ese instante. El chequeo ocurre en (a) ingest/edición del LLM y (b) cada pasada de Lint. El Lint es la red de seguridad.

### REGLA CRÍTICA — Transparencia de fragmentación
La fragmentación es la unidad base de toda la arquitectura. NUNCA silenciosa, NUNCA asumir el "sí". Toda fragmentación explica: (1) por qué, (2) qué va a cada nodo, (3) qué se conserva, (4) pide confirmación. Tono cálido, formato visual, entendible en 10 segundos aunque el usuario esté cansado:

```
─────────────────────────────────────
La nota [[X]] ha crecido a N palabras.
Sé que piensas mejor cuando cada cosa está en su sitio.
Te propongo separarla — sin perder nada, sin cambiar su clasificación:

  1️⃣  [[x-tema-a]]  — [qué recoge]
  2️⃣  [[x-evento-b]] — [qué recoge], intacto
  3️⃣  [[x]] — queda como índice limpio + datos base

  ✅ Sí   ✏️ Cambiar algo   ⏸ Ahora no
Si dudas, pospón. No hay prisa.
─────────────────────────────────────
```

---

## 10. Imágenes (protocolo de descripción persistida)

Un LLM no lee markdown con imágenes embebidas en una pasada, y re-ver una imagen en cada query es ruinoso.

```
- Carpeta fija: 02_Wiki/_assets/
- Referencia: ![[captura.png]]
- En el ingest, el LLM VE la imagen UNA vez y escribe junto al embed:

  ![[captura.png]]
  > **[Descripción persistida]** [qué muestra, datos clave legibles]

- En queries futuras el LLM lee la descripción (~50 tokens), NO re-ve la imagen
- Solo re-ve si el usuario lo pide
```

Imágenes en nodos `literatura`/`inmutable`: se preservan, descripción opcional y discreta, nunca se tocan.

---

## 11. Overview = dashboard de atención

`overview.md` NO es prosa. Es un dashboard Dataview con **dos secciones fijas y nada más**:

- **🎯 FOCUS** — `estado: activo` + `prioridad: alta`, **máximo 7**. Si hay un octavo, el sistema obliga a degradar otro. Protege contra la dispersión.
- **📋 PENDIENTE** — `estado: activo` + prioridad media/baja.

Todo lo demás (completado, pausado, archivado) **no se renderiza**. Existe y es consultable, pero no contamina la vista. Mantenimiento manual: cero (Dataview lo genera; el Lint solo valida el frontmatter).

Estados de proyecto: `activo | completado | pausado | archivado`. Prioridad: `alta | media | baja`.

---

## 12. Lint unificado

Un solo barrido, un solo informe amable, agrupado por severidad (🔴 necesita decisión / 🟡 puedo arreglarlo con tu sí / 🟢 hecho). Verifica:
- Aliases (cada hub de persona ≥3 aliases o `alias_único: true`)
- Techos cruzados
- Enlaces rotos (renombrados)
- Conceptos casi-duplicados (>70% similitud → fusionar, ver §sig.)
- Frontmatter incompleto o valores fuera de vocabulario cerrado
- Punteros `padre` rotos
- Estados: proyectos `activo` sin actividad en 90 días → sugerir `pausado`
- Coherencia de dimensiones

Ignora siempre carpetas `_`.

### Qué comprueba el script y qué queda al juicio del agente

`python3 _herramientas/lint_estructura.py` hace la parte determinista: frontmatter y tipo de cada valor, vocabulario cerrado, punteros `padre`, `origen_enlace` en los nodos posteriores a su regla (§13), enlaces rotos (wikilinks y markdown), techos, contrato de evento, hubs `activo` sin actividad en 90 días, ventana de 10 eventos, y tipos y techo del log. Sale con código 1 si hay algún 🔴 y con 2 si no pudo ejecutarse. Un nodo ilegible no tumba el informe: sale como 🔴.

Tiene tests en `_herramientas/tests/`. Quien cambie el script los pasa antes: `python3 -m unittest discover -s _herramientas/tests`.

Quedan al juicio del agente, porque un script no puede comprobarlos: conceptos casi duplicados, coherencia de dimensiones, afirmaciones caducadas y contradicciones entre nodos.

**Hook pre-commit** (`_herramientas/hooks/pre-commit`; se activa una vez por clon con `git config core.hooksPath _herramientas/hooks`). Repite el lint en cada commit y lo bloquea si hay un 🔴. Añade dos reglas que solo tienen sentido al commitear:

- un nodo `inmutable: true` no se modifica ni se borra. Se levanta con `AETERNEA_PERMITIR_INMUTABLE=1`, solo si lo pide el usuario;
- un nodo que cambia lleva `última_actualización` de hoy. Se levanta con `AETERNEA_MIGRACION=1` en migraciones mecánicas, que no cambian contenido.

Por qué existe: sin nada que lo haga cumplir, un schema se degrada en silencio. En el vault del que sale esta plantilla, antes del lint, 19 de 77 eventos incumplían el contrato y en 24 nodos la fecha iba por detrás de su último cambio o no existía.

### Anti-duplicación de conceptos
Antes de crear un concepto, leer los conceptos existentes **de su ámbito** (§7, regla dura anti-solapamiento: los hijos de su hub vía L1, o su carpeta si es de rango hub) — nunca la base entera. Si similitud >70% → fusionar, no crear paralelo.

---

## 13. Convenciones generales

- **Nombres de archivo:** minúsculas, guiones, sin acentos. Título legible en frontmatter + H1.
- **Wikilinks:** sintaxis Obsidian. Enlaces de entidad por nombre, no por ruta.
- **Enlaces en frontmatter, siempre entre comillas:** `padre: "[[x]]"`. Sin comillas, Obsidian y Dataview no los leen como enlace; el grep del agente sí, y por eso el fallo pasa desapercibido. `_herramientas/lint_estructura.py` lo detecta.
- **Procedencia de enlaces:** todo wikilink no trivial (`padre`, `relacionado_con`, y enlaces de cuerpo con peso semántico) lleva `origen_enlace: explícito | inferido`.
  - `explícito` — la fuente o el usuario afirmó la relación directamente.
  - `inferido` — el LLM la dedujo conectando dos nodos por su cuenta.
  - Vocabulario cerrado, misma disciplina que §4: ante duda, el LLM pregunta antes de asignar, nunca aproxima.
  - **No retroactivo.** Si migras notas que ya existían, sus enlaces no se etiquetan a posteriori — inventar la procedencia de un enlace ya escrito sería la alucinación que esta regla existe para evitar. La ausencia del campo ya los marca como anteriores. El lint lo exige solo en los nodos creados después de `REGLA_ORIGEN`, una fecha al principio de `_herramientas/lint_estructura.py`: si migras notas fechadas después de ese día, cámbiala por el día en que empezaste el vault.
- **Idioma:** español. Términos técnicos en inglés si no hay equivalente. *(Cámbialo al tuyo; los nombres de campo y de carpeta pueden quedarse como están.)*
- **Fechas:** ISO `YYYY-MM-DD`. Relativas → absolutas antes de guardar.
- **`última_actualización`:** fecha del último cambio de contenido del nodo. La pone quien lo cambia, en el mismo paso; el hook lo exige (§12). Una migración mecánica —marcado, renombrar un campo— no la mueve.
- **Tono:** las páginas son claras y estructuradas, pero preservan las metáforas del usuario en citas. La eficiencia nunca sacrifica la voz (ver `aeternea-desafios-pendientes.md`).

---

## 14. Vocabulario cerrado — registro de ampliaciones

Los valores de los ejes cerrados solo se amplían aquí, con aprobación del usuario.

- `cercania`: nucleo, cercana, orbita, distante — **mide vínculo operativo, no convivencia (§4)**
- `rol_dinamica`: mentor, aliado, espejo, antagonista, dependiente, neutro
- `intensidad`: baja, media, alta, Overclocking

*(Ampliaciones futuras se registran debajo con fecha.)*


---

## 15. El log — formato, acceso y rotación

### Regla de acceso (la que ahorra tokens)

**El log es de escritura, no de lectura.** No entra en el pre-flight (§7) ni en ninguna operación por defecto. Se abre sólo ante una pregunta explícitamente histórica (*¿por qué…?, ¿cuándo…?, ¿qué cambió en…?*), y aun entonces buscando la sección concreta, nunca cargándolo entero. **Para añadir una entrada no hace falta leerlo**: se inserta bajo la cabecera.

### Formato de entrada (obligatorio)

Objetivo: ≤80 palabras por entrada. El log registra **qué se hizo y por qué no era obvio**, no re-describe lo que ya dicen los nodos.

```markdown
## [YYYY-MM-DD] tipo | título
**Dominio:** technical | personal | meta · **Fuente:** de dónde salió

**Creadas:** `nodo-a`, `nodo-b`
**Actualizadas:** `nodo-c`, `index_x`
**Filesystem:** movimientos de archivo, si los hubo

**Decisiones:** sólo las que NO se deducen leyendo el resultado.
```

Tipos: `ingest` · `query` · `lint` · `schema` · `migración`. `query` solo cuando la consulta deja un nodo (§7): una que solo lee no se registra.

**Prohibido:** describir el contenido de cada nodo creado (ya está en el nodo), repetir lo que el frontmatter dice, narrar el proceso. Si una decisión se entiende abriendo el nodo, no va al log.

### Rotación

**Cuatrimestral** (C1 ene-abr · C2 may-ago · C3 sep-dic) **o** al superar **2.000 palabras**, lo que ocurra antes. Si el tamaño dispara dentro de un cuatrimestre, la partición lleva sufijo: `log-2026-C2-01.md`, `-02`…

- El techo de 2.000 aplica **sólo al log caliente** — el que puede cargarse por accidente. Las particiones frías no tienen techo: viven en `_log_archivo/` (carpeta `_`, invisible al Lint y al pre-flight, §1) y no se leen nunca. Trocearlas más alarga el índice sin ahorrar un token.
- La cabecera del log caliente mantiene el **índice de particiones**: una línea por archivo frío con periodo, rango, nº de entradas y contenido. ~15 palabras por partición. Es lo que permite decidir si abrir un archivo frío **sin abrirlo**.

### Notas de evolución

Cada cambio de schema se registra en el log como `## [fecha] schema | descripción`.
