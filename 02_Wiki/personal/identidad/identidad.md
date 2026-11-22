---
tipo_nodo: hub
arquetipo_taxonomico: identidad
domain: personal
estado: activo
aliases: [identidad, personalidad, forma de ser, quién soy, psicología]
creation_date: 2026-10-29
última_actualización: 2026-10-29
---

# Identidad

Psicología base del usuario en **17 casillas fijas**. La información nueva **actualiza** una casilla; nunca crea otra (SCHEMA §8). Por eso entran enteras en el pre-flight L0: su coste no crece con los ingests.

## Las casillas

**Base — estático, solo evidencia directa**
[[id-demograficos]] · [[id-historia-socio-familiar]] · [[id-biologico-salud]]

**Rasgos — sin puntuar, sin escalas**
[[id-rasgo-estabilidad-emocional]] · [[id-rasgo-extraversion]] · [[id-rasgo-apertura]] · [[id-rasgo-amabilidad]] · [[id-rasgo-responsabilidad]]

**Dinámica y funcionamiento**
[[id-defensas-afrontamiento]] · [[id-autoconcepto]] · [[id-valores-proposito]] · [[id-estilo-interpersonal]] · [[id-ritmos-energia-atencion]] · [[id-estilo-cognitivo-aprendizaje]] · [[id-patron-inicio-cierre]] · [[id-metricas-actividad]]

**Derivado** — [[id-sintesis]] · no se escribe a mano, se deriva por etapas.

## Reglas de escritura (inviolables — texto completo en SCHEMA §8)

- **Registrar, no evaluar.** Se escribe lo que dice la fuente, con su cita. Prohibido puntuar o escalar.
- **Sin evidencia no se escribe.** Fecha + verbatim por afirmación; un hueco se queda `sin_datos`.
- **Casillas sensibles** (demográficos, historia socio-familiar, salud): solo afirmación directa. Prohibida la inferencia.
- **Sin marco clínico.** La estructura ordena, no diagnostica.

## Ramas hermanas — el resto de ti

- [[trayectoria]] — evolución profesional, por etapas
- [[laboratorio]] — análisis de dinámicas sociales
- [[literatura]] — textos intactos
- Personas — `personal/entidades_sociales/`, con vistas en [[index_personal]]

## Histórico

Lo superado de cada casilla baja a `personal/_historial_identidad/<casilla>.md` — append-only, invisible al Lint y al pre-flight, solo bajo demanda (*"¿cómo he cambiado?"*).
