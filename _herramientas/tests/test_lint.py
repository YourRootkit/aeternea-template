"""Tests del lint estructural.

Caja negra: cada caso monta un vault mínimo en una carpeta temporal y lanza el script como lo
lanzaría un usuario. Solo se miran el código de salida y el informe.

    python3 -m unittest discover -s _herramientas/tests        (también vale: pytest _herramientas/tests)

Cada test lleva en su nombre el fallo real del que salió.
"""
import datetime
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

LINT = pathlib.Path(__file__).resolve().parents[1] / "lint_estructura.py"
HOY = datetime.date.today()
SCHEMA = (
    "# Schema de prueba\n\n## 14. Vocabulario cerrado\n\n"
    "- `cercania`: nucleo, cercana, orbita, distante — nota que no es un valor\n"
    "- `intensidad`: baja, media, alta, Overclocking\n\n## 15. El log\n"
)
EVENTO = '## Contexto\nc\n\n## Detalle\nd\n\n## Citas verbatim\n> "uno"\n\n> "dos"\n\n## Reflexión post\nr\n'


def nodo(cuerpo="# Nodo\n", **campos):
    """Texto de un nodo. Los campos sustituyen o amplían el frontmatter mínimo; None lo quita."""
    fm = {"tipo_nodo": "hub", "domain": "personal", "creation_date": "2026-01-01"}
    fm.update(campos)
    return "---\n" + "".join(f"{k}: {v}\n" for k, v in fm.items() if v is not None) + "---\n" + cuerpo


class Caso(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = pathlib.Path(self._tmp.name)
        (self.raiz / "02_Wiki").mkdir()
        (self.raiz / "SCHEMA.md").write_text(SCHEMA, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def escribe(self, rel, texto):
        ruta = self.raiz / "02_Wiki" / rel
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        return ruta

    def lint(self, *args, **entorno):
        r = subprocess.run([sys.executable, str(LINT), str(self.raiz), *args], capture_output=True,
                           text=True, encoding="utf-8", env={**os.environ, **entorno})
        return r.returncode, r.stdout + r.stderr

    def da_rojo(self, esperado, *args, **entorno):
        codigo, salida = self.lint(*args, **entorno)
        self.assertNotIn("Traceback", salida)
        self.assertEqual(codigo, 1, salida)
        self.assertIn(esperado, salida)
        return salida

    def pasa(self, *args, **entorno):
        codigo, salida = self.lint(*args, **entorno)
        self.assertEqual(codigo, 0, salida)
        self.assertNotIn("🔴", salida)
        return salida


class Basico(Caso):
    def test_vault_limpio_sale_en_verde(self):
        self.escribe("a.md", nodo())
        self.assertIn("🟢 Todo en orden.", self.pasa())

    def test_las_carpetas_con_guion_bajo_se_ignoran(self):
        self.escribe("a.md", nodo())
        self.escribe("_archivo/roto.md", "sin frontmatter y con [[enlace-roto]]\n")
        self.assertIn("1 nodos", self.pasa())

    def test_sin_frontmatter_es_rojo(self):
        self.escribe("a.md", "# solo un título\n")
        self.da_rojo("sin frontmatter")

    def test_falta_un_campo_obligatorio(self):
        self.escribe("a.md", nodo(creation_date=None))
        self.da_rojo("falta `creation_date`")

    def test_readme_de_carpeta_no_es_un_nodo(self):
        # 5 rojos de ruido en el vault real: los README de carpeta no llevan frontmatter
        self.escribe("personal/README.md", "# Qué va en esta carpeta\n")
        self.pasa()

    def test_enlace_de_frontmatter_sin_comillas(self):
        self.escribe("a.md", nodo(padre="[[b]]"))
        self.escribe("b.md", nodo())
        self.da_rojo("sin comillas")

    def test_padre_que_no_existe(self):
        self.escribe("a.md", nodo(padre='"[[no-existe]]"'))
        self.da_rojo("apunta a [[no-existe]]")

    def test_techo_duro(self):
        self.escribe("a.md", nodo("palabra " * 401))
        self.da_rojo("techo duro 400")

    def test_el_frontmatter_no_cuenta_para_el_techo(self):
        # caso real: un hub con 337 palabras de cuerpo medía 411 con frontmatter; techo 400
        alias = ", ".join(f"alias{i}" for i in range(200))
        self.escribe("a.md", nodo("palabra " * 390, aliases=f"[{alias}]"))
        self.pasa()


class NuncaRevienta(Caso):
    """Siete entradas que daban traceback y dejaban al vault sin informe."""

    def test_tipo_nodo_como_lista(self):
        self.escribe("a.md", nodo(tipo_nodo="[hub, faceta]"))
        self.da_rojo("`tipo_nodo` debe ser un único valor de texto y es una lista")

    def test_domain_como_lista(self):
        # así lo escribía el CLAUDE.md del vault: `domain: [technical, personal]`
        self.escribe("a.md", nodo(domain="[technical, personal]"))
        self.da_rojo("`domain` debe ser un único valor de texto y es una lista")

    def test_fecha_imposible(self):
        # PyYAML lanza ValueError, no YAMLError, al construir el 30 de febrero
        self.escribe("a.md", nodo(creation_date="2026-02-30"))
        self.da_rojo("valor imposible")

    def test_fecha_que_no_es_iso(self):
        self.escribe("a.md", nodo(creation_date="marzo de 2026"))
        self.da_rojo("no es una fecha ISO")

    def test_nivel_no_numerico(self):
        self.escribe("a.md", nodo(tipo_nodo="faceta", domain="technical", nivel="tres"))
        self.pasa()

    def test_aliases_que_no_es_lista(self):
        self.escribe("a.md", nodo(arquetipo_taxonomico="entidad_social", aliases=5))
        self.da_rojo("`aliases` debe ser una lista")

    def test_archivo_que_no_es_utf8(self):
        (self.raiz / "02_Wiki" / "a.md").write_bytes(nodo().encode("utf-8") + b"caf\xe9\n")
        self.da_rojo("no está en UTF-8")

    def test_un_nodo_roto_no_tapa_los_fallos_de_otro(self):
        self.escribe("a.md", nodo(tipo_nodo="[hub]"))
        self.escribe("b.md", nodo(creation_date=None))
        salida = self.da_rojo("a.md: `tipo_nodo` debe ser")
        self.assertIn("b.md: falta `creation_date`", salida)

    def test_sin_schema_es_error_de_uso(self):
        (self.raiz / "SCHEMA.md").unlink()
        codigo, salida = self.lint()
        self.assertEqual(codigo, 2, salida)
        self.assertNotIn("Traceback", salida)
        self.assertIn("SCHEMA.md", salida)

    def test_schema_sin_seccion_14_es_error_de_uso(self):
        (self.raiz / "SCHEMA.md").write_text("# Schema\n\n## 13. Otra cosa\n", encoding="utf-8")
        codigo, salida = self.lint()
        self.assertEqual(codigo, 2, salida)
        self.assertIn("## 14.", salida)


class VocabularioCerrado(Caso):
    def test_valor_fuera_de_la_lista(self):
        self.escribe("a.md", nodo(intensidad="PENDIENTE_USUARIO"))
        self.da_rojo("intensidad = `PENDIENTE_USUARIO` no está en SCHEMA §14")

    def test_eje_vacio_es_aviso_no_rojo(self):
        self.escribe("a.md", nodo(intensidad=""))
        self.assertIn("`intensidad` sin asignar", self.pasa())

    def test_la_nota_tras_la_raya_no_es_un_valor(self):
        self.escribe("a.md", nodo(cercania="nota que no es un valor"))
        self.da_rojo("cercania =")


class ProcedenciaDeEnlaces(Caso):
    """§13: desde el 2026-08-03, un nodo que enlaza en su frontmatter dice si el enlace es explícito o inferido."""

    def test_nodo_nuevo_con_padre_y_sin_origen(self):
        self.escribe("hub.md", nodo())
        self.escribe("a.md", nodo(padre='"[[hub]]"', creation_date="2026-08-04"))
        self.da_rojo("le falta `origen_enlace`")

    def test_nodo_nuevo_con_relacionado_con_y_sin_origen(self):
        self.escribe("hub.md", nodo())
        self.escribe("a.md", nodo(relacionado_con='["[[hub]]"]', creation_date="2026-11-13"))
        self.da_rojo("le falta `origen_enlace`")

    def test_la_regla_no_es_retroactiva(self):
        # 38 nodos del vault real son anteriores a la regla: etiquetarlos ahora sería inventar la procedencia
        self.escribe("hub.md", nodo())
        self.escribe("a.md", nodo(padre='"[[hub]]"', creation_date="2026-08-02"))
        self.assertIn("🟢 Todo en orden.", self.pasa())

    def test_creado_el_dia_de_la_regla_es_aviso(self):
        # caso real: dos nodos creados el mismo día que la regla; el log no dice qué fue antes
        self.escribe("hub.md", nodo())
        self.escribe("a.md", nodo(padre='"[[hub]]"', creation_date="2026-08-03"))
        self.assertIn("lo decide el usuario", self.pasa())

    def test_con_origen_pasa(self):
        self.escribe("hub.md", nodo())
        self.escribe("a.md", nodo(padre='"[[hub]]"', origen_enlace="inferido", creation_date="2026-11-13"))
        self.assertIn("🟢 Todo en orden.", self.pasa())

    def test_nodo_sin_enlaces_en_el_frontmatter_no_lo_necesita(self):
        self.escribe("a.md", nodo(creation_date="2026-11-13"))
        self.assertIn("🟢 Todo en orden.", self.pasa())


class Enlaces(Caso):
    def test_wikilink_roto(self):
        self.escribe("a.md", nodo("# a\n[[no-existe]]\n"))
        self.da_rojo("enlace roto [[no-existe]]")

    def test_alias_escapado_dentro_de_una_tabla(self):
        # rojo falso: `[[b\|alias]]` se leía como enlace a `b\`
        self.escribe("a.md", nodo("# a\n\n| Nodo | Nota |\n|---|---|\n| [[b\\|el alias]] | x |\n"))
        self.escribe("b.md", nodo())
        self.pasa()

    def test_enlace_markdown_roto(self):
        # `index_tecnico.md` del vault real: 17 enlaces markdown que nadie comprobaba
        self.escribe("a.md", nodo("# a\n[no existe](entidades/no-existe.md)\n"))
        self.da_rojo("enlace markdown roto (entidades/no-existe.md)")

    def test_enlace_markdown_valido_con_espacios_y_ancla(self):
        self.escribe("entidades/con espacio.md", nodo())
        self.escribe("a.md", nodo("# a\n[sí](entidades/con%20espacio.md#seccion) y [otro](<entidades/con espacio.md>)\n"))
        self.pasa()

    def test_enlaces_externos_y_anclas_no_se_comprueban(self):
        self.escribe("a.md", nodo("# a\n[web](https://example.org/x.md) [correo](mailto:a@example.org) [aquí](#arriba)\n"))
        self.pasa()

    def test_un_enlace_no_resuelve_contra_las_plantillas(self):
        # rojo que no salía: `[[evento]]` se daba por bueno porque existe `_plantillas/evento.md`
        (self.raiz / "_plantillas").mkdir()
        (self.raiz / "_plantillas" / "evento.md").write_text("---\ntipo_nodo: evento\n---\n", encoding="utf-8")
        self.escribe("a.md", nodo("# a\n[[evento]]\n"))
        self.da_rojo("enlace roto [[evento]]")

    def test_los_enlaces_dentro_de_codigo_no_cuentan(self):
        self.escribe("a.md", nodo("# a\n`[[ejemplo]]` y\n```\n[[otro]] [x](no.md)\n```\n"))
        self.pasa()


class ContratoDeEvento(Caso):
    def evento(self, cuerpo, **campos):
        self.escribe("e.md", nodo(cuerpo, tipo_nodo="evento", **campos))

    def test_evento_correcto(self):
        self.evento(EVENTO)
        self.pasa()

    def test_secciones_extra_en_medio_no_molestan(self):
        self.evento(EVENTO.replace("## Reflexión post", "## Conexiones\nx\n\n## Reflexión post"))
        self.pasa()

    def test_cabeceras_de_nivel_3_no_valen(self):
        # `"## Contexto" in cuerpo` es una subcadena: `### Contexto` la contenía y pasaba
        self.evento(EVENTO.replace("## ", "### "))
        self.da_rojo("está como `### Contexto`: debe ser `##`")

    def test_cabecera_con_coletilla_no_vale(self):
        self.evento(EVENTO.replace("## Citas verbatim", "## Citas"))
        self.da_rojo("hay `## Citas`: debe llamarse exactamente `## Citas verbatim`")

    def test_orden_de_las_secciones(self):
        self.evento('## Reflexión post\nr\n\n## Citas verbatim\n> "uno"\n\n> "dos"\n\n## Detalle\nd\n\n## Contexto\nc\n')
        self.da_rojo("secciones fuera de orden")

    def test_reflexion_post_va_la_ultima(self):
        self.evento(EVENTO + "\n## Nota añadida después\nx\n")
        self.da_rojo("`## Reflexión post` no va último")

    def test_contexto_de_mas_de_300_palabras(self):
        self.evento(EVENTO.replace("## Contexto\nc", "## Contexto\n" + "palabra " * 301))
        self.da_rojo("`Contexto` de 301 palabras, máximo 300")

    def test_menos_de_dos_citas(self):
        self.evento(EVENTO.replace('> "dos"\n', ""))
        self.da_rojo("1 citas verbatim en línea `> `, mínimo 2")

    def test_citas_en_vineta_dicen_como_arreglarse(self):
        # 6 eventos del vault real tenían sus citas, pero en viñetas
        self.evento(EVENTO.replace('> "uno"\n\n> "dos"', '- "uno"\n- *"dos"*'))
        self.da_rojo("hay 2 en viñeta: pásalas a líneas `> `")

    def test_exencion_declarada_es_aviso(self):
        self.evento("## Contexto\nc\n", contrato_exento='"sesión de mayo sin citas en la fuente"')
        salida = self.pasa()
        self.assertIn("exento del contrato de evento (sesión de mayo sin citas en la fuente)", salida)

    def test_exencion_que_ya_no_hace_falta(self):
        self.evento(EVENTO, contrato_exento='"motivo viejo"')
        self.assertIn("ya cumple el contrato: quítalo", self.pasa())


class Avisos(Caso):
    def test_hub_activo_sin_actividad_en_90_dias(self):
        vieja = (HOY - datetime.timedelta(days=120)).isoformat()
        self.escribe("p.md", nodo(estado="activo", última_actividad=vieja))
        self.assertIn("`activo` sin actividad desde", self.pasa())

    def test_ventana_de_diez_eventos(self):
        self.escribe("h.md", nodo())
        for i in range(11):
            self.escribe(f"e{i}.md", nodo(EVENTO, tipo_nodo="evento", padre='"[[h]]"'))
        self.assertIn("11 eventos vivos bajo el hub", self.pasa())

    def test_log_con_tipo_fuera_de_vocabulario_y_pasado_de_techo(self):
        self.escribe("a.md", nodo())
        self.escribe("log.md", "# Log\n\n## [2026-01-01] mantenimiento | x\n\n## [2026-01-02] ingest | y\n" + "palabra " * 2001)
        salida = self.pasa()
        self.assertIn("tipo de entrada `mantenimiento` fuera de §15", salida)
        self.assertIn("toca rotar (§15)", salida)


class FechaAlDia(Caso):
    def test_nodo_tocado_con_fecha_vieja(self):
        self.escribe("a.md", nodo(última_actualización="2026-01-01"))
        self.da_rojo("pon la fecha de hoy", "--tocados", "02_Wiki/a.md")

    def test_nodo_tocado_sin_el_campo(self):
        self.escribe("a.md", nodo())
        self.da_rojo("pon la fecha de hoy", "--tocados", "02_Wiki/a.md")

    def test_nodo_tocado_con_fecha_de_hoy_o_de_ayer(self):
        # las sesiones cruzan la medianoche: se admite la fecha del día anterior
        self.escribe("a.md", nodo(última_actualización=HOY.isoformat()))
        self.escribe("b.md", nodo(última_actualización=(HOY - datetime.timedelta(days=1)).isoformat()))
        self.pasa("--tocados", "02_Wiki/a.md", "02_Wiki/b.md")

    def test_una_migracion_no_exige_fecha(self):
        self.escribe("a.md", nodo(última_actualización="2026-01-01"))
        self.pasa("--tocados", "02_Wiki/a.md", AETERNEA_MIGRACION="1")

    def test_indices_log_y_carpetas_frias_no_llevan_fecha(self):
        self.escribe("a.md", nodo())
        self.escribe("log.md", "# Log\n")
        self.escribe("_log_archivo/viejo.md", "# frío\n")
        self.pasa("--tocados", "02_Wiki/log.md", "02_Wiki/_log_archivo/viejo.md", "SCHEMA.md")


@unittest.skipUnless(shutil.which("git"), "necesita git")
class LoQueEntraEnUnCommit(Caso):
    def git(self, *args):
        subprocess.run(["git", "-C", str(self.raiz), "-c", "user.name=test", "-c", "user.email=test@example.org",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=", *args], check=True, capture_output=True)

    def repo_con(self, **nodos):
        for rel, texto in nodos.items():
            self.escribe(rel.replace("_md", ".md"), texto)
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "inicial")

    def test_modificar_un_nodo_inmutable_bloquea(self):
        # la regla de oro: una carta guardada intacta no se toca
        self.repo_con(carta_md=nodo("# Carta\ntexto original\n", tipo_nodo="fuente", inmutable="true"))
        self.escribe("carta.md", nodo("# Carta\ntexto resumido\n", tipo_nodo="fuente", inmutable="true"))
        self.git("add", "-A")
        self.da_rojo("modifica un nodo `inmutable: true`", "--commit")

    def test_borrar_un_nodo_inmutable_bloquea(self):
        self.repo_con(carta_md=nodo(tipo_nodo="fuente", inmutable="true"), a_md=nodo())
        (self.raiz / "02_Wiki" / "carta.md").unlink()
        self.git("add", "-A")
        self.da_rojo("borra un nodo `inmutable: true`", "--commit")

    def test_inmutable_con_comentario_detras_tambien_bloquea(self):
        # fallo real (2026-11-22): el hook buscaba `inmutable: true` con una regex de línea entera,
        # y un comentario detrás del valor le escondía la carta
        valor = "true   # exento de techos"
        self.repo_con(carta_md=nodo("# Carta\ntexto original\n", tipo_nodo="fuente", inmutable=valor), a_md=nodo())
        self.escribe("carta.md", nodo("# Carta\ntexto resumido\n", tipo_nodo="fuente", inmutable=valor))
        self.git("add", "-A")
        self.da_rojo("modifica un nodo `inmutable: true`", "--commit")
        self.git("rm", "-q", "--cached", "02_Wiki/carta.md")
        self.da_rojo("borra un nodo `inmutable: true`", "--commit")

    def test_las_plantillas_inmutables_quedan_protegidas(self):
        # contrato entre `_plantillas/` y el hook: cada línea `inmutable:` que se publica, tal cual,
        # tiene que bloquear el commit. Sin `_plantillas/` (el vault vivo no la trae), no aplica.
        plantillas = LINT.parents[1] / "_plantillas"
        lineas = [l for p in sorted(plantillas.glob("*.md")) for l in p.read_text(encoding="utf-8").splitlines()
                  if l.startswith("inmutable:")] if plantillas.is_dir() else []
        if not lineas:
            self.skipTest("no hay `_plantillas/` con nodos inmutables")
        valores = [l.split(":", 1)[1].strip() for l in lineas]
        self.repo_con(**{f"carta{i}_md": nodo("# Carta\noriginal\n", tipo_nodo="fuente", inmutable=v)
                         for i, v in enumerate(valores)})
        for i, v in enumerate(valores):
            self.escribe(f"carta{i}.md", nodo("# Carta\nresumida\n", tipo_nodo="fuente", inmutable=v))
        self.git("add", "-A")
        salida = self.da_rojo("modifica un nodo `inmutable: true`", "--commit")
        for i in range(len(valores)):
            self.assertIn(f"carta{i}.md: el commit modifica", salida)

    def test_el_usuario_puede_autorizar_tocar_un_inmutable(self):
        self.repo_con(carta_md=nodo("# Carta\ncon una errata\n", tipo_nodo="fuente", inmutable="true"))
        self.escribe("carta.md", nodo("# Carta\nsin la errata\n", tipo_nodo="fuente", inmutable="true"))
        self.git("add", "-A")
        self.pasa("--commit", AETERNEA_PERMITIR_INMUTABLE="1")

    def test_commit_que_cambia_un_nodo_sin_poner_la_fecha(self):
        # 21 nodos del vault real tenían la fecha por detrás de su último cambio, y 14 no la tenían
        self.repo_con(a_md=nodo(última_actualización="2026-01-01"))
        self.escribe("a.md", nodo("# Nodo\ncontenido nuevo\n", última_actualización="2026-01-01"))
        self.git("add", "-A")
        salida = self.da_rojo("cambia en este commit", "--commit")
        self.assertIn("Commit bloqueado", salida)

    def test_commit_con_la_fecha_puesta_pasa(self):
        self.repo_con(a_md=nodo(última_actualización="2026-01-01"))
        self.escribe("a.md", nodo("# Nodo\ncontenido nuevo\n", última_actualización=HOY.isoformat()))
        self.git("add", "-A")
        self.pasa("--commit")

    def test_un_commit_sin_nodos_no_exige_nada(self):
        self.repo_con(a_md=nodo(última_actualización="2026-01-01"))
        (self.raiz / "SCHEMA.md").write_text(SCHEMA + "\nuna línea más\n", encoding="utf-8")
        self.git("add", "-A")
        self.pasa("--commit")


if __name__ == "__main__":
    unittest.main()
