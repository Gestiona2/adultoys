#!/usr/bin/env python3
"""Genera el catalogo en PDF de Adultoyss.

    python3 tools/catalogo_pdf.py
    python3 tools/catalogo_pdf.py --base https://adultoyss.com/ --salida catalogo.pdf
    python3 tools/catalogo_pdf.py --todos        # incluye los agotados
    python3 tools/catalogo_pdf.py --tema halloween   # edicion de temporada

Sale con portada, menu por categorias (con enlaces y numero de pagina),
marcadores del lector de PDF y, en cada producto, un boton que abre su ficha
en la web. Lee los mismos datos que el sitio (src/datos/), asi que precios,
nombres y fotos nunca se desfasan: si cambia el catalogo, se vuelve a correr.

Solo incluye productos visibles y con existencias. Los ocultos (precio 0) y
los agotados no salen, igual que en la web.

Necesita: pip install weasyprint
"""
import argparse
import html
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "src" / "datos"
PUBLIC = RAIZ / "public"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def pesos(valor):
    return "$" + f"{int(valor):,}".replace(",", ".")


def esc(texto):
    return html.escape(str(texto or ""), quote=True)


def cargar(nombre):
    return json.loads((DATOS / nombre).read_text(encoding="utf-8"))


_CARPETA_IMG = None


def jpeg(origen, ancho_max, calidad=78):
    """WeasyPrint guarda los WebP sin comprimir (57 MB). Como JPEG pesa una
    fraccion. Se hace una copia temporal; las fotos del sitio no se tocan."""
    from PIL import Image
    destino = _CARPETA_IMG / (origen.stem + f"-{ancho_max}.jpg")
    if not destino.exists():
        with Image.open(origen) as im:
            im = im.convert("RGBA")
            fondo = Image.new("RGB", im.size, (255, 255, 255))
            fondo.paste(im, mask=im.split()[3])
            if fondo.width > ancho_max:
                fondo = fondo.resize((ancho_max, round(fondo.height * ancho_max / fondo.width)), Image.LANCZOS)
            fondo.save(destino, "JPEG", quality=calidad, optimize=True, progressive=True)
    return destino.as_uri()


def construir_html(base, todos, tema=None):
    config = cargar("config.json")
    categorias = sorted(cargar("categorias.json"), key=lambda c: c["orden"])
    productos = [p for p in cargar("productos.json") if not p["oculto"] and (todos or p["stock"])]

    por_categoria = {}
    for p in productos:
        por_categoria.setdefault(p["categoria"], []).append(p)
    for lista in por_categoria.values():
        lista.sort(key=lambda p: (p.get("subcategoria_nombre") or "", p["titulo"].lower()))
    categorias = [c for c in categorias if por_categoria.get(c["id"])]

    hoy = date.today()
    fecha = f"{MESES[hoy.month - 1].capitalize()} de {hoy.year}"
    wa = config["whatsapp"]
    wa_visible = config["sedes"][0].get("telefono_visible", f"+{wa}")
    enlace_wa = f"https://wa.me/{wa}"
    base = base.rstrip("/") + "/"

    def url_producto(slug):
        return f"{base}producto/{quote(slug)}/"

    logo = (PUBLIC / "img/marca/logo-adultoyss-claro.png").as_uri()
    portada = jpeg(PUBLIC / "img/sitio/banner-hero-neon-1200.webp", 1200, 80)
    sora = (PUBLIC / "fonts/sora-variable.woff2").as_uri()
    inter = (PUBLIC / "fonts/inter-variable.woff2").as_uri()

    partes = []
    hw = None
    if tema == "halloween":
        import catalogo_halloween as hw
        activos = hw.crear_activos(_CARPETA_IMG)

    # ---- portada ----
    if hw:
        partes.append(hw.portada(activos, logo, fecha, len(productos), base, enlace_wa, wa_visible, esc))
    else:
      partes.append(f"""
<section class="portada">
  <img class="portada-foto" src="{portada}" alt="">
  <div class="portada-velo"></div>
  <div class="portada-contenido">
    <img class="portada-logo" src="{logo}" alt="Adultoyss, tienda erótica">
    <p class="portada-etiqueta">CATÁLOGO · {esc(fecha.upper())}</p>
    <h1>Tu deseo,<br><span>nuestra misión.</span></h1>
    <p class="portada-texto">Juguetes, lencería y bienestar íntimo seleccionados para explorar sin juicios.
      Empaque neutro y atención por WhatsApp.</p>
    <p class="portada-cifra"><strong>{len(productos)}</strong> productos disponibles</p>
    <div class="portada-pie">
      <a class="portada-boton" href="{base}">Visitar la tienda web</a>
      <a class="portada-boton portada-boton-wa" href="{enlace_wa}">WhatsApp {esc(wa_visible)}</a>
      <p>Contenido exclusivo para mayores de 18 años.</p>
    </div>
  </div>
</section>""")

    # ---- menu ----
    filas = []
    for c in categorias:
        n = len(por_categoria[c["id"]])
        filas.append(f"""
      <a class="menu-fila" href="#cat-{esc(c['id'])}">
        <span class="menu-nombre">{esc(c['nombre'])}</span>
        <span class="menu-cuenta">{n} producto{'s' if n != 1 else ''}</span>
      </a>""")
    partes.append(f"""
<section class="menu" id="menu">
  {hw.decoracion_pagina(activos, False) if hw else ""}
  <p class="etiqueta">EXPLORA</p>
  <h2>Menú</h2>
  <p class="menu-texto">Toca una categoría para ir directo a ella. En cada producto, el botón
    <b>Ver en la web</b> abre su ficha para comprarlo.</p>
  <div class="menu-lista">{''.join(filas)}
  </div>
  <div class="menu-ayuda">
    <strong>¿No sabes por dónde empezar?</strong>
    <span>Escríbenos y te ayudamos a elegir, sin compromiso.</span>
    <a class="boton" href="{enlace_wa}">Hablar por WhatsApp</a>
  </div>
</section>""")

    # ---- categorias ----
    # La primera pagina de cada categoria lleva encabezado: caben 2 filas (6).
    # Las siguientes caben 3 filas (9).
    for c in categorias:
        lista = por_categoria[c["id"]]
        trozos = [lista[:6]] + [lista[i:i + 9] for i in range(6, len(lista), 9)]
        for orden, trozo in enumerate(trozos):
            primera = orden == 0
            tarjetas = []
            for p in trozo:
                foto = jpeg(PUBLIC / "img" / p["imagenes"][0], 420)
                sub = p.get("subcategoria_nombre") or ""
                marca = p.get("marca") or ""
                etiqueta = " · ".join(x for x in (sub, marca) if x)
                tarjetas.append(f"""
      <article class="tarjeta">
        <a class="tarjeta-foto" href="{url_producto(p['slug'])}"><img src="{foto}" alt="{esc(p['titulo'])}"></a>
        <div class="tarjeta-cuerpo">
          <p class="tarjeta-sub">{esc(etiqueta)}</p>
          <h3><a href="{url_producto(p['slug'])}">{esc(p['titulo'])}</a></h3>
          <p class="tarjeta-precio">{pesos(p['precio'])}</p>
          <a class="boton" href="{url_producto(p['slug'])}">Ver en la web <span>→</span></a>
        </div>
      </article>""")
            deco = (f'<img class="cat-deco-murci" src="{activos["murcielago"]}" alt="">'
                    f'<img class="cat-deco" src="{activos["calabaza"]}" alt="">') if hw else ""
            cabeza = (f"""<header class="cat-cabeza" id="cat-{esc(c['id'])}">{deco}
        <p class="etiqueta">CATEGORÍA</p>
        <h2>{esc(c['nombre'])}</h2>
        <p class="cat-cuenta">{len(lista)} producto{'s' if len(lista) != 1 else ''}</p>
      </header>""" if primera else f"""<header class="cat-cabeza cat-cabeza-sigue">
        <h2>{esc(c['nombre'])} <small>(continúa)</small></h2>
      </header>""")
            partes.append(f"""
<section class="pagina{' pagina-primera' if primera else ''}">
  {hw.decoracion_pagina(activos, (len(partes) + 1) % 2 == 1) if hw else ""}
  <div class="volver"><a href="#menu">↑ Volver al menú</a></div>
  {cabeza}
  <div class="grilla">{''.join(tarjetas)}
  </div>
</section>""")

    # ---- contraportada ----
    if hw:
        partes.append(hw.cierre(activos, logo, base, enlace_wa, wa_visible, esc))
    else:
      partes.append(f"""
<section class="cierre">
  <img class="cierre-logo" src="{logo}" alt="Adultoyss">
  <h2>¿Listo para elegir?</h2>
  <p>Compra en la web o escríbenos por WhatsApp. Te asesoramos con discreción.</p>
  <p><a class="portada-boton" href="{base}">Ir a la tienda web</a>
     <a class="portada-boton portada-boton-wa" href="{enlace_wa}">WhatsApp {esc(wa_visible)}</a></p>
  <small>Precios y disponibilidad sujetos a cambio. Producto para mayores de 18 años. Este catálogo
    es informativo y no reemplaza la consulta con un profesional de la salud.</small>
</section>""")

    css = CSS.replace("__SORA__", sora).replace("__INTER__", inter)
    if hw:
        css += hw.css(activos)
    titulo = f"Catálogo Adultoyss{' — Edición Halloween' if hw else ''} — {fecha}"
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>{esc(titulo)}</title>
<meta name="author" content="Adultoyss Tienda Erótica">
<meta name="description" content="Catálogo de productos de Adultoyss con enlace a cada producto en la web.">
<style>{css}</style></head>
<body>{''.join(partes)}</body></html>"""


CSS = """
@font-face { font-family: Sora; src: url(__SORA__); font-weight: 100 800; }
@font-face { font-family: Inter; src: url(__INTER__); font-weight: 100 900; }

:root { --bg:#07040d; --sup:#100b1a; --texto:#f6f2fb; --suave:#cec4dd; --mute:#9c90ae;
  --magenta:#ff2e9a; --violeta:#b45cff; --azul:#4d8dff; }
* { box-sizing: border-box; margin: 0; padding: 0; }
@page { size: A4; margin: 0; }
@page contenido {
  size: A4; margin: 16mm 12mm 18mm;
  background: var(--bg);
  @bottom-left { content: "ADULTOYSS · CATÁLOGO"; font: 600 7pt Inter; letter-spacing: .14em; color: var(--mute); }
  @bottom-center { content: element(volver); }
  @bottom-right { content: counter(page); font: 600 8pt Inter; color: var(--mute); }
}
@page portada { size: A4; margin: 0; background: var(--bg); }
.portada { page: portada; }
.menu, .pagina, .cierre { page: contenido; }
.volver { position: running(volver); font: 600 7.5pt Inter; }
.volver a { color: #ff8fcb; }
a { color: inherit; text-decoration: none; }
html { background: var(--bg); color: var(--texto); font-family: Inter, sans-serif; }
body { font-size: 10pt; }

/* portada */
.portada { position: relative; height: 297mm; width: 210mm; overflow: hidden; break-after: page; }
.portada-foto { position: absolute; right: -30mm; top: 0; height: 100%; width: 150mm; object-fit: cover; opacity: .85; }
.portada-velo { position: absolute; inset: 0;
  background: linear-gradient(90deg, #07040d 8%, rgba(7,4,13,.86) 48%, rgba(7,4,13,.25) 100%),
              linear-gradient(0deg, #07040d 0%, rgba(7,4,13,0) 34%); }
.portada-contenido { position: absolute; left: 18mm; top: 22mm; bottom: 20mm; width: 120mm; }
.portada-logo { height: 28mm; }
.portada-etiqueta { margin-top: 60mm; font: 700 8.5pt Inter; letter-spacing: .22em; color: #ff8fcb; }
.portada h1 { margin-top: 6mm; font: 800 40pt/1.02 Sora; letter-spacing: -.03em; }
.portada h1 span { color: var(--magenta); }
.portada-texto { margin-top: 8mm; font-size: 11.5pt; line-height: 1.6; color: var(--suave); max-width: 100mm; }
.portada-cifra { margin-top: 9mm; font-size: 10.5pt; color: var(--suave); }
.portada-cifra strong { font: 800 22pt Sora; color: #fff; margin-right: 2mm; }
.portada-pie { position: absolute; left: 0; bottom: 0; }
.portada-pie p { margin-top: 6mm; font-size: 8pt; color: var(--mute); }
.portada-boton { display: inline-block; padding: 3.2mm 6.5mm; border-radius: 99px; font: 700 9pt Inter; color: #fff;
  background: linear-gradient(100deg, var(--magenta), var(--violeta) 55%, var(--azul)); margin: 0 2mm 2mm 0; }
.portada-boton-wa { background: #17a34a; }

/* menu */
.etiqueta { font: 700 7.5pt Inter; letter-spacing: .2em; color: #ff8fcb; }
h2 { font: 800 24pt Sora; letter-spacing: -.02em; }
.menu { break-before: page; break-after: page; }
.menu h2 { margin-top: 2mm; font-size: 32pt; }
.menu-texto { margin: 4mm 0 8mm; color: var(--suave); line-height: 1.6; max-width: 140mm; }
.menu-lista { border-top: 1px solid rgba(255,255,255,.12); }
.menu-fila { display: flex; align-items: baseline; padding: 4.4mm 0; border-bottom: 1px solid rgba(255,255,255,.12); }
.menu-nombre { font: 700 14pt Sora; flex: 1; }
.menu-cuenta { font-size: 9pt; color: var(--mute); margin-right: 8mm; }
/* El numero lo pone el propio enlace: attr(href) debe leerse del <a>. */
.menu-fila::after { content: target-counter(attr(href url), page); font: 700 11pt Sora; color: var(--magenta);
  min-width: 10mm; text-align: right; }
.menu-fila { position: relative; }
.menu-ayuda { margin-top: 10mm; padding: 6mm 8mm; border-radius: 5mm; background: var(--sup);
  border: 1px solid rgba(255,46,154,.35); display: flex; flex-direction: column; gap: 2mm; }
.menu-ayuda strong { font: 700 13pt Sora; }
.menu-ayuda span { color: var(--suave); }
/* Color sólido: un degradado dentro de la tarjeta redondeada sale apagado en algunos lectores. */
.boton { display: inline-block; text-align: center; padding: 2.6mm 5mm; border-radius: 99px; font: 700 8.5pt Inter; color: #fff;
  background: #e5128a; }
.menu-ayuda .boton { align-self: flex-start; margin-top: 2mm; background: #17a34a; }

/* marcadores del lector de PDF */
.menu h2 { bookmark-level: 1; bookmark-label: "Menú"; }
.cat-cabeza:not(.cat-cabeza-sigue) h2 { bookmark-level: 1; bookmark-label: content(text); }

/* categorias */
.pagina { break-before: page; }
.cat-cabeza { margin-bottom: 6mm; padding-bottom: 4mm; border-bottom: 1px solid rgba(255,255,255,.12); }
.cat-cabeza h2 { margin-top: 1.5mm; }
.cat-cabeza-sigue h2 { font-size: 15pt; }
.cat-cabeza-sigue h2 small { font: 500 9pt Inter; color: var(--mute); }
.cat-cuenta { margin-top: 1.5mm; color: var(--mute); font-size: 9pt; }
.grilla { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5mm; }
.tarjeta { background: var(--sup); border: 1px solid rgba(255,255,255,.1); border-radius: 4mm; overflow: hidden;
  display: flex; flex-direction: column; break-inside: avoid; }
.tarjeta-foto { display: block; background: #fff; height: 38mm; }
.tarjeta-foto img { width: 100%; height: 100%; object-fit: contain; }
.tarjeta-cuerpo { padding: 2.8mm 3.2mm 3.2mm; display: flex; flex-direction: column; flex: 1; }
.tarjeta-sub { font: 700 6pt Inter; letter-spacing: .1em; text-transform: uppercase; color: #ff8fcb; height: 4.6mm; overflow: hidden; }
.tarjeta h3 { font: 600 8.6pt/1.25 Sora; height: 10.5mm; overflow: hidden; margin-top: 1mm; }
.tarjeta-precio { font: 800 12pt Sora; margin: 1mm 0 2.2mm; }
.tarjeta .boton { margin-top: auto; }

/* cierre */
.cierre { break-before: page; text-align: center; padding-top: 70mm; }
.cierre-logo { height: 26mm; }
.cierre h2 { margin-top: 12mm; font-size: 28pt; }
.cierre p { margin: 5mm auto 0; max-width: 120mm; color: var(--suave); line-height: 1.6; }
.cierre small { display: block; margin: 40mm auto 0; max-width: 140mm; color: var(--mute); font-size: 7.5pt; line-height: 1.6; }
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="https://demos.emp2web.com/adultoys/",
                    help="direccion publica del sitio; cada boton apunta a <base>/producto/<slug>")
    ap.add_argument("--salida", default=None, help="archivo PDF de salida")
    ap.add_argument("--tema", choices=["halloween"], default=None,
                    help="edicion tematica: halloween agrega telaranas, bruja, murcielagos y calabazas")
    ap.add_argument("--todos", action="store_true", help="incluir tambien los agotados")
    args = ap.parse_args()

    try:
        from weasyprint import HTML
    except ImportError:
        sys.exit("Falta weasyprint: pip install weasyprint")

    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    if not args.salida:
        args.salida = str(RAIZ / ("Catalogo-Adultoyss-Halloween.pdf" if args.tema else "Catalogo-Adultoyss.pdf"))
    global _CARPETA_IMG
    with tempfile.TemporaryDirectory(prefix="catalogo-") as tmp:
        _CARPETA_IMG = Path(tmp)
        contenido = construir_html(args.base, args.todos, args.tema)
        HTML(string=contenido, base_url=str(RAIZ)).write_pdf(args.salida, optimize_images=True)
    tam = Path(args.salida).stat().st_size / 1_000_000
    print(f"Listo: {args.salida} ({tam:.1f} MB)")


if __name__ == "__main__":
    main()
