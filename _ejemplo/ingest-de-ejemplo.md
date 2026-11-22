# Ingest de ejemplo

Un ingest completo, de la fuente al log, para ver el sistema funcionando antes de meter nada tuyo. **Los datos son inventados.** Todo lo que hay aquí se ejecutó de verdad sobre una copia limpia de esta plantilla y pasó `_herramientas/lint_estructura.py`.

Los nodos van dentro de bloques de código para que sus enlaces no se mezclen con tu vault. Cuando lo hayas visto, borra la carpeta `_ejemplo/`.

---

## 0. La fuente

La usuaria deja `notas-sabado.md` en `01_Buffer_de_entrada/` y le pide al agente: *"ingesta notas-sabado.md"*.

```text
Notas del sábado 14 de marzo

- Por fin monté el NAS con la Raspberry Pi 5 y dos discos de 4 TB en RAID 1 (mdadm). Unas 4 horas.
- Primer intento: el segundo disco no aparecía. Era la fuente: con 3 A no da para dos discos. Con la oficial de 5 A, bien.
- Marcos vino a ayudarme. Me explicó que RAID no es una copia de seguridad: "RAID te protege de que se muera un disco, no de que borres tú la carpeta". Me pasó su script de rsync para copiar a un disco externo.
- Me he dado cuenta de que no entiendo nada hasta que lo rompo. Leí la guía de mdadm dos veces y no me enteré; en cuanto el array falló, lo entendí en diez minutos. Si no lo toco, no lo entiendo.
- Marcos es el de siempre: el que me resuelve las dudas de redes desde que entré en la empresa.
- Siguiente: montar Samba para compartir desde el portátil.
```

## 1. Pre-flight L0 — el mapa (SCHEMA §7)

El agente lista los hubs y las casillas: **solo nombres, ningún contenido**. En un vault recién creado salen los 4 hubs estructurales y las 17 casillas de identidad (`identidad.md`, `id-autoconcepto.md` … `trayectoria.md`). Todavía no hay ni personas ni proyectos.

## 2. Clasificación fail-safe (SCHEMA §7)

| Marcador | ¿Presente? |
|---|---|
| 1ª persona íntima / tono confesional | No: notas factuales |
| Apelación a un "tú", verso, despedida o firma | No |
| Carga afectiva | No |

**Cero marcadores y estructura de notas → se atomiza.** Además es **mixta**: hay material técnico (el NAS) y personal (Marcos, cómo aprende la usuaria). Se **bifurca** y las dos ramas se unen con **un solo** enlace cruzado (SCHEMA §2).

## 3. Plan de atomización — lo que el agente enseña ANTES de escribir

```text
Técnico
  + entidades/nas-casero.md                      hub de proyecto (nuevo)
  + entidades/nas-casero-2026-03-14-montaje.md   evento: la sesión de montaje
Personal
  + personal/entidades_sociales/marcos.md        hub de persona (nuevo)
  ~ personal/identidad/id-estilo-cognitivo-aprendizaje.md   +1 manifestación, con 2 citas
Hilo fino
  evento → [[marcos]] en relacionado_con

Necesito dos datos para los ejes cerrados de Marcos (la fuente no basta):
  · cercania:   ¿cercana (tu referencia de redes) u orbita (solo trabajo)?
  · intensidad: ¿baja o media?
```

La usuaria contesta *"cercana y media"*. El agente **no aproxima**: si la realidad no encaja en el vocabulario de §14, pregunta antes de escribir. `rol_dinamica: mentor` sí sale directo de la fuente.

## 4. Anti-solapamiento — L1, solo del tema (SCHEMA §7)

```bash
grep -rlE '^padre: "?\[\[nas-casero(\]\]|\|)' --include='*.md' 02_Wiki   # nada: el proyecto no existe
ls 02_Wiki/personal/entidades_sociales/                                     # nada: Marcos no existe
```

Se mira el barrio del tema, nunca la base entera.

## 5. Nodos escritos

### `02_Wiki/entidades/nas-casero.md`
```markdown
---
tipo_nodo: hub
domain: technical
estado: activo
prioridad: media
ficha_viva: true
última_actividad: 2026-03-14
tags: [nas, raspberry-pi, raid, homelab]
aliases: [nas, nas casero, servidor de archivos, raspberry nas]
creation_date: 2026-03-14
última_actualización: 2026-03-14
---

# NAS casero

## Núcleo
Servidor de archivos doméstico: Raspberry Pi 5 con dos discos de 4 TB en RAID 1 (mdadm). Un sitio único para los archivos de casa, accesible desde el portátil.

## Por qué importa
`sin_datos`: la fuente no lo dice, y el agente no lo infiere (SCHEMA §7).

## Facetas
*(ninguna todavía)*

## Insights (decisiones)
*(ninguno todavía)*

## Eventos
- [[nas-casero-2026-03-14-montaje]]

## Estado
`activo`, en el frontmatter. Lo pendiente (Samba, el rsync) está en su último evento, no aquí: el hub no copia la fase (SCHEMA §7).

## Conexiones externas
*(ninguna)*
```

### `02_Wiki/entidades/nas-casero-2026-03-14-montaje.md`
```markdown
---
tipo_nodo: evento
domain: technical
padre: "[[nas-casero]]"
origen_enlace: explícito
nivel: 2
periodo: 2026-03-14
fuente: "2026-03-14 - notas-sabado.md"
relacionado_con: ["[[marcos]]"]      # el hilo fino de la fuente mixta (SCHEMA §2)
creation_date: 2026-03-14
última_actualización: 2026-03-14
---

# NAS casero — montaje del RAID 1 (2026-03-14)

## Contexto
Primera sesión del proyecto: una Raspberry Pi 5 y dos discos de 4 TB para un RAID 1 con mdadm, sin experiencia previa con RAID en Linux.

## Detalle
1. El segundo disco no aparecía. Causa: la fuente de 3 A no daba para dos discos; con la oficial de 5 A, resuelto.
2. Array RAID 1 creado con mdadm. Unas 4 horas en total.
3. Marcos aclaró que RAID no sustituye a una copia de seguridad y pasó su script de rsync a disco externo.

## Citas verbatim
> "RAID te protege de que se muera un disco, no de que borres tú la carpeta." — Marcos

> "Era la fuente: con 3 A no da para dos discos."

## Reflexión post
La avería de la fuente fue lo que hizo entender el array. Pendiente: Samba, y programar el rsync.
```

### `02_Wiki/personal/entidades_sociales/marcos.md`
```markdown
---
tipo_nodo: hub
arquetipo_taxonomico: entidad_social
domain: personal
cercania: cercana
rol_dinamica: mentor
intensidad: media
ambito: "trabajo — compañero desde que entró en la empresa"
aporte: "resuelve dudas de redes; enseña con criterio práctico"
aliases: [Marcos, el de redes, compañero de redes]
creation_date: 2026-03-14
última_actualización: 2026-03-14
---

# Marcos

## Núcleo
Compañero de trabajo y referencia técnica: *"el que me resuelve las dudas de redes desde que entré en la empresa"*.

## Facetas
*(ninguna todavía)*

## Eventos (ventana activa — máx. 10)
*(ninguno propio todavía: la sesión del NAS vive en la rama técnica y llega hasta aquí por el hilo fino)*

## Insights
*(ninguno todavía)*
```

### `02_Wiki/personal/identidad/id-estilo-cognitivo-aprendizaje.md` — lo que cambia
La casilla estaba en `sin_datos`, así que no se superó nada y no hace falta tocar `_historial_identidad/`. Pasa a `estado: activo` y gana:
```markdown
## Contenido

### Entiende rompiendo, no leyendo
La documentación sola no le basta: entiende cuando el sistema falla delante de él. Con mdadm, dos lecturas de la guía sin resultado; diez minutos cuando el array falló.

## Evidencia

- 2026-03-14 · *"Si no lo toco, no lo entiendo."* · `2026-03-14 - notas-sabado.md`
- 2026-03-14 · *"Leí la guía de mdadm dos veces y no me enteré; en cuanto el array falló, lo entendí en diez minutos."* · ídem

<!-- Una línea por afirmación: fecha · cita verbatim · fuente. Sin evidencia no se escribe (SCHEMA §8).
     Lo que deje de ser cierto baja a personal/_historial_identidad/id-estilo-cognitivo-aprendizaje.md antes de reescribir. -->
```

## 6. Índice, log y fuente

- `index_tecnico.md` gana una fila en *Hubs* (`nas-casero`) y otra en *Fuentes procesadas*. `index_personal.md` no se toca: Marcos aparece solo en las vistas Dataview.
- `log.md`, bajo la cabecera, sin leer el resto:

```markdown
## [2026-03-14] ingest | Notas del sábado: montaje del NAS
**Dominio:** technical + personal (fuente mixta) · **Fuente:** `notas-sabado.md`

**Creadas:** `nas-casero`, `nas-casero-2026-03-14-montaje`, `marcos`
**Actualizadas:** `id-estilo-cognitivo-aprendizaje`, `index_tecnico`
**Filesystem:** `notas-sabado.md` → `_procesados/2026-03-14 - notas-sabado.md`

**Decisiones:** fuente bifurcada, con hilo fino evento → `marcos`. `cercania: cercana` e `intensidad: media` las confirmó la usuaria: la fuente no bastaba para elegir.
```

- La fuente se **mueve**, no se borra: `01_Buffer_de_entrada/_procesados/2026-03-14 - notas-sabado.md`.

## 7. Comprobación

```text
$ python3 _herramientas/lint_estructura.py
Lint estructural — 29 nodos en 02_Wiki/ (carpetas `_` ignoradas)

🟢 Todo en orden.
```

Si lo reproduces hoy verás además un 🟡 en `nas-casero`: su `última_actividad` es del 2026-03-14 y, pasados 90 días, el lint pregunta si sigue vivo (§12). Es el aviso funcionando, no un error.

