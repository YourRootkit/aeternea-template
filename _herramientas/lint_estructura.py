#!/usr/bin/env python3
"""Lint estructural de Aeternea: la parte del Lint (SCHEMA §12) que no necesita juicio.

Comprueba frontmatter, vocabulario cerrado, punteros `padre`, enlaces rotos (wikilinks y
markdown), techos de palabras, el contrato de nodo-evento, estados sin actividad, la ventana
de eventos y el log. No decide nada: informa por severidad.

    python3 _herramientas/lint_estructura.py [ruta-del-vault]
    python3 _herramientas/lint_estructura.py --commit          # lo que usa el hook pre-commit
    python3 _herramientas/lint_estructura.py --tocados NODO...  # exige fecha al día en esos nodos

Códigos de salida: 0 sin ningún 🔴 · 1 con alguno · 2 si no pudo ejecutarse (no encuentra el
vault, `SCHEMA.md` o su §14). Un nodo ilegible nunca tumba el informe: sale como 🔴.

Variables de entorno (solo afectan a --commit y --tocados):
    AETERNEA_MIGRACION=1           no exige `última_actualización` al día (migraciones mecánicas)
    AETERNEA_PERMITIR_INMUTABLE=1  deja modificar o borrar un nodo `inmutable: true`

Requiere PyYAML (`pip install pyyaml`; en Linux, mejor el paquete de la distro).
"""
import argparse
import datetime
import os
import pathlib
import re
import subprocess
import sys
import urllib.parse


def salir(mensaje):
    """Error de uso: no hay informe posible. Código 2, distinto del 1 de «hay rojos»."""
    print(mensaje, file=sys.stderr)
    sys.exit(2)


try:
    import yaml
except ImportError:
    salir("Falta PyYAML: pip install pyyaml  (en Linux, mejor el paquete de tu distro: python3-yaml o python3-pyyaml)")

# En Windows, hasta Python 3.15, la salida por tubería (Git Bash, un agente) no es UTF-8
# y el informe casca al imprimir los emojis de severidad.
for _flujo in (sys.stdout, sys.stderr):
    _flujo.reconfigure(encoding="utf-8")

TIPOS = {"hub", "faceta", "evento", "insight", "concepto", "fuente", "etapa", "meta"}
DOMINIOS = {"technical", "personal", "meta"}
ORIGENES = {"explícito", "inferido"}
REGLA_ORIGEN = datetime.date(2026, 8, 3)  # §13: `origen_enlace` obligatorio desde este día; no es retroactivo
SIN_FRONTMATTER = {"index_tecnico.md", "index_personal.md", "log.md", "README.md"}  # capa humana, por diseño
SIN_DESTINO = {"_plantillas"}  # andamios: `[[evento]]` no puede darse por bueno contra `_plantillas/evento.md`

# SCHEMA §6 — (aviso, techo duro) por (tipo_nodo, domain). None = cualquier dominio.
# Se cuenta el cuerpo: sin frontmatter y sin comentarios HTML.
TECHOS = {
    ("hub", None): (250, 400),
    ("faceta", "personal"): (1500, 2500),
    ("faceta", "technical"): (1000, 1800),
    ("evento", "personal"): (2000, 2500),
    ("evento", "technical"): (1500, 2500),
    ("insight", "personal"): (1200, 2000),
    ("insight", "technical"): (800, 1500),
    ("fuente", None): (2000, 3000),
}
SUBFACETA_TECNICA = (600, 1200)
CABECERAS_EVENTO = ["Contexto", "Detalle", "Citas verbatim", "Reflexión post"]
CONTEXTO_MAX = 300        # palabras (§6)
VENTANA_EVENTOS = 10      # eventos vivos por hub (§6)
DIAS_SIN_ACTIVIDAD = 90   # hub `activo` sin actividad → sugerir `pausado` (§12)
LOG_TECHO = 2000          # palabras del log caliente (§15)
TIPOS_LOG = {"ingest", "query", "lint", "schema", "migración"}

ENLACE = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
ENLACE_MD = re.compile(r"!?\[[^\]\n]*\]\((?:<([^>\n]+)>|([^)\s]+))(?:\s+\"[^\"\n]*\")?\)")
ESQUEMA_URL = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
BLOQUE_CODIGO = re.compile(r"```.*?```", re.S)
CODIGO_LINEA = re.compile(r"`[^`\n]*`")
COMENTARIO = re.compile(r"<!--.*?-->", re.S)
CABECERA = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", re.M)
ENTRADA_LOG = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\][ \t]+([^|\n]+?)[ \t]*\|", re.M)
VINETA_CON_CITA = re.compile(r"\s*[-*+]\s+.*[\"«“]")


# ── Lectura ────────────────────────────────────────────────────────────────────────────

def vocabulario_cerrado(raiz):
    """Lee los ejes de SCHEMA §14: líneas `- `eje`: v1, v2, v3 — nota`."""
    esquema = raiz / "SCHEMA.md"
    if not esquema.is_file():
        salir(f"No encuentro {esquema}: de su §14 sale el vocabulario cerrado.")
    partes = re.split(r"^## 14\.", esquema.read_text(encoding="utf-8-sig"), maxsplit=1, flags=re.M)
    if len(partes) < 2:
        salir("SCHEMA.md no tiene una sección «## 14.»: de ahí sale el vocabulario cerrado.")
    seccion = re.split(r"^## ", partes[1], maxsplit=1, flags=re.M)[0]
    ejes = {}
    for m in re.finditer(r"^- `(\w+)`: ([^\n]+)", seccion, re.M):
        valores = m.group(2).split(" — ")[0]
        ejes[m.group(1)] = {v.strip() for v in valores.split(",")}
    if not ejes:
        salir("La §14 de SCHEMA.md no declara ningún eje con la forma «- `eje`: valor1, valor2».")
    return ejes


def partir(texto):
    """Devuelve (frontmatter_crudo | None, cuerpo)."""
    if not texto.startswith("---\n"):
        return None, texto
    fin = texto.find("\n---", 4)
    if fin < 0:
        return None, texto
    return texto[4:fin], texto[fin + 4:]


def cargar(ruta):
    """Lee un nodo. Devuelve (frontmatter | None, cuerpo, error | None)."""
    try:
        texto = ruta.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return None, "", "no está en UTF-8: guárdalo como UTF-8"
    crudo, cuerpo = partir(texto)
    if ruta.name in SIN_FRONTMATTER:
        return {}, cuerpo, None
    if crudo is None:
        return None, cuerpo, "sin frontmatter"
    try:
        fm = yaml.safe_load(crudo) or {}
    except yaml.YAMLError as e:
        return None, cuerpo, f"frontmatter ilegible ({str(e).splitlines()[0]})"
    except ValueError as e:  # YAML válido que no se puede construir: una fecha como 2026-02-30
        return None, cuerpo, f"frontmatter con un valor imposible ({e})"
    if not isinstance(fm, dict):
        return None, cuerpo, "lo que hay entre los `---` iniciales no es un frontmatter de campos"
    return fm, cuerpo, None


def fecha_de(valor):
    """Fecha ISO de un campo de frontmatter, o None si no lo es."""
    if isinstance(valor, datetime.datetime):
        return valor.date()
    if isinstance(valor, datetime.date):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.date.fromisoformat(valor.strip())
        except ValueError:
            return None
    return None


def clase_de(valor):
    if isinstance(valor, list):
        return "una lista"
    if isinstance(valor, dict):
        return "un bloque de campos"
    return f"un valor de tipo {type(valor).__name__}"


def texto_unico(fm, campo, rel, rojo):
    """El valor de un campo que debe ser texto. Si llega otra cosa, lo marca y devuelve None."""
    valor = fm.get(campo)
    if valor is None or isinstance(valor, str):
        return valor
    rojo.append(f"{rel}: `{campo}` debe ser un único valor de texto y es {clase_de(valor)}")
    return None


def enlaces_de(valor):
    """Enlaces de un campo de frontmatter. Un enlace sin comillas llega como lista anidada."""
    if valor is None:
        return [], False
    items = valor if isinstance(valor, list) else [valor]
    sin_comillas = any(isinstance(i, list) for i in items)
    destinos = []
    for i in items:
        if isinstance(i, str):
            destinos += [m.group(1).strip().rstrip("\\") for m in ENLACE.finditer(i)]
    return destinos, sin_comillas


def es_nodo(ruta, wiki):
    """Un .md del wiki fuera de las carpetas `_`."""
    try:
        partes = ruta.relative_to(wiki).parts
    except ValueError:
        return False
    return ruta.suffix == ".md" and not any(parte.startswith("_") for parte in partes)


# ── Contrato de nodo-evento (SCHEMA §6) ────────────────────────────────────────────────

def contrato_evento(cuerpo):
    """Lista de incumplimientos del contrato. Vacía si el evento cumple."""
    texto = COMENTARIO.sub("", BLOQUE_CODIGO.sub("", cuerpo))
    cabeceras = [(len(m.group(1)), m.group(2).strip(), m.start(), m.end()) for m in CABECERA.finditer(texto)]
    secciones = [c for c in cabeceras if c[0] == 2]
    fallos, lugar = [], {}

    for nombre in CABECERAS_EVENTO:
        exactas = [c for c in secciones if c[1] == nombre]
        if exactas:
            lugar[nombre] = exactas[0]
            if len(exactas) > 1:
                fallos.append(f"`## {nombre}` repetida")
            continue
        otro_nivel = [c for c in cabeceras if c[1] == nombre and c[0] != 2]
        parecida = [c for c in secciones if c[1].lower().startswith(nombre.lower().split()[0])]
        if otro_nivel:
            pista = f" (está como `{'#' * otro_nivel[0][0]} {nombre}`: debe ser `##`)"
        elif parecida:
            pista = f" (hay `## {parecida[0][1][:40]}`: debe llamarse exactamente `## {nombre}`)"
        else:
            pista = ""
        fallos.append(f"falta `## {nombre}`{pista}")

    presentes = [n for n in CABECERAS_EVENTO if n in lugar]
    if sorted(presentes, key=lambda n: lugar[n][2]) != presentes:
        fallos.append("secciones fuera de orden (Contexto → Detalle → Citas verbatim → Reflexión post)")
    if "Contexto" in lugar and secciones[0] is not lugar["Contexto"]:
        fallos.append(f"`## Contexto` no va primero (antes está `## {secciones[0][1][:40]}`)")
    if "Reflexión post" in lugar and secciones[-1] is not lugar["Reflexión post"]:
        fallos.append(f"`## Reflexión post` no va último (después está `## {secciones[-1][1][:40]}`)")

    def seccion(nombre):
        inicio = lugar[nombre]
        siguientes = [c for c in cabeceras if c[2] > inicio[2] and c[0] <= 2]
        return texto[inicio[3]:siguientes[0][2] if siguientes else len(texto)]

    if "Contexto" in lugar:
        palabras = len(seccion("Contexto").split())
        if palabras > CONTEXTO_MAX:
            fallos.append(f"`Contexto` de {palabras} palabras, máximo {CONTEXTO_MAX}")
    if "Citas verbatim" in lugar:
        lineas = seccion("Citas verbatim").splitlines()
        citas = sum(1 for l in lineas if l.lstrip().startswith(">") and l.strip("> \t\"«»“”*_"))
        if citas < 2:
            vinetas = sum(1 for l in lineas if VINETA_CON_CITA.match(l))
            pista = f"; hay {vinetas} en viñeta: pásalas a líneas `> `" if vinetas else ""
            fallos.append(f"{citas} citas verbatim en línea `> `, mínimo 2{pista}")
    return fallos


# ── Revisión de un nodo ────────────────────────────────────────────────────────────────

def revisar(ruta, rel, fm, cuerpo, vault):
    """Comprobaciones de un nodo ya cargado. Devuelve (rojos, amarillos)."""
    rojo, amarillo = [], []
    raiz, wiki, ejes, existentes, hoy = (vault[k] for k in ("raiz", "wiki", "ejes", "existentes", "hoy"))
    tipo = dom = None

    if ruta.name not in SIN_FRONTMATTER:
        for campo in ("tipo_nodo", "domain", "creation_date"):
            if campo not in fm:
                rojo.append(f"{rel}: falta `{campo}`")
        tipo = texto_unico(fm, "tipo_nodo", rel, rojo)
        dom = texto_unico(fm, "domain", rel, rojo)
        if tipo is not None and tipo not in TIPOS:
            rojo.append(f"{rel}: tipo_nodo `{tipo}` no existe (SCHEMA §3)")
            tipo = None
        if dom is not None and dom not in DOMINIOS:
            rojo.append(f"{rel}: domain `{dom}` no existe")
            dom = None
        if "origen_enlace" in fm and fm["origen_enlace"] not in ORIGENES:
            rojo.append(f"{rel}: origen_enlace `{fm['origen_enlace']}` fuera de vocabulario (§13)")
        if "origen_enlace" not in fm and ("padre" in fm or "relacionado_con" in fm):
            creado = fecha_de(fm.get("creation_date"))
            if creado and creado > REGLA_ORIGEN:
                rojo.append(f"{rel}: enlaza en el frontmatter y le falta `origen_enlace` (§13)")
            elif creado == REGLA_ORIGEN:  # no se sabe si se creó antes o después de fijarse la regla ese día
                amarillo.append(f"{rel}: sin `origen_enlace`; se creó el día en que se fijó la regla (§13) → lo decide el usuario")
        for campo in ("creation_date", "última_actualización", "última_actividad"):
            if fm.get(campo) is not None and fecha_de(fm[campo]) is None:
                rojo.append(f"{rel}: `{campo}` = `{fm[campo]}` no es una fecha ISO (YYYY-MM-DD)")

        # Ejes cerrados: solo valores de §14. Vacío = sin asignar todavía.
        for eje, valores in ejes.items():
            if eje in fm:
                v = fm[eje]
                if v is None:
                    amarillo.append(f"{rel}: `{eje}` sin asignar")
                elif not isinstance(v, str):
                    rojo.append(f"{rel}: `{eje}` debe ser un único valor de texto y es {clase_de(v)}")
                elif v not in valores:
                    rojo.append(f"{rel}: {eje} = `{v}` no está en SCHEMA §14 {sorted(valores)}")

        if fm.get("arquetipo_taxonomico") == "entidad_social" and tipo == "hub":
            aliases = fm.get("aliases")
            if aliases is not None and not isinstance(aliases, list):
                rojo.append(f"{rel}: `aliases` debe ser una lista y es {clase_de(aliases)}")
            elif len(aliases or []) < 3 and not fm.get("alias_único"):
                amarillo.append(f"{rel}: menos de 3 aliases (o falta `alias_único: true`)")

        # Enlaces del frontmatter
        for campo in ("padre", "relacionado_con", "fuentes_relacionadas"):
            destinos, sin_comillas = enlaces_de(fm.get(campo))
            if sin_comillas:
                rojo.append(f"{rel}: `{campo}` con enlace sin comillas — Obsidian no lo lee como enlace")
            for d in destinos:
                if d.lower() not in existentes:
                    rojo.append(f"{rel}: `{campo}` apunta a [[{d}]], que no existe")

        # Estados (§12): un hub `activo` sin actividad reciente
        actividad = fecha_de(fm.get("última_actividad"))
        if tipo == "hub" and fm.get("estado") == "activo" and actividad:
            dias = (hoy - actividad).days
            if dias > DIAS_SIN_ACTIVIDAD:
                amarillo.append(f"{rel}: `activo` sin actividad desde {actividad} ({dias} días) — ¿`pausado`? (§12)")

    # Enlaces del cuerpo (fuera de código y comentarios)
    limpio = CODIGO_LINEA.sub("", BLOQUE_CODIGO.sub("", COMENTARIO.sub("", cuerpo)))
    for m in ENLACE.finditer(limpio):
        d = m.group(1).strip().rstrip("\\")  # `[[x\|alias]]`: la barra escapa el `|` dentro de una tabla
        nombre = d.split("/")[-1].lower()
        if "<" in d:
            continue
        if nombre not in existentes and f"{nombre}.md" not in existentes:
            rojo.append(f"{rel}: enlace roto [[{d}]]")
    for m in ENLACE_MD.finditer(limpio):
        destino = (m.group(1) or m.group(2)).strip()
        if ESQUEMA_URL.match(destino) or destino.startswith("#"):
            continue  # web, mailto, ancla interna
        camino = urllib.parse.unquote(destino.split("#")[0].split("?")[0])
        if camino and not any((base / camino).exists() for base in (ruta.parent, wiki, raiz)):
            rojo.append(f"{rel}: enlace markdown roto ({destino})")

    # Techos (SCHEMA §6); literatura inmutable, exenta
    if fm and not fm.get("inmutable"):
        techo = TECHOS.get((tipo, dom)) or TECHOS.get((tipo, None))
        nivel = fm.get("nivel")
        if tipo == "faceta" and dom == "technical" and isinstance(nivel, int) and nivel >= 3:
            techo = SUBFACETA_TECNICA
        if techo:
            palabras = len(COMENTARIO.sub("", cuerpo).split())
            if palabras > techo[1]:
                rojo.append(f"{rel}: {palabras} palabras, techo duro {techo[1]} → fragmentar (§9)")
            elif palabras > techo[0]:
                amarillo.append(f"{rel}: {palabras} palabras, aviso en {techo[0]}")

    # Contrato de nodo-evento (SCHEMA §6)
    if tipo == "evento":
        fallos = contrato_evento(cuerpo)
        exento = fm.get("contrato_exento")
        exento = exento.strip() if isinstance(exento, str) else ""
        if fallos and exento:
            amarillo.append(f"{rel}: exento del contrato de evento ({exento}) — no cumple: {'; '.join(fallos)}")
        elif fallos:
            rojo.append(f"{rel}: evento — {'; '.join(fallos)}")
        elif "contrato_exento" in fm:
            amarillo.append(f"{rel}: lleva `contrato_exento` y ya cumple el contrato: quítalo")

    return rojo, amarillo


def revisar_log(wiki):
    """El log caliente (§15): tipos de entrada y techo de palabras."""
    amarillo = []
    log = wiki / "log.md"
    if not log.is_file():
        return amarillo
    try:
        texto = log.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return amarillo  # ya sale como 🔴 en la revisión del nodo
    for tipo in sorted({m.group(1) for m in ENTRADA_LOG.finditer(texto)} - TIPOS_LOG):
        amarillo.append(f"02_Wiki/log.md: tipo de entrada `{tipo}` fuera de §15 {sorted(TIPOS_LOG)}")
    palabras = len(texto.split())
    if palabras > LOG_TECHO:
        amarillo.append(f"02_Wiki/log.md: {palabras} palabras, techo {LOG_TECHO} → toca rotar (§15)")
    return amarillo


# ── Lo que entra en un commit ──────────────────────────────────────────────────────────

def git(raiz, *args):
    return subprocess.run(["git", "-C", str(raiz), *args], capture_output=True)


def cambios_del_commit(raiz):
    """[(estado, ruta)] de lo que está en el índice. Un renombrado sale como D + A."""
    r = git(raiz, "diff", "--cached", "--name-status", "--no-renames", "-z")
    if r.returncode != 0:
        salir("--commit necesita ejecutarse dentro de un repositorio git.")
    campos = r.stdout.decode("utf-8", "replace").split("\0")
    return [(campos[i], campos[i + 1]) for i in range(0, len(campos) - 1, 2)]


def es_inmutable(crudo):
    """¿El frontmatter declara `inmutable: true`? Se lee como YAML: con una regex de línea, un
    comentario detrás del valor (`inmutable: true  # …`) escondía el nodo al hook."""
    try:
        fm = yaml.safe_load(crudo)
    except (yaml.YAMLError, ValueError):
        fm = None
    if isinstance(fm, dict):
        return fm.get("inmutable") is True
    # Frontmatter ilegible: ante la duda, se protege (regla de oro, SCHEMA §7)
    return re.search(r"^inmutable:\s*true\b", crudo, re.M | re.I) is not None


def inmutables_tocados(raiz, cambios):
    """Nodos `inmutable: true` que el commit modifica o borra (regla de oro, SCHEMA §7)."""
    rojo = []
    for estado, ruta in cambios:
        if estado not in ("M", "D") or not ruta.endswith(".md"):
            continue
        anterior = git(raiz, "show", f"HEAD:{ruta}")
        if anterior.returncode != 0:
            continue
        crudo, _ = partir(anterior.stdout.decode("utf-8", "replace").replace("\r\n", "\n"))
        if crudo and es_inmutable(crudo):
            verbo = "borra" if estado == "D" else "modifica"
            rojo.append(f"{ruta}: el commit {verbo} un nodo `inmutable: true` — no se toca "
                        "(si lo ha pedido el usuario: AETERNEA_PERMITIR_INMUTABLE=1)")
    return rojo


def fechas_de_tocados(rutas, vault):
    """Un nodo que cambia lleva `última_actualización` de hoy (o de ayer: las sesiones cruzan medianoche)."""
    rojo = []
    limite = vault["hoy"] - datetime.timedelta(days=1)
    for r in rutas:
        ruta = pathlib.Path(r)
        ruta = ruta if ruta.is_absolute() else vault["raiz"] / ruta
        if not ruta.is_file() or not es_nodo(ruta.resolve(), vault["wiki"]) or ruta.name in SIN_FRONTMATTER:
            continue
        fm, _, error = cargar(ruta)
        if error or fm.get("inmutable"):
            continue  # el error ya sale en la revisión general
        fecha = fecha_de(fm.get("última_actualización"))
        if fecha is None or fecha < limite:
            rel = ruta.resolve().relative_to(vault["raiz"]).as_posix()
            rojo.append(f"{rel}: cambia en este commit y su `última_actualización` es "
                        f"`{fm.get('última_actualización')}` — pon la fecha de hoy "
                        "(migración mecánica: AETERNEA_MIGRACION=1)")
    return rojo


# ── Programa ───────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Lint estructural de Aeternea (SCHEMA §12).")
    ap.add_argument("vault", nargs="?", help="raíz del vault (por defecto, la carpeta que contiene _herramientas/)")
    ap.add_argument("--commit", action="store_true", help="añade las comprobaciones de lo que entra en el commit")
    ap.add_argument("--tocados", nargs="*", default=[], metavar="NODO", help="nodos que deben llevar la fecha al día")
    args = ap.parse_args()

    raiz = pathlib.Path(args.vault).resolve() if args.vault else pathlib.Path(__file__).resolve().parents[1]
    wiki = raiz / "02_Wiki"
    if not wiki.is_dir():
        salir(f"No encuentro {wiki}")

    visibles = [p for p in raiz.rglob("*")
                if p.is_file() and not any(parte.startswith(".") for parte in p.relative_to(raiz).parts)
                and p.relative_to(raiz).parts[0] not in SIN_DESTINO]
    existentes = {p.name.lower() for p in visibles} | {p.stem.lower() for p in visibles if p.suffix == ".md"}
    vault = {"raiz": raiz, "wiki": wiki, "ejes": vocabulario_cerrado(raiz),
             "existentes": existentes, "hoy": datetime.date.today()}

    rojo, amarillo = [], []
    nodos = sorted(p for p in wiki.rglob("*.md") if es_nodo(p, wiki))
    cargados = {}
    for p in nodos:
        rel = p.relative_to(raiz).as_posix()
        fm, cuerpo, error = cargar(p)
        if error:
            rojo.append(f"{rel}: {error}")
            continue
        cargados[p] = (rel, fm, cuerpo)

    # Ventana activa (§6): eventos vivos que cuelgan directamente de cada hub
    hubs = {p.stem.lower(): rel for p, (rel, fm, _) in cargados.items() if fm.get("tipo_nodo") == "hub"}
    eventos_por_hub = {}
    for p, (rel, fm, cuerpo) in cargados.items():
        if fm.get("tipo_nodo") == "evento":
            for padre in enlaces_de(fm.get("padre"))[0][:1]:
                eventos_por_hub[padre.lower()] = eventos_por_hub.get(padre.lower(), 0) + 1

    for p, (rel, fm, cuerpo) in cargados.items():
        try:
            r, a = revisar(p, rel, fm, cuerpo, vault)
        except Exception as e:  # red de seguridad: un nodo raro no puede dejar al vault sin informe
            r, a = [f"{rel}: el lint no ha podido revisarlo ({type(e).__name__}: {e}) — es un fallo del lint, avisa"], []
        rojo += r
        amarillo += a
    for nombre, n in sorted(eventos_por_hub.items()):
        if n > VENTANA_EVENTOS and nombre in hubs:
            amarillo.append(f"{hubs[nombre]}: {n} eventos vivos bajo el hub, ventana de {VENTANA_EVENTOS} → rollover o capa `etapa` (§6)")
    amarillo += revisar_log(wiki)

    tocados = list(args.tocados)
    if args.commit:
        cambios = cambios_del_commit(raiz)
        if os.environ.get("AETERNEA_PERMITIR_INMUTABLE") != "1":
            rojo += inmutables_tocados(raiz, cambios)
        tocados += [ruta for estado, ruta in cambios if estado in ("A", "M")]
    if tocados and os.environ.get("AETERNEA_MIGRACION") != "1":
        rojo += fechas_de_tocados(tocados, vault)

    if args.commit:  # en el hook, solo lo que bloquea: los avisos se ven lanzando el lint a mano
        if rojo:
            print(f"🔴 Necesita arreglo ({len(rojo)})")
            print("\n".join(f"  - {x}" for x in rojo), end="\n\n")
            print("Commit bloqueado: arregla los 🔴 de arriba y repite. (Emergencia: git commit --no-verify)")
        else:
            print(f"Lint estructural: {len(nodos)} nodos, ningún rojo ({len(amarillo)} avisos).")
        sys.exit(1 if rojo else 0)

    print(f"Lint estructural — {len(nodos)} nodos en {wiki.relative_to(raiz).as_posix()}/ (carpetas `_` ignoradas)\n")
    for titulo, lista in (("🔴 Necesita arreglo", rojo), ("🟡 Revisar", amarillo)):
        if lista:
            print(f"{titulo} ({len(lista)})")
            print("\n".join(f"  - {x}" for x in lista), end="\n\n")
    if not rojo and not amarillo:
        print("🟢 Todo en orden.")
    sys.exit(1 if rojo else 0)


if __name__ == "__main__":
    main()
