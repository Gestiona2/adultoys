#!/usr/bin/env python3
"""
Descarga completa del sitio actual de Adultoyss (adultoyssexshopcol.odoo.com).

Deja en insumos/:
  tecnico/html/         HTML crudo de cada pagina del sitemap
  tecnico/catalogo.json productos con precio, sku, categorias, descripcion
  tecnico/categorias.json  arbol/lista de categorias y sus productos
  tecnico/paginas.json  home, contacto, legales y blog (texto + html)
  negocio/*.md          version legible de paginas y blog
  fotos/catalogo/       foto principal de cada producto
  fotos/sitio/          banners e imagenes de las paginas
  marca/                logo

Uso: python3 tools/descargar-sitio.py
Requiere red. No modifica el sitio original.
"""
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

RAIZ = Path(__file__).resolve().parent.parent
INS = RAIZ / "insumos"
BASE = "https://adultoyssexshopcol.odoo.com"
UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126 Safari/537.36"
}
HILOS = 5
REINTENTOS = 3


def pedir(url, binario=False, timeout=45):
    ultimo = None
    for intento in range(REINTENTOS):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                datos = r.read()
                ctype = r.headers.get("Content-Type", "")
            return datos if binario else datos.decode("utf-8", "replace"), ctype
        except Exception as e:  # noqa: BLE001
            ultimo = e
            time.sleep(1.5 * (intento + 1))
    raise ultimo


def limpiar_nombre(texto, maximo=80):
    texto = unescape(texto)
    texto = re.sub(r"[^\w\-]+", "-", texto, flags=re.UNICODE)
    texto = re.sub(r"-{2,}", "-", texto).strip("-_").lower()
    return texto[:maximo] or "sin-nombre"


def extension(ctype, url):
    ctype = (ctype or "").lower()
    if "png" in ctype:
        return ".png"
    if "webp" in ctype:
        return ".webp"
    if "gif" in ctype:
        return ".gif"
    if "svg" in ctype:
        return ".svg"
    if "jpeg" in ctype or "jpg" in ctype:
        return ".jpg"
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    return ext if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg") else ".jpg"


def texto_limpio(nodo):
    if nodo is None:
        return ""
    for t in nodo.find_all(["script", "style", "noscript"]):
        t.decompose()
    lineas = []
    for linea in nodo.get_text("\n", strip=True).split("\n"):
        linea = re.sub(r"[ \t]+", " ", linea).strip()
        if linea and (not lineas or lineas[-1] != linea):
            lineas.append(linea)
    return "\n".join(lineas)


def json_ld(sopa, tipo):
    for sc in sopa.find_all("script", type="application/ld+json"):
        try:
            datos = json.loads(sc.string or "{}")
        except Exception:  # noqa: BLE001
            continue
        for d in datos if isinstance(datos, list) else [datos]:
            if d.get("@type") == tipo:
                return d
    return None


def descargar_imagen(url, destino, vistas):
    url_abs = urllib.parse.urljoin(BASE, url)
    if url_abs in vistas:
        return vistas[url_abs]
    try:
        datos, ctype = pedir(url_abs, binario=True)
    except Exception as e:  # noqa: BLE001
        print(f"  ! imagen fallo {url_abs}: {e}")
        vistas[url_abs] = None
        return None
    destino = destino.with_suffix(extension(ctype, url_abs))
    if not destino.exists() or destino.stat().st_size < len(datos):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(datos)
    vistas[url_abs] = destino
    return destino


def extraer_producto(url, html_crudo, vistas):
    s = BeautifulSoup(html_crudo, "html.parser")
    ld = json_ld(s, "Product") or {}
    bc = json_ld(s, "BreadcrumbList") or {}

    h1 = s.find("h1")
    nombre = (ld.get("name") or (h1.get_text(" ", strip=True) if h1 else "")).strip()

    precio = None
    nodo_precio = s.select_one(".oe_price")
    if nodo_precio:
        precio = nodo_precio.get_text(" ", strip=True)
    precio_antes = None
    nodo_antes = s.select_one(".oe_default_price")
    if nodo_antes and not nodo_antes.get("class", []) == ["d-none"]:
        precio_antes = nodo_antes.get_text(" ", strip=True)

    oferta = ld.get("offers") or {}
    if isinstance(oferta, list):
        oferta = oferta[0] if oferta else {}

    desc_nodo = s.select_one(
        ".o_wsale_product_details_content_section_title .oe_structure"
    )
    descripcion_html = desc_nodo.decode_contents().strip() if desc_nodo else ""
    descripcion = texto_limpio(desc_nodo)

    migas = []
    for it in bc.get("itemListElement", []):
        item = it.get("item", {})
        nombre_miga = it.get("name") or (item.get("name") if isinstance(item, dict) else None)
        if nombre_miga:
            migas.append(nombre_miga)

    categorias = []
    for a in s.select(".o_product_tags a, .o_wsale_product_details_content_section_title .badge"):
        t = a.get_text(" ", strip=True)
        if t and t not in categorias:
            categorias.append(t)
    for m in migas:
        if m and m not in categorias and m.lower() not in ("todos los productos", "products", "productos"):
            categorias.append(m)

    # El JSON-LD del sitio apunta a https://Www.com (dominio de relleno de Odoo),
    # asi que se normaliza contra el dominio real y se prefiere la imagen del HTML.
    imagen_ld = ld.get("image") or ""
    if isinstance(imagen_ld, list):
        imagen_ld = imagen_ld[0] if imagen_ld else ""
    imagen_ld = re.sub(r"^https?://(www\.)?Www\.com", BASE, imagen_ld, flags=re.I)
    img = s.select_one(".o-carousel-product img, .product_detail img")
    if img and img.get("src") and "product.product" in img["src"]:
        imagen_ld = urllib.parse.urljoin(BASE, img["src"])
    if not imagen_ld:
        img = s.select_one(".o-carousel-product img, .product_detail img")
        if img and img.get("src"):
            imagen_ld = urllib.parse.urljoin(BASE, img["src"])

    sku = ld.get("sku") or ""
    gtin = ld.get("gtin") or ""
    if not sku:
        m = re.match(r"(\d+-[a-z]+-\d+)", urllib.parse.urlparse(url).path.strip("/").split("/")[-1], re.I)
        if m:
            sku = m.group(1).upper()
    product_id = None
    m = re.search(r"/image/product\.product/(\d+)/", imagen_ld)
    if m:
        product_id = int(m.group(1))
    if not product_id:
        m = re.search(r"-(\d+)$", urllib.parse.urlparse(url).path)
        if m:
            product_id = int(m.group(1))

    slug = urllib.parse.urlparse(url).path.strip("/").split("/")[-1]
    destino_foto = INS / "fotos" / "catalogo" / f"{sku or product_id}-{limpiar_nombre(nombre)}"
    foto = None
    if imagen_ld:
        foto = descargar_imagen(imagen_ld, destino_foto, vistas)

    imagenes_extra = []
    for img in s.select(".o-carousel-product img, .product_detail img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        src_abs = urllib.parse.urljoin(BASE, src)
        if "product.product" in src_abs and src_abs != imagen_ld:
            imagenes_extra.append(src_abs)

    return {
        "url": url,
        "slug": slug,
        "odoo_id": product_id,
        "nombre": nombre,
        "sku": sku,
        "gtin": gtin,
        "precio_texto": precio,
        "precio": oferta.get("price"),
        "moneda": oferta.get("priceCurrency", "COP"),
        "disponible": "InStock" in str(oferta.get("availability", "")),
        "precio_antes": precio_antes,
        "categoria_principal": migas[0] if migas else None,
        "migas": migas,
        "categorias": categorias,
        "descripcion": descripcion,
        "descripcion_html": descripcion_html,
        "imagen": str(foto.relative_to(RAIZ)) if foto else None,
        "imagen_url": imagen_ld,
        "imagenes_extra": sorted(set(imagenes_extra)),
        "imagenes_descripcion": [],
    }


def extraer_categoria(url, html_crudo, por_slug=None):
    s = BeautifulSoup(html_crudo, "html.parser")
    nombre = None
    h1 = s.find("h1")
    if h1:
        nombre = h1.get_text(" ", strip=True)
    if not nombre or nombre.lower() in ("products", "productos", "tienda"):
        nodo = s.select_one(".o_wsale_products_page_title, .breadcrumb-item.active")
        if nodo:
            nombre = nodo.get_text(" ", strip=True)

    productos = []
    for it in s.select(".oe_product"):
        for a in it.find_all("a", href=True):
            href = urllib.parse.urljoin(BASE, a["href"])
            if "/shop/" not in href or "/category/" in href:
                continue
            cola = href.rstrip("/").split("/")[-1]
            # las grillas de categoria anteponen la categoria a la URL canonica
            canonica = (por_slug or {}).get(cola, href if href.count("/") == 5 else None)
            if canonica and canonica not in productos:
                productos.append(canonica)

    paginas = []
    for a in s.select(".pagination a, .page-link"):
        href = a.get("href")
        if href:
            href = urllib.parse.urljoin(BASE, href)
            if "/page/" in href and href not in paginas:
                paginas.append(href)

    total = None
    m = re.search(r"(\d+)\s+resultado", s.get_text(" ", strip=True))
    if m:
        total = int(m.group(1))

    return {
        "url": url,
        "slug": urllib.parse.urlparse(url).path.strip("/").split("/")[-1],
        "nombre": nombre,
        "total_sitio": total,
        "productos": productos,
        "paginas": paginas,
    }


def extraer_pagina(url, html_crudo, vistas, prefijo):
    s = BeautifulSoup(html_crudo, "html.parser")
    titulo = s.title.get_text(strip=True) if s.title else url
    desc = s.find("meta", attrs={"name": "description"})
    desc = desc.get("content") if desc else ""

    for t in s(["script", "style", "noscript", "header", "footer"]):
        t.decompose()

    principal = (
        s.select_one("main")
        or s.select_one("#wrap")
        or s.select_one(".oe_website_sale")
        or s.body
    )
    texto = texto_limpio(principal)

    imagenes = []
    for i, img in enumerate(s.find_all(["img", "source"])):
        src = img.get("src") or img.get("data-src") or img.get("srcset")
        if not src:
            continue
        src = src.split(",")[0].strip().split(" ")[0]
        if "/web/image/" not in src and not src.startswith("/web"):
            continue
        src = urllib.parse.urljoin(BASE, src)
        if any(x in src for x in ("/logo/", "wikimedia")):
            continue
        imagenes.append(src)

    for el in s.find_all(style=True):
        m = re.search(r"url\(['\"]?([^'\")]+)", el["style"])
        if m and "/web/image/" in m.group(1):
            imagenes.append(urllib.parse.urljoin(BASE, m.group(1)))

    guardadas = []
    vistas_locales = set()
    for src in imagenes:
        if src in vistas_locales:
            continue
        vistas_locales.add(src)
        nombre = limpiar_nombre(urllib.parse.unquote(Path(urllib.parse.urlparse(src).path).name), 70)
        destino = INS / "fotos" / "sitio" / f"{prefijo}-{nombre}"
        ruta = descargar_imagen(src, destino, vistas)
        if ruta:
            guardadas.append(str(ruta.relative_to(RAIZ)))

    return {
        "url": url,
        "titulo": titulo,
        "descripcion_meta": desc,
        "texto": texto,
        "imagenes": guardadas,
        "html": principal.decode_contents() if principal else "",
    }


def markdown_pagina(pagina):
    lineas = [f"# {pagina['titulo']}", "", f"Fuente: {pagina['url']}", ""]
    if pagina.get("descripcion_meta"):
        lineas += [f"> {pagina['descripcion_meta']}", ""]
    lineas += [pagina["texto"], ""]
    return "\n".join(lineas)


def main():
    for d in ("negocio/blog", "negocio/paginas", "tecnico/html", "fotos/catalogo", "fotos/sitio", "marca"):
        (INS / d).mkdir(parents=True, exist_ok=True)

    sitemap, _ = pedir(f"{BASE}/sitemap.xml")
    (INS / "tecnico" / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    try:
        robots, _ = pedir(f"{BASE}/robots.txt")
        (INS / "tecnico" / "robots.txt").write_text(robots, encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    urls = re.findall(r"<loc>(.*?)</loc>", sitemap)
    productos_url = [u for u in urls if "/shop/" in u and "/category/" not in u]
    categorias_url = [u for u in urls if "/shop/category/" in u]
    blog_url = [u for u in urls if "/blog/" in u and not u.endswith("/feed")]
    otras_url = [u for u in urls if u not in productos_url + categorias_url + blog_url]

    print(f"sitemap: {len(urls)} urls · {len(productos_url)} productos · "
          f"{len(categorias_url)} categorias · {len(blog_url)} blog · {len(otras_url)} paginas")

    html_cache = {}

    def bajar(url):
        destino = INS / "tecnico" / "html" / (
            limpiar_nombre(urllib.parse.urlparse(url).path.strip("/").replace("/", "-"), 120) + ".html"
        )
        if destino.exists() and destino.stat().st_size > 2000:
            return url, destino.read_text(encoding="utf-8", errors="replace")
        html_crudo, _ = pedir(url)
        destino.write_text(html_crudo, encoding="utf-8")
        return url, html_crudo

    todas = productos_url + categorias_url + blog_url + otras_url
    with ThreadPoolExecutor(max_workers=HILOS) as pool:
        futuros = {pool.submit(bajar, u): u for u in todas}
        for i, fut in enumerate(as_completed(futuros), 1):
            u = futuros[fut]
            try:
                _, html_crudo = fut.result()
                html_cache[u] = html_crudo
            except Exception as e:  # noqa: BLE001
                print(f"  ! pagina fallo {u}: {e}")
            if i % 25 == 0 or i == len(todas):
                print(f"  paginas {i}/{len(todas)}")

    vistas = {}
    productos = []
    from threading import Lock

    bloqueo = Lock()
    con_cache = [u for u in productos_url if u in html_cache]

    def procesar_producto(u):
        try:
            return extraer_producto(u, html_cache[u], vistas)
        except Exception as e:  # noqa: BLE001
            print(f"  ! producto fallo {u}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=HILOS) as pool:
        futuros = {pool.submit(procesar_producto, u): u for u in con_cache}
        for i, fut in enumerate(as_completed(futuros), 1):
            r = fut.result()
            if r:
                productos.append(r)
            if i % 50 == 0 or i == len(con_cache):
                print(f"  productos {i}/{len(con_cache)}")
    productos.sort(key=lambda p: p["nombre"])

    por_slug = {u.rstrip("/").split("/")[-1]: u for u in productos_url}

    # Las grillas muestran 20 por pagina: hay que seguir la paginacion de cada
    # categoria o la membresia queda incompleta (lenceria, por ejemplo, tiene 84).
    extra_cat = set()
    for u in categorias_url:
        if u not in html_cache:
            continue
        try:
            c = extraer_categoria(u, html_cache[u], por_slug)
            extra_cat.update(p for p in c["paginas"] if p not in html_cache)
        except Exception:  # noqa: BLE001
            pass
    if extra_cat:
        print(f"  paginacion de categorias: {len(extra_cat)} paginas extra")
        with ThreadPoolExecutor(max_workers=HILOS) as pool:
            futuros = {pool.submit(bajar, u): u for u in extra_cat}
            for fut in as_completed(futuros):
                try:
                    u2, html2 = fut.result()
                    html_cache[u2] = html2
                except Exception as e:  # noqa: BLE001
                    print(f"  ! paginacion fallo: {e}")

    categorias = []
    for u in categorias_url:
        if u not in html_cache:
            continue
        try:
            base = extraer_categoria(u, html_cache[u], por_slug)
            vistos = list(base["productos"])
            paginas_extra = base["paginas"]
            vistas_pag = set()
            cola = list(paginas_extra)
            while cola:
                pu = cola.pop(0)
                if pu in vistas_pag or pu not in html_cache:
                    continue
                vistas_pag.add(pu)
                extra = extraer_categoria(pu, html_cache[pu], por_slug)
                for p in extra["productos"]:
                    if p not in vistos:
                        vistos.append(p)
                for p in extra["paginas"]:
                    if p not in vistas_pag and p not in cola:
                        cola.append(p)
            base["productos"] = vistos
            base["paginas"] = sorted(vistas_pag)
            base.pop("total_sitio", None)
            categorias.append(base)
        except Exception as e:  # noqa: BLE001
            print(f"  ! categoria fallo {u}: {e}")
    categorias.sort(key=lambda c: c["slug"])

    for c in categorias:
        validos = set(c["productos"])
        c["productos"] = [p["url"] for p in productos if p["url"] in validos]
        c["total"] = len(c["productos"])

    # categorias reales por producto segun las paginas de categoria
    por_url = {p["url"]: p for p in productos}
    for c in categorias:
        for pu in c["productos"]:
            if pu in por_url and c["nombre"] not in por_url[pu]["categorias"]:
                por_url[pu]["categorias"].append(c["nombre"])

    paginas = []
    for u in otras_url:
        if u in html_cache:
            try:
                paginas.append(extraer_pagina(u, html_cache[u], vistas, "pagina"))
            except Exception as e:  # noqa: BLE001
                print(f"  ! pagina fallo {u}: {e}")

    blog = []
    for u in blog_url:
        if u in html_cache:
            try:
                blog.append(extraer_pagina(u, html_cache[u], vistas, "blog"))
            except Exception as e:  # noqa: BLE001
                print(f"  ! blog fallo {u}: {e}")

    # logo oficial
    logo_url = f"{BASE}/web/image/website/1/logo/Adultoyss?unique=968baea"
    descargar_imagen(logo_url, INS / "marca" / "logo-adultoyss", vistas)

    (INS / "tecnico" / "catalogo.json").write_text(
        json.dumps(productos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (INS / "tecnico" / "categorias.json").write_text(
        json.dumps(categorias, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (INS / "tecnico" / "paginas.json").write_text(
        json.dumps(paginas + blog, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for p in paginas:
        nombre = limpiar_nombre(urllib.parse.urlparse(p["url"]).path.strip("/") or "inicio", 60)
        (INS / "negocio" / "paginas" / f"{nombre}.md").write_text(markdown_pagina(p), encoding="utf-8")
    for p in blog:
        nombre = limpiar_nombre(urllib.parse.urlparse(p["url"]).path.strip("/").split("/")[-1], 70)
        (INS / "negocio" / "blog" / f"{nombre}.md").write_text(markdown_pagina(p), encoding="utf-8")

    con_foto = sum(1 for p in productos if p["imagen"])
    print("\nLISTO")
    print(f"  productos: {len(productos)} (con foto: {con_foto})")
    print(f"  categorias: {len(categorias)}")
    print(f"  paginas: {len(paginas)} · blog: {len(blog)}")
    print(f"  imagenes de sitio: {len(list((INS / 'fotos' / 'sitio').glob('*')))}")
    print(f"  fotos de catalogo: {len(list((INS / 'fotos' / 'catalogo').glob('*')))}")

    sin_precio = [p["nombre"] for p in productos if not p["precio"]]
    sin_desc = [p["nombre"] for p in productos if not p["descripcion"]]
    sin_foto = [p["nombre"] for p in productos if not p["imagen"]]
    print(f"  sin precio: {len(sin_precio)} · sin descripcion: {len(sin_desc)} · sin foto: {len(sin_foto)}")
    for etiqueta, lista in (("SIN PRECIO", sin_precio), ("SIN DESCRIPCION", sin_desc), ("SIN FOTO", sin_foto)):
        if lista:
            print(f"  {etiqueta}: {', '.join(lista[:15])}{' …' if len(lista) > 15 else ''}")


if __name__ == "__main__":
    main()
