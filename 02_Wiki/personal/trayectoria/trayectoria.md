---
tipo_nodo: hub
arquetipo_taxonomico: trayectoria
domain: personal
estado: activo
aliases: [trayectoria, carrera, evolución profesional, etapas, historia profesional]
creation_date: 2026-10-29
última_actualización: 2026-10-29
---

# Trayectoria

Evolución profesional del usuario. **Régimen acumulativo**: nada reemplaza a nada.

## Por qué hay etapas y no una lista de hitos

Un hub plano con cientos de hitos hace que cada consulta L1 devuelva cientos de líneas. La capa de **etapa** (SCHEMA §3) rompe eso: L1 sobre este hub devuelve **etapas**, no hitos. Las etapas crecen a razón de una o dos por año; los hitos, sin límite. El coste queda atado a lo que crece despacio.

## Etapas

`sin_datos` — las revela el material, no se definen a priori.

## Ciclo de vida de una etapa

1. **Activa** — sus eventos cuelgan vivos. Ventana de ~10-15 (SCHEMA §6).
2. **Al cerrarse** — se consolida en síntesis + hitos que de verdad importaron.
3. **El detalle completo** baja a `personal/_historial_trayectoria/<etapa>.md` — append-only, invisible al Lint y al pre-flight. **Nada se pierde**: se lee solo bajo demanda.

## Qué NO entra aquí

Un hito entra si marcó una dirección, cerró una puerta o enseñó algo que sigue vigente. Lo demás es ruido con fecha.

## Ramas hermanas

- [[identidad]] — quién eres, en 17 casillas
