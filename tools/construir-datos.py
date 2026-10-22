#!/usr/bin/env python3
"""Convierte lo descargado del sitio anterior en el catalogo del sitio nuevo.

    python3 tools/construir-datos.py

Lee `insumos/tecnico/catalogo.json` y `categorias.json`, limpia nombres y
descripciones, agrupa las 55 categorias sueltas en grupos de navegacion y
escribe:

    src/datos/productos.json     catalogo que usa el sitio
    src/datos/categorias.json    grupos + tipos, con conteos
    src/datos/_fuentes.json      que foto original corresponde a cada slug

El archivo `_fuentes.json` lo usa tools/preparar-imagenes.mjs y no se publica.

Reglas que aplica:
  - Los productos sin precio (42 en el sitio anterior) quedan con `oculto:
    true`: no aparecen en el sitio ni en el buscador, pero siguen en el Excel
    para que el dueno les ponga precio.
  - Los agotados si se publican, marcados como agotados: son buenos para SEO.
  - El descuento no se escribe a mano: se calcula de precio y precio_antes.
  - Si un producto no trae descripcion, se escribe una neutra por grupo. Nunca
    se inventan propiedades, materiales ni beneficios medicos.
"""
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "insumos" / "tecnico" / "catalogo.json"
DESTINO = RAIZ / "src" / "datos"
FUENTES = DESTINO / "_fuentes.json"

# ---------------------------------------------------------------------------
# Grupos de navegacion. El orden es el que se ve en el menu y en la portada.
# ---------------------------------------------------------------------------
GRUPOS = [
    {
        "id": "vibradores",
        "nombre": "Vibradores y succionadores",
        "corto": "Vibradores",
        "icono": "vibrador",
        "orden": 1,
        "descripcion": "Estimulación externa e interna, succionadores y juguetes con app.",
        "imagen": "sitio/categoria-vibradores",
    },
    {
        "id": "dildos",
        "nombre": "Dildos y plugs",
        "corto": "Dildos y plugs",
        "icono": "dildo",
        "orden": 2,
        "descripcion": "Formas, tamaños y materiales para descubrir qué te gusta.",
        "imagen": "sitio/categoria-dildos",
    },
    {
        "id": "parejas",
        "nombre": "Para parejas",
        "corto": "Parejas",
        "icono": "parejas",
        "orden": 3,
        "descripcion": "Juegos, anillos y accesorios para sumar complicidad.",
        "imagen": "sitio/categoria-parejas",
    },
    {
        "id": "lenceria",
        "nombre": "Lencería y disfraces",
        "corto": "Lencería",
        "icono": "lenceria",
        "orden": 4,
        "descripcion": "Lencería, disfraces y medias para sentirte como quieras.",
        "imagen": "sitio/categoria-lenceria",
    },
    {
        "id": "lubricantes",
        "nombre": "Lubricantes y cosméticos",
        "corto": "Lubricantes",
        "icono": "gota",
        "orden": 5,
        "descripcion": "Lubricantes, aceites, feromonas y cuidado íntimo.",
        "imagen": "sitio/categoria-lubricantes",
    },
    {
        "id": "salud",
        "nombre": "Salud sexual",
        "corto": "Salud sexual",
        "icono": "potencia",
        "orden": 6,
        "descripcion": "Potenciadores, retardantes y bienestar para tu vida íntima.",
        "imagen": "sitio/categoria-salud",
    },
    {
        "id": "sado",
        "nombre": "Sado y fetish",
        "corto": "Sado",
        "icono": "esposas",
        "orden": 7,
        "descripcion": "Juego de roles, bondage y sensaciones intensas con consentimiento.",
        "imagen": "sitio/categoria-sado",
    },
    {
        "id": "higiene",
        "nombre": "Higiene y cuidado",
        "corto": "Higiene",
        "icono": "escudo",
        "orden": 8,
        "descripcion": "Preservativos, limpieza y accesorios para cuidar tus juguetes.",
        "imagen": "sitio/categoria-higiene",
    },
    {
        "id": "weed",
        "nombre": "WEED y accesorios",
        "corto": "WEED",
        "icono": "hoja",
        "orden": 9,
        "descripcion": "Papeles, pipas y accesorios para tu ritual. Solo mayores de 18.",
        "imagen": "sitio/categoria-weed",
    },
    {
        "id": "otros",
        "nombre": "Otros",
        "corto": "Otros",
        "icono": "regalo",
        "orden": 10,
        "descripcion": "Tarjetas de regalo y accesorios especiales.",
        "imagen": "sitio/categoria-otros",
    },
]

SUBCATEGORIA_GRUPO = {
    "JUGUETE/VIBRADOR": "vibradores",
    "BALAS": "vibradores",
    "HUEVOS": "vibradores",
    "SUCCIONADOR": "vibradores",
    "SATISFYER": "vibradores",
    "SIMILARES SATISFYER": "vibradores",
    "VIBRADORES LIQUIDOS": "vibradores",
    "JUGUETES APP": "vibradores",
    "MASAJEADOR": "vibradores",
    "MASTURBADORES": "vibradores",
    "MASTURBADORES ELLOS": "vibradores",
    "FUNDAS": "vibradores",
    "DILDOS": "dildos",
    "DILDO MANUAL": "dildos",
    "PLUG": "dildos",
    "BOLAS ANALES": "dildos",
    "ARNES": "dildos",
    "ANILLOS": "parejas",
    "JUEGO MESA": "parejas",
    "LENCERIA": "lenceria",
    "LENCERIA ARNES": "lenceria",
    "LENCERIA HOMBRE": "lenceria",
    "MALLAS": "lenceria",
    "MEDIAS": "lenceria",
    "MEDIAS LIGUERO": "lenceria",
    "PANTIS": "lenceria",
    "PIJAMAS SEXYS": "lenceria",
    "DISFRAZ": "lenceria",
    "DIADEMAS HALLOWEN TEMATICAS": "lenceria",
    "TRAJE DE BAÑO": "lenceria",
    "FAJAS CUERPO BARBY": "lenceria",
    "ANTIFAS": "lenceria",
    "GUANTES": "lenceria",
    "LUBRICANTES": "lubricantes",
    "LUBRICANTES ANALES": "lubricantes",
    "LUBRICANTES ESTRECHANTES": "lubricantes",
    "LUBRICANTES MULTIORGASMOS": "lubricantes",
    "LUBRICANTES SEN": "lubricantes",
    "COSMETICOS": "lubricantes",
    "COMESTIBLE": "lubricantes",
    "PHEROMONAS": "lubricantes",
    "VELAS": "lubricantes",
    "ESTRECHANTES": "lubricantes",
    "MULTIORGASMOS": "lubricantes",
    "POTENCIADORES": "salud",
    "RETARDANTES": "salud",
    "VOLUMINIZADORES": "salud",
    "SADO": "sado",
    "HIGIENE": "higiene",
    "PRESERVATIVOS": "higiene",
    "PILAS": "higiene",
    "REPUESTOS": "higiene",
    "WEED": "weed",
    "BOLSAS": "higiene",
    "WEBCAM": "otros",
    "TARJETA DE REGALO": "otros",
}

# Productos que el sitio anterior dejo sin categoria o dentro de GENERAL. Se
# clasifican por nombre, que es lo unico que hay. Cambiar aqui si el dueno
# corrige la categoria en el Excel.
CASOS_ESPECIALES = {
    "ANILLO DOBLE/RETARDANTE DOUBLE TAYLOR.": "ANILLOS",
    "BOLAS ANALES BEADS": "BOLAS ANALES",
    "BOLSAS GRISES METALICAS": "HIGIENE",
    "KIT SADO X3 BONDAGE": "SADO",
    "OMEGA 3 CAPSULAS": "POTENCIADORES",
    "TUMBA K3 500 ML - IMPRO NATURAL": "POTENCIADORES",
    "VIBRADOR CAT APP": "JUGUETES APP",
    "ZOLIQUE TOP DE MUJER ROJO FLORAL DE VERANO SEXY Y CHIC.": "LENCERIA",
    "BABAYDOLL RUBI LINDA": "LENCERIA",
    "BABYDOLL CORAZON ROJO": "LENCERIA",
    "COLEGIALA DULCE": "DISFRAZ",
    "PLEASURE MULTI ORGASMO": "MULTIORGASMOS",
    "TARJETA DE REGALO": "TARJETA DE REGALO",
}

NOMBRES_SUB = {
    "ANILLOS": "Anillos",
    "ANTIFAS": "Antifaces",
    "ARNES": "Arneses",
    "BALAS": "Balas vibradoras",
    "BOLSAS": "Bolsas",
    "BOLAS ANALES": "Bolas anales",
    "COMESTIBLE": "Comestibles",
    "COSMETICOS": "Cosméticos",
    "DIADEMAS HALLOWEN TEMATICAS": "Diademas Halloween",
    "DILDO MANUAL": "Dildos manuales",
    "DILDOS": "Dildos",
    "DISFRAZ": "Disfraces",
    "ESTRECHANTES": "Estrechantes",
    "FAJAS CUERPO BARBY": "Fajas",
    "FUNDAS": "Fundas",
    "GENERAL": "General",
    "GUANTES": "Guantes",
    "HIGIENE": "Higiene",
    "HUEVOS": "Huevos vibradores",
    "JUEGO MESA": "Juegos de mesa",
    "JUGUETE/VIBRADOR": "Juguetes y vibradores",
    "JUGUETES APP": "Juguetes con app",
    "LENCERIA": "Lencería",
    "LENCERIA ARNES": "Lencería arnés",
    "LENCERIA HOMBRE": "Lencería para hombre",
    "LUBRICANTES": "Lubricantes",
    "LUBRICANTES ANALES": "Lubricantes anales",
    "LUBRICANTES ESTRECHANTES": "Lubricantes estrechantes",
    "LUBRICANTES MULTIORGASMOS": "Lubricantes multiorgasmos",
    "LUBRICANTES SEN": "Lubricantes Sen",
    "MALLAS": "Mallas",
    "MASAJEADOR": "Masajeadores",
    "MASTURBADORES": "Masturbadores",
    "MASTURBADORES ELLOS": "Masturbadores para él",
    "MEDIAS": "Medias",
    "MEDIAS LIGUERO": "Medias ligueros",
    "MULTIORGASMOS": "Multiorgasmos",
    "PANTIS": "Pantis",
    "PHEROMONAS": "Feromonas",
    "PIJAMAS SEXYS": "Pijamas sexys",
    "PILAS": "Pilas",
    "PLUG": "Plugs",
    "POTENCIADORES": "Potenciadores",
    "PRESERVATIVOS": "Preservativos",
    "REPUESTOS": "Repuestos",
    "RETARDANTES": "Retardantes",
    "SADO": "Sado",
    "SATISFYER": "Satisfyer",
    "SIMILARES SATISFYER": "Similares a Satisfyer",
    "SUCCIONADOR": "Succionadores",
    "TARJETA DE REGALO": "Tarjetas de regalo",
    "TRAJE DE BAÑO": "Trajes de baño",
    "VELAS": "Velas",
    "VIBRADORES LIQUIDOS": "Vibradores líquidos",
    "VOLUMINIZADORES": "Voluminizadores",
    "WEBCAM": "Webcam",
    "WEED": "WEED",
}

MARCAS = [
    "Satisfyer", "Satisfayer", "Blix", "Xbull", "Rino", "Stud", "Apolos",
    "KLG", "Sen", "Today", "Mero Macho", "Full Power", "Bull Max", "B-Chota",
    "Tumba K3", "Omega 3", "Furunbao", "Shilajit", "Black Power", "Power XS",
    "Handsome Up", "Yesain", "Zeus", "Love Buzz", "Funny Egg", "Afrodita",
]

# Palabras que se quedan como estan al pasar un nombre de mayusculas a frase.
PRESERVAR = {
    "KLG", "BLIX", "XBULL", "RINO", "STUD", "SEN", "WEED", "CBD", "THC",
    "XL", "XXL", "XXX", "BDSM", "USB", "APP", "K3", "F7", "SATISFYER",
    "SATISFAYER", "TODAY", "KING", "COCK", "G", "ML", "CM", "CAP", "CAPS",
    "PINK", "BLUE", "RED", "GOLD", "TURBO", "TOUCH",
}

CONECTORES = {"de", "del", "la", "el", "los", "las", "y", "o", "u", "con", "sin", "para", "por", "en", "a", "al", "x"}

DESCRIPCIONES = {
    "vibradores": (
        "Diseñado para explorar nuevas sensaciones con comodidad y discreción. "
        "Su forma y textura están pensadas para un uso fácil, seguro y placentero, "
        "solo o en pareja."
    ),
    "dildos": (
        "Una pieza para descubrir el placer a tu ritmo. Diseño ergonómico y "
        "superficie de fácil limpieza para que te concentres en lo que sientes."
    ),
    "parejas": (
        "Un accesorio pensado para sumar complicidad y nuevas experiencias en "
        "pareja. Fácil de usar, discreto y listo para tu momento."
    ),
    "lenceria": (
        "Una pieza que combina comodidad y seducción para sentirte segura y "
        "deseada. Tejidos suaves y un diseño pensado para realzar tu figura."
    ),
    "lubricantes": (
        "Textura sedosa que acompaña el juego íntimo y ayuda a que todo fluya con "
        "más comodidad. Revisa las indicaciones del fabricante antes de usar."
    ),
    "salud": (
        "Un aliado para tu bienestar íntimo. Úsalo según las indicaciones del "
        "fabricante y consulta a un profesional si tienes dudas."
    ),
    "sado": (
        "Un accesorio para explorar el juego de roles y las sensaciones intensas "
        "con confianza y consentimiento. Diseño resistente y fácil de incorporar."
    ),
    "higiene": (
        "Pensado para cuidar tu intimidad y mantener tus productos en buen estado. "
        "Práctico, discreto y fácil de usar."
    ),
    "weed": (
        "Un accesorio para tu ritual de bienestar. Uso exclusivo para mayores de "
        "18 años; revisa la normativa local antes de comprar."
    ),
    "otros": (
        "Un producto seleccionado para complementar tu experiencia. Escríbenos por "
        "WhatsApp si quieres más detalles antes de comprar."
    ),
}

RECOMENDADOS = {
    "satisfyer-pro-2",
    "succionador-galaku",
    "bala-faire-app",
    "dildo-david",
    "arnes-dalias",
    "lubricante-multi-frio-calor-sen-intimo",
    "preservativos-today-x3",
    "fantasia-erotica",
    "anillo-vibrador-bunny-ring-blue",
    "cerdito-lamedor-pink-con-lengua",
    "babydoll-encaje-dorado",
    "huevo-remote-control-egg",
}

TITULOS_ESPECIALES = {
    "SATISFAYER PRO 2": "Satisfyer Pro 2",
    "SUBCIONADOR GALAKU": "Succionador Galaku",
    "FANTASIA EROTICA": "Fantasía Erótica",
    "ARNES DALIAS": "Arnés Dalias",
    "LENCERIA 75000": "Babydoll Encaje Dorado",
}

ACENTOS = {
    "Lenceria": "Lencería",
    "lenceria": "lencería",
    "Capsulas": "Cápsulas",
    "capsulas": "cápsulas",
}

CIFRA = re.compile(r"^\d+([.,]\d+)?$")


def sin_tildes(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def a_slug(texto):
    texto = sin_tildes(texto or "").lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return re.sub(r"-{2,}", "-", texto)


def limpiar(texto):
    texto = (texto or "").replace("\u200b", "").replace("\ufeff", "")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n\s*\n+", "\n\n", texto)
    return texto.strip()


def titulo_legible(nombre):
    nombre = limpiar(nombre).strip(" .,-")
    if not nombre:
        return "Producto"
    letras = [c for c in nombre if c.isalpha()]
    if letras and sum(c.isupper() for c in letras) / len(letras) < 0.7:
        return nombre[0].upper() + nombre[1:]

    salida = []
    for i, palabra in enumerate(nombre.split()):
        limpia = palabra.strip(".,;:")
        if limpia in PRESERVAR or (any(c.isdigit() for c in limpia) and len(limpia) <= 6):
            nueva = palabra
        elif limpia.lower() in CONECTORES and i > 0:
            nueva = palabra.lower()
        else:
            nueva = palabra.lower()
            # Respeta el separador interno (barra, guion) y capitaliza cada parte.
            partes = re.split(r"([/\-])", nueva)
            for j in range(0, len(partes), 2):
                if partes[j]:
                    partes[j] = partes[j][0].upper() + partes[j][1:]
                    # Siglas que ya venian preservadas.
                    if partes[j].upper() in PRESERVAR:
                        partes[j] = partes[j].upper()
            nueva = "".join(partes)
        salida.append(nueva)

    titulo = " ".join(salida)
    for mal, bien in ACENTOS.items():
        titulo = titulo.replace(mal, bien)
    return titulo[0].upper() + titulo[1:] if titulo else "Producto"


def marca_de(nombre):
    bajo = sin_tildes(nombre).lower()
    for marca in MARCAS:
        if re.search(rf"\b{re.escape(sin_tildes(marca).lower())}\b", bajo):
            return "Satisfyer" if marca == "Satisfayer" else marca
    return ""


def descripcion_de(producto, grupo, subcategoria):
    original = limpiar(producto.get("descripcion"))
    if len(original) >= 80:
        return original[:2200].rsplit(" ", 1)[0] if len(original) > 2200 else original
    base = DESCRIPCIONES[grupo]
    original_nombre = producto.get("nombre", "")
    clave = sin_tildes(limpiar(original_nombre)).upper()
    nombre = TITULOS_ESPECIALES.get(clave) or titulo_legible(original_nombre)
    return f"{nombre}. {base} Producto para mayores de 18 años."


def precio_de(valor):
    if isinstance(valor, (int, float)):
        return int(round(valor))
    texto = str(valor or "")
    texto = re.sub(r"[^\d,]", "", texto).replace(",", ".")
    if not texto:
        return 0
    try:
        return int(float(texto))
    except ValueError:
        return 0


def main():
    productos_origen = json.loads(ORIGEN.read_text(encoding="utf-8"))
    categorias_origen = json.loads((DESTINO.parent.parent / "insumos" / "tecnico" / "categorias.json").read_text(encoding="utf-8"))
    por_url = {c["url"]: c for c in categorias_origen}

    # Cuantas veces aparece cada producto en las categorias del sitio anterior.
    pertenece = defaultdict(list)
    for cat in categorias_origen:
        for url in cat["productos"]:
            pertenece[url].append(cat["nombre"])

    subcategorias = set(SUBCATEGORIA_GRUPO) | set(NOMBRES_SUB)
    subcategorias.add("BOLSAS")

    productos = []
    fuentes = {}
    usados = Counter()
    for item in productos_origen:
        original_nombre = limpiar(item.get("nombre"))
        clave = sin_tildes(original_nombre).upper()
        grupo = None
        sub = None

        sub = CASOS_ESPECIALES.get(original_nombre) or CASOS_ESPECIALES.get(clave)
        if not sub:
            candidatas = pertenece.get(item.get("url"), [])
            principal = item.get("categoria_principal")
            orden = ([principal] if principal else []) + candidatas
            for nombre_cat in orden:
                if nombre_cat in SUBCATEGORIA_GRUPO:
                    sub = nombre_cat
                    break
        if not sub and item.get("categorias"):
            sub = item["categorias"][0]
        if sub not in SUBCATEGORIA_GRUPO:
            sub = "GENERAL"

        # El sitio anterior dejo varios dildos dentro de "JUGUETE/VIBRADOR".
        # Si el nombre empieza por "Dildo" y no es un vibrador, va a Dildos.
        bajo = sin_tildes(original_nombre).lower()
        if bajo.startswith("dildo ") and "vibrador" not in bajo:
            sub = "DILDOS"

        grupo = SUBCATEGORIA_GRUPO.get(sub, "otros")
        precio = precio_de(item.get("precio"))
        antes = precio_de(item.get("precio_antes"))
        if antes <= precio:
            antes = None
        descuento = round((antes - precio) / antes * 100) if antes else None

        titulo = TITULOS_ESPECIALES.get(clave, titulo_legible(original_nombre))
        base_slug = a_slug(titulo)[:70].strip("-") or f"producto-{item.get('odoo_id', len(productos))}"
        usados[base_slug] += 1
        slug = base_slug if usados[base_slug] == 1 else f"{base_slug}-{usados[base_slug]}"

        descripcion = descripcion_de(item, grupo, sub)
        resumen = re.sub(r"\s+", " ", descripcion).strip()
        if len(resumen) > 160:
            resumen = resumen[:157].rsplit(" ", 1)[0] + "…"

        producto = {
            "slug": slug,
            "titulo": titulo,
            "precio": precio,
            "precio_antes": antes,
            "descuento": descuento,
            "categoria": grupo,
            "subcategoria": sub,
            "subcategoria_nombre": NOMBRES_SUB.get(sub, titulo_legible(sub)),
            "marca": marca_de(original_nombre),
            "presentacion": "",
            "stock": bool(item.get("disponible")),
            "recomendado": slug in RECOMENDADOS,
            "promo_flash": False,
            "promo_flash_vence": None,
            "promo_flash_donde": None,
            "imagenes": [f"productos/{slug}.webp"],
            "descripcion": descripcion,
            "resumen": resumen,
            "sku": item.get("sku") or "",
            "oculto": precio <= 0,
            "descripcion_generada": len(limpiar(item.get("descripcion"))) < 80,
        }
        productos.append(producto)
        fuentes[slug] = item.get("imagen", "")

    # Orden estable: primero lo disponible, luego por grupo y nombre.
    orden_grupo = {g["id"]: g["orden"] for g in GRUPOS}
    productos.sort(key=lambda p: (p["oculto"], not p["stock"], orden_grupo[p["categoria"]], p["titulo"].lower()))

    # Conteos por grupo y por subcategoria, solo de lo visible.
    conteo_grupo = Counter(p["categoria"] for p in productos if not p["oculto"])
    conteo_sub = Counter(p["subcategoria"] for p in productos if not p["oculto"])
    grupos = []
    for g in GRUPOS:
        subs = [
            {
                "id": a_slug(s),
                "nombre": NOMBRES_SUB.get(s, titulo_legible(s)),
                "original": s,
                "total": conteo_sub.get(s, 0),
            }
            for s in sorted(subcategorias, key=lambda s: NOMBRES_SUB.get(s, s))
            if SUBCATEGORIA_GRUPO.get(s, "otros") == g["id"] and conteo_sub.get(s, 0) > 0
        ]
        grupos.append({**g, "total": conteo_grupo.get(g["id"], 0), "subcategorias": subs})

    DESTINO.mkdir(parents=True, exist_ok=True)
    (DESTINO / "productos.json").write_text(
        json.dumps(productos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (DESTINO / "categorias.json").write_text(
        json.dumps(grupos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    FUENTES.write_text(json.dumps(fuentes, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"Productos: {len(productos)} ({sum(1 for p in productos if not p['oculto'])} visibles)")
    print(f"Agotados: {sum(1 for p in productos if not p['stock'])}")
    print(f"Sin precio (ocultos): {sum(1 for p in productos if p['oculto'])}")
    print(f"Con descripcion propia: {sum(1 for p in productos if not p['descripcion_generada'])}")
    for g in grupos:
        print(f"  {g['nombre']:<28} {g['total']:>4}  ({len(g['subcategorias'])} tipos)")


if __name__ == "__main__":
    main()
