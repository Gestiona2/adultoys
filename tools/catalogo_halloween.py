"""Decoracion de Halloween para el catalogo en PDF (tools/catalogo_pdf.py).

Todo es vectorial (SVG): telaranas, luna con bruja en escoba, murcielagos,
arañas colgando, calabazas, fantasma y caldero. Se crean en una carpeta
temporal al generar el PDF, asi que no hay imagenes que mantener ni que pesen.

Se activa con:  python3 tools/catalogo_pdf.py --tema halloween
"""
import math
from pathlib import Path

NARANJA = "#ff9a3d"


def _svg(ancho, alto, cuerpo, defs="", extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" '
            f'width="{ancho}" height="{alto}" {extra}><defs>{defs}</defs>{cuerpo}</svg>')


def telarana(esquina="tr"):
    """Telaraña en una esquina: radios, anillos y hilos que cuelgan."""
    n, lado = 7, 300
    cx, cy = lado, 0
    radios = [38, 80, 128, 182, 240]
    largo = 292

    def punto(k, r):
        a = math.radians(90 + 15 * k)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    trazos = []
    for k in range(n):
        x, y = punto(k, largo)
        trazos.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke-width="1.5"/>')
    for r in radios:
        for k in range(n - 1):
            x1, y1 = punto(k, r)
            x2, y2 = punto(k + 1, r)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            # el hilo se comba hacia la esquina, como una telaraña real
            qx, qy = cx + (mx - cx) * 0.80, cy + (my - cy) * 0.80
            trazos.append(f'<path d="M{x1:.1f},{y1:.1f} Q{qx:.1f},{qy:.1f} {x2:.1f},{y2:.1f}" fill="none"/>')
    giro = {
        "tr": "",
        "tl": f'transform="translate({lado},0) scale(-1,1)"',
        "br": f'transform="translate(0,{lado}) scale(1,-1)"',
        "bl": f'transform="translate({lado},{lado}) scale(-1,-1)"',
    }[esquina]
    cuerpo = (f'<g {giro} stroke="#ffffff" stroke-opacity="0.42" stroke-width="1.2" fill="none">'
              f'{"".join(trazos)}</g>')
    return _svg(lado, lado, cuerpo)


def arana(hilo=90):
    """Araña colgando de un hilo. `hilo` es el largo del hilo en unidades del dibujo."""
    y = hilo
    patas = []
    for lado in (-1, 1):
        for i, (dx, dy) in enumerate([(26, -16), (32, -4), (32, 8), (26, 18)]):
            x0, y0 = 30 + lado * 6, y + 12 + i * 2.2
            x1, y1 = 30 + lado * dx, y + 12 + dy - 14
            x2, y2 = 30 + lado * (dx + 2), y1 + 22
            patas.append(f'<path d="M{x0},{y0} L{x1},{y1} L{x2},{y2}"/>')
    cuerpo = (
        f'<line x1="30" y1="0" x2="30" y2="{y}" stroke="#ffffff" stroke-opacity="0.55" stroke-width="1"/>'
        f'<g stroke="#a678e0" stroke-width="1.7" fill="none" stroke-linecap="round" stroke-linejoin="round">{"".join(patas)}</g>'
        f'<circle cx="30" cy="{y + 8}" r="5.5" fill="#2d1b45" stroke="#a678e0" stroke-width="1"/>'
        f'<ellipse cx="30" cy="{y + 24}" rx="9" ry="11" fill="#2d1b45" stroke="#a678e0" stroke-width="1"/>'
        f'<path d="M26.5,{y + 20} h7 l-3.5,6 l3.5,6 h-7 l3.5,-6 z" fill="{NARANJA}"/>'
        f'<circle cx="27.6" cy="{y + 7}" r="1.3" fill="#ffd25e"/><circle cx="32.4" cy="{y + 7}" r="1.3" fill="#ffd25e"/>'
    )
    return _svg(60, y + 44, cuerpo)


def murcielago(relleno="#24143a", borde="#a678e0"):
    cuerpo = (
        f'<path d="M50,16 C47,7 44,3 41,8 C37,5 31,7 26,13 C18,10 9,13 0,22 C8,22 13,24 17,31 '
        f'C21,27 27,27 31,33 C35,29 41,29 45,35 L50,27 L55,35 C59,29 65,29 69,33 C73,27 79,27 83,31 '
        f'C87,24 92,22 100,22 C91,13 82,10 74,13 C69,7 63,5 59,8 C56,3 53,7 50,16 Z" '
        f'fill="{relleno}" stroke="{borde}" stroke-width="1.4" stroke-linejoin="round"/>'
        f'<circle cx="46.5" cy="17" r="1.1" fill="#ffd25e"/><circle cx="53.5" cy="17" r="1.1" fill="#ffd25e"/>'
    )
    return _svg(100, 38, cuerpo)


def luna():
    """Luna con halo hecho de círculos translúcidos (los degradados salían apagados en el PDF)."""
    cuerpo = ('<circle cx="110" cy="110" r="108" fill="#ff9a3d" fill-opacity="0.07"/>'
              '<circle cx="110" cy="110" r="98" fill="#ff9a3d" fill-opacity="0.09"/>'
              '<circle cx="110" cy="110" r="89" fill="#ff9a3d" fill-opacity="0.12"/>'
              '<circle cx="110" cy="110" r="80" fill="#ffc861"/>'
              '<circle cx="104" cy="104" r="66" fill="#ffdf8f"/>'
              '<circle cx="98" cy="98" r="48" fill="#fff0bd" fill-opacity="0.85"/>'
              '<g fill="#e9a43f" fill-opacity="0.55"><circle cx="84" cy="90" r="13"/><circle cx="130" cy="74" r="8"/>'
              '<circle cx="136" cy="128" r="16"/><circle cx="92" cy="138" r="7"/></g>')
    return _svg(220, 220, cuerpo)


def bruja(relleno="#0a0610", borde=None):
    """Bruja en escoba, en silueta, volando hacia la derecha.

    Con `borde` se le dibuja un contorno claro: sirve para verla sobre fondos oscuros.
    """
    n = relleno
    contorno = f'stroke="{borde}" stroke-width="1.6" stroke-linejoin="round"' if borde else ""
    cuerpo = (
        f'<g transform="rotate(-9 150 100)" fill="{n}" {contorno}>'
        # palo y cerdas de la escoba
        f'<rect x="22" y="118" width="232" height="6" rx="3"/>'
        f'<path d="M26,121 C12,106 -2,106 -16,98 C-8,111 -14,118 -22,121 C-14,125 -8,132 -16,144 C-2,136 12,136 26,124 Z"/>'
        f'<rect x="26" y="114" width="6" height="14" fill="{NARANJA}"/>'
        # capa que ondea hacia atrás
        f'<path d="M150,98 C124,100 100,114 68,126 C96,134 126,132 154,124 Z"/>'
        # cuerpo
        f'<path d="M130,120 C122,100 130,80 148,72 L172,70 C178,86 174,106 168,120 Z"/>'
        # botas
        f'<path d="M148,118 L146,142 L134,148 L138,155 L156,152 L162,118 Z"/>'
        f'<path d="M160,120 L168,140 L158,150 L164,156 L180,148 L174,118 Z"/>'
        # brazo hacia el palo
        + (f'<path d="M164,80 Q188,92 202,116" fill="none" stroke="{borde}" stroke-width="11" stroke-linecap="round"/>' if borde else "") +
        f'<path d="M164,80 Q188,92 202,116" fill="none" stroke="{n}" stroke-width="8" stroke-linecap="round"/>'
        # pelo, cabeza y nariz
        f'<path d="M160,52 C140,46 122,56 104,50 C120,62 140,66 158,68 Z"/>'
        f'<circle cx="168" cy="57" r="11"/>'
        f'<path d="M177,54 L190,60 L177,64 Z"/>'
        # sombrero
        f'<ellipse cx="166" cy="47" rx="27" ry="6"/>'
        f'<path d="M150,46 C152,30 160,16 176,6 C186,0 196,6 190,11 C178,17 178,33 184,46 Z"/>'
        f'<path d="M153,39 L183,39 L183.6,44 L152.4,44 Z" fill="{NARANJA}"/>'
        f'</g>'
    )
    # el viewBox deja sitio a las cerdas de la escoba, que salen por la izquierda
    return _svg(340, 190, cuerpo).replace('viewBox="0 0 340 190"', 'viewBox="-30 -4 340 190"')


def calabaza(cara=True):
    gajos = ('<ellipse cx="38" cy="66" rx="27" ry="37" fill="#e8651a" stroke="#a83d08" stroke-width="1"/>'
             '<ellipse cx="82" cy="66" rx="27" ry="37" fill="#e8651a" stroke="#a83d08" stroke-width="1"/>'
             '<ellipse cx="60" cy="66" rx="25" ry="39" fill="#f58220" stroke="#a83d08" stroke-width="1"/>'
             '<ellipse cx="56" cy="58" rx="14" ry="26" fill="#ffa63d" fill-opacity="0.55"/>')
    tallo = '<path d="M54,30 C55,16 62,10 70,8 L76,13 C69,17 68,24 68,31 Z" fill="#587d1a" stroke="#3b5610" stroke-width="0.8"/>'
    rostro = ''
    if cara:
        rostro = ('<path d="M36,64 L46,47 L55,64 Z" fill="#ffe27a"/><path d="M65,64 L74,47 L84,64 Z" fill="#ffe27a"/>'
                  '<path d="M36,79 L45,73 L52,82 L60,73 L68,82 L75,73 L84,79 Q60,102 36,79 Z" fill="#ffe27a"/>')
    return _svg(120, 110, gajos + tallo + rostro)


def calabaza_mini():
    """Calabaza chica, de tamaño fijo, para viñetas del menú."""
    return calabaza().replace('width="120" height="110"', 'width="26" height="24"', 1)


def fantasma():
    cuerpo = ('<path d="M10,120 V50 C10,22 28,6 50,6 C72,6 90,22 90,50 V120 L77,108 L63,122 L50,108 L37,122 L23,108 Z" '
              'fill="#f1ecfb" stroke="#9b86c8" stroke-width="1"/>'
              '<ellipse cx="36" cy="50" rx="6" ry="9" fill="#1b1030"/><ellipse cx="64" cy="50" rx="6" ry="9" fill="#1b1030"/>'
              '<ellipse cx="50" cy="78" rx="7" ry="10" fill="#1b1030"/>')
    return _svg(100, 130, cuerpo)


def caldero():
    cuerpo = ('<g stroke="#a678e0" stroke-width="1.4">'
              '<path d="M34,98 L26,116 M106,98 L114,116" fill="none" stroke-linecap="round" stroke-width="3"/>'
              '<path d="M20,40 C8,72 22,104 70,104 C118,104 132,72 120,40 Z" fill="#1c1228"/>'
              '<ellipse cx="70" cy="40" rx="52" ry="11" fill="#0f0a18"/></g>'
              '<ellipse cx="70" cy="40" rx="45" ry="7.5" fill="#6df03c"/>'
              '<g fill="#8cf55e"><circle cx="54" cy="28" r="5"/><circle cx="80" cy="20" r="7.5"/>'
              '<circle cx="98" cy="31" r="4"/><circle cx="66" cy="10" r="3"/></g>')
    return _svg(140, 122, cuerpo)


# ---------------------------------------------------------------- activos
def crear_activos(carpeta):
    """Escribe los SVG en `carpeta` y devuelve {nombre: uri}."""
    carpeta = Path(carpeta)
    piezas = {
        "web-tr": telarana("tr"), "web-tl": telarana("tl"),
        "web-br": telarana("br"), "web-bl": telarana("bl"),
        "arana": arana(90), "arana-corta": arana(40),
        "murcielago": murcielago(), "luna": luna(), "bruja": bruja(),
        "calabaza": calabaza(), "calabaza-mini": calabaza_mini(),
        "fantasma": fantasma(), "caldero": caldero(),
    }
    uris = {}
    for nombre, svg in piezas.items():
        ruta = carpeta / f"hw-{nombre}.svg"
        ruta.write_text(svg, encoding="utf-8")
        uris[nombre] = ruta.as_uri()
    return uris


def css(a):
    """Estilos que se suman a los del catalogo normal."""
    return f"""
/* ===== Edición Halloween ===== */
@page contenido {{
  @bottom-left {{ content: "ADULTOYSS · EDICIÓN HALLOWEEN"; font: 600 7pt Inter; letter-spacing: .14em; color: #ff9a3d; }}
}}
.etiqueta, .tarjeta-sub {{ color: {NARANJA}; }}
.tarjeta {{ border-color: rgba(255,140,40,.30); }}
.tarjeta-precio {{ color: #ffb866; }}
.cat-cabeza {{ border-bottom-color: rgba(255,140,40,.40); position: relative; }}
.cat-deco {{ position: absolute; right: 14mm; top: -1mm; height: 17mm; }}
.cat-deco-murci {{ position: absolute; right: 36mm; top: 4mm; width: 13mm; }}
.boton {{ background: #e0560c; }}
/* Adornos de cada página: detrás del contenido, anclados a las esquinas de la hoja. */
.hw-pagina {{ position: absolute; z-index: -1; }}
.menu-ayuda {{ border-color: rgba(255,140,40,.45); }}
.menu-fila::after {{ color: {NARANJA}; }}
.menu-fila::before {{ content: url({a['calabaza-mini']}); margin-right: 4mm; align-self: center; }}
.volver a {{ color: {NARANJA}; }}

/* portada */
.portada {{ background: linear-gradient(180deg, #0b0516 0%, #1a0b2e 52%, #3d1606 100%); }}
.hw {{ position: absolute; }}
.portada h1 span {{ color: {NARANJA}; }}
.portada-etiqueta {{ color: {NARANJA}; margin-top: 52mm; }}
.portada-boton {{ background: #e0560c; }}
.portada-boton-wa {{ background: #17a34a; }}

/* contraportada */
.cierre {{ position: relative; padding-top: 26mm; }}
.cierre-escena {{ position: relative; height: 66mm; margin: 4mm auto 0; width: 150mm; }}
.cierre-escena img {{ position: absolute; }}
.cierre h2 {{ color: #fff; margin-top: 8mm; font-size: 24pt; }}
.cierre small {{ margin-top: 16mm !important; }}
.cierre h2 span {{ color: {NARANJA}; }}
"""


def portada(a, logo, fecha, cifra, base, enlace_wa, wa_visible, esc):
    """HTML de la portada: luna, bruja, murciélagos, arañas, telarañas y calabazas."""
    return f"""
<section class="portada">
  <img class="hw" style="left:104mm; top:6mm; width:106mm;" src="{a['luna']}" alt="">
  <img class="hw" style="left:108mm; top:26mm; width:100mm;" src="{a['bruja']}" alt="">
  <img class="hw" style="left:0; top:0; width:80mm;" src="{a['web-tl']}" alt="">
  <img class="hw" style="right:0; bottom:0; width:92mm;" src="{a['web-br']}" alt="">
  <img class="hw" style="left:70mm; top:0; width:11mm;" src="{a['arana']}" alt="">
  <img class="hw" style="left:184mm; top:0; width:9mm;" src="{a['arana-corta']}" alt="">
  <img class="hw" style="left:84mm; top:56mm; width:20mm;" src="{a['murcielago']}" alt="">
  <img class="hw" style="left:140mm; top:90mm; width:15mm;" src="{a['murcielago']}" alt="">
  <img class="hw" style="left:56mm; top:84mm; width:11mm;" src="{a['murcielago']}" alt="">
  <img class="hw" style="left:176mm; top:92mm; width:18mm;" src="{a['murcielago']}" alt="">
  <img class="hw" style="left:150mm; top:224mm; width:46mm;" src="{a['calabaza']}" alt="">
  <img class="hw" style="left:118mm; top:244mm; width:34mm;" src="{a['calabaza']}" alt="">
  <img class="hw" style="left:184mm; top:250mm; width:22mm;" src="{a['calabaza']}" alt="">
  <div class="portada-contenido">
    <img class="portada-logo" src="{logo}" alt="Adultoyss, tienda erótica">
    <p class="portada-etiqueta">CATÁLOGO · EDICIÓN HALLOWEEN · {esc(fecha.upper())}</p>
    <h1>Esta noche,<br><span>conjura tu deseo.</span></h1>
    <p class="portada-texto">Juguetes, lencería y bienestar íntimo seleccionados para explorar sin juicios.
      Empaque neutro y atención por WhatsApp.</p>
    <p class="portada-cifra"><strong>{cifra}</strong> productos disponibles</p>
    <div class="portada-pie">
      <a class="portada-boton" href="{base}">Visitar la tienda web</a>
      <a class="portada-boton portada-boton-wa" href="{enlace_wa}">WhatsApp {esc(wa_visible)}</a>
      <p>Contenido exclusivo para mayores de 18 años.</p>
    </div>
  </div>
</section>"""


def cierre(a, logo, base, enlace_wa, wa_visible, esc):
    return f"""
<section class="cierre">
  <img class="cierre-logo" src="{logo}" alt="Adultoyss">
  <div class="cierre-escena" aria-hidden="true">
    <img style="left:34mm; top:24mm; width:46mm;" src="{a['caldero']}" alt="">
    <img style="left:0; top:12mm; width:30mm;" src="{a['fantasma']}" alt="">
    <img style="left:118mm; top:26mm; width:34mm;" src="{a['calabaza']}" alt="">
    <img style="left:76mm; top:-12mm; width:64mm;" src="{a['luna']}" alt="">
    <img style="left:66mm; top:-2mm; width:84mm;" src="{a['bruja']}" alt="">
    <img style="left:20mm; top:-6mm; width:16mm;" src="{a['murcielago']}" alt="">
    <img style="left:132mm; top:-2mm; width:12mm;" src="{a['murcielago']}" alt="">
  </div>
  <h2>¡Feliz Halloween!<br><span>Que sea una noche inolvidable.</span></h2>
  <p>Compra en la web o escríbenos por WhatsApp. Te asesoramos con discreción.</p>
  <p><a class="portada-boton" href="{base}">Ir a la tienda web</a>
     <a class="portada-boton portada-boton-wa" href="{enlace_wa}">WhatsApp {esc(wa_visible)}</a></p>
  <small>Precios y disponibilidad sujetos a cambio. Producto para mayores de 18 años. Este catálogo
    es informativo y no reemplaza la consulta con un profesional de la salud.</small>
</section>"""


def decoracion_pagina(a, derecha):
    """Telaraña, araña y murciélago en las esquinas de la hoja.

    Las coordenadas son relativas al área de contenido: los márgenes de la hoja
    son 12 mm a los lados y 16 mm arriba, 18 mm abajo. Las hojas impares quedan
    a la derecha y llevan la telaraña grande en esa esquina; las pares, a la izquierda.
    """
    if derecha:
        grande = f'<img class="hw-pagina" style="right:-12mm; top:-16mm; width:50mm;" src="{a["web-tr"]}" alt="">'
        chica = f'<img class="hw-pagina" style="left:-12mm; bottom:-18mm; width:26mm;" src="{a["web-bl"]}" alt="">'
        arana = f'<img class="hw-pagina" style="left:150mm; top:-16mm; width:11mm;" src="{a["arana"]}" alt="">'
        bicho = f'<img class="hw-pagina" style="left:112mm; top:-11mm; width:14mm;" src="{a["murcielago"]}" alt="">'
    else:
        grande = f'<img class="hw-pagina" style="left:-12mm; top:-16mm; width:50mm;" src="{a["web-tl"]}" alt="">'
        chica = f'<img class="hw-pagina" style="right:-12mm; bottom:-18mm; width:26mm;" src="{a["web-br"]}" alt="">'
        arana = f'<img class="hw-pagina" style="left:150mm; top:-16mm; width:11mm;" src="{a["arana"]}" alt="">'
        bicho = f'<img class="hw-pagina" style="left:96mm; top:-11mm; width:14mm;" src="{a["murcielago"]}" alt="">'
    return grande + chica + arana + bicho
