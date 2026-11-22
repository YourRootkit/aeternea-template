# Índice Personal — Aeternea Wiki

Catálogo del dominio personal. Las **personas** se navegan por vistas dimensionales auto-generadas (Dataview); el resto de contenido, por taxonomía.

> Las vistas Dataview se renderizan en Obsidian. El LLM no las ejecuta — para enumerar personas usa glob de `personal/entidades_sociales/` + lectura de frontmatter (SCHEMA §7).

---

## 👥 Personas — vistas dimensionales

### Núcleo íntimo
```dataview
TABLE WITHOUT ID file.link AS Persona, rol_dinamica AS Rol, intensidad AS Intensidad
FROM "02_Wiki/personal/entidades_sociales"
WHERE tipo_nodo = "hub" AND cercania = "nucleo"
SORT choice(intensidad = "Overclocking", 4, choice(intensidad = "alta", 3, choice(intensidad = "media", 2, 1))) DESC
```

### En Overclocking *(consumiendo toda la banda ahora mismo)*
```dataview
TABLE WITHOUT ID file.link AS Persona, cercania AS Cercanía, rol_dinamica AS Rol
FROM "02_Wiki/personal/entidades_sociales"
WHERE tipo_nodo = "hub" AND intensidad = "Overclocking"
```

### Antagonistas activos
```dataview
TABLE WITHOUT ID file.link AS Persona, cercania AS Cercanía, intensidad AS Intensidad
FROM "02_Wiki/personal/entidades_sociales"
WHERE tipo_nodo = "hub" AND rol_dinamica = "antagonista"
```

### Todas las personas
```dataview
TABLE WITHOUT ID file.link AS Persona, cercania AS Cercanía, rol_dinamica AS Rol, intensidad AS Intensidad
FROM "02_Wiki/personal/entidades_sociales"
WHERE tipo_nodo = "hub"
SORT choice(cercania = "nucleo", 1, choice(cercania = "cercana", 2, choice(cercania = "orbita", 3, 4))) ASC, choice(intensidad = "Overclocking", 4, choice(intensidad = "alta", 3, choice(intensidad = "media", 2, 1))) DESC
```

---

## IDENTIDAD
*Psicología base. **Estructura fija de 17 casillas** bajo [[identidad]] — la información nueva actualiza una casilla, nunca crea otra. Lo superado baja a `_historial_identidad/` (frío, solo bajo demanda). Reglas de escritura en SCHEMA §8.*

**Punto de entrada: [[identidad]]**
```dataview
LIST FROM "02_Wiki/personal/identidad" WHERE arquetipo_taxonomico = "identidad" SORT file.name ASC
```

## LABORATORIO
*Análisis de dinámicas sociales, jerarquías, sesgos, comportamiento colectivo.*

**Punto de entrada: [[laboratorio]]**
```dataview
LIST FROM "02_Wiki/personal/laboratorio"
```

## LITERATURA
*Cartas, poesía, manifiestos, reflexiones íntimas. Intactos, inmutables.*

**Punto de entrada: [[literatura]]**
```dataview
LIST FROM "02_Wiki/personal/literatura"
```

## TRAYECTORIA
*Evolución profesional. **Régimen acumulativo**: nada reemplaza a nada. Navegación por **etapas** — L1 devuelve etapas, no hitos (SCHEMA §3). Etapas cerradas → detalle en `_historial_trayectoria/`.*

**Punto de entrada: [[trayectoria]]**
```dataview
LIST FROM "02_Wiki/personal/trayectoria" SORT file.name ASC
```

## BAUL_TEMPORAL
*Fallback inclasificable. Gestión manual del usuario.*
```dataview
LIST FROM "02_Wiki/personal/baul_temporal"
```
