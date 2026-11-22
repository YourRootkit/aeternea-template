---
tipo_nodo: hub
nivel: raiz
domain: meta
creation_date: 2026-10-29
última_actualización: 2026-10-29
---

# Aeternea — MOC Raíz

Panel de atención. Solo muestra lo vivo y relevante (SCHEMA §11).

---

## 🎯 FOCUS
*`estado: activo` + `prioridad: alta`. Máximo 7: si hay un octavo, se degrada otro.*

```dataview
TABLE WITHOUT ID file.link AS Proyecto, domain AS Dominio, última_actividad AS "Última actividad"
FROM "02_Wiki/entidades" OR "02_Wiki/personal"
WHERE tipo_nodo = "hub" AND estado = "activo" AND prioridad = "alta"
SORT última_actividad DESC
LIMIT 7
```

---

## 📋 PENDIENTE
*`estado: activo` + prioridad media o baja.*

```dataview
LIST
FROM "02_Wiki/entidades" OR "02_Wiki/personal"
WHERE tipo_nodo = "hub" AND estado = "activo" AND (prioridad = "media" OR prioridad = "baja")
SORT última_actividad DESC
```

---

## Navegación

- [[index_tecnico]] — catálogo técnico
- [[index_personal]] — catálogo personal
- [[SCHEMA]] — especificación canónica del sistema
- [[log]] — historial de operaciones
- [[aeternea-desafios-pendientes]] — backlog vivo

> Si FOCUS y PENDIENTE salen vacíos es porque aún no hay hubs con `estado` y `prioridad`. Si salen como bloques de código, falta el plugin Dataview.
