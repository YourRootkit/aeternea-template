---
tipo_nodo: hub
domain: technical
estado: activo                 # activo | completado | pausado | archivado
prioridad: media               # alta | media | baja — FOCUS admite 7 'alta' como máximo (SCHEMA §11)
ficha_viva: true               # ficha de proyecto (SCHEMA §7): el estado vive solo aquí arriba
última_actividad: YYYY-MM-DD   # último cambio en el proyecto: su carpeta o su último evento
tags: []
aliases: []                    # ≥3 para el discovery
creation_date: YYYY-MM-DD
última_actualización: YYYY-MM-DD
---

# <Proyecto>

## Núcleo
<!-- Qué es y para qué existe, en 3-5 líneas. Techo del hub: 400 palabras. -->

## Por qué importa
<!-- Con palabras del usuario, cita y fecha. Si no lo ha dicho: `sin_datos`. No se infiere (SCHEMA §7). -->

## Facetas
- [[<proyecto>-<subsistema>]]

## Insights (decisiones)
- [[<proyecto>-<decision>]]

## Eventos
- [[<proyecto>-YYYY-MM-DD-<sesion>]]

## Estado
<!-- `estado` y `prioridad` viven en el frontmatter. La fase y el siguiente paso NO van aquí: cambian
     cada sesión y se desfasarían. Van en el documento de entrada del proyecto o en su último evento (SCHEMA §7). -->

## Conexiones externas
<!-- Dónde vive el detalle: carpeta, repo o documento de entrada del proyecto. -->
