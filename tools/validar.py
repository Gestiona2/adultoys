#!/usr/bin/env python3
"""Revisa que el catalogo de Adultoyss este bien formado antes de publicarlo.

    python3 tools/validar.py src/datos/productos.json public/img

Existe porque el catalogo lo edita un agente conversando con el dueno de la
tienda, y un dato mal escrito puede romper el sitio o publicar un precio falso
sin que nadie lo note. Cada mensaje dice que producto esta mal, que pasa y como
se escribe bien, para corregirlo sin saber programar.

Devuelve codigo de salida 1 si hay errores.
"""
import difflib
import json
import re
import sys
from pathlib import Path

OBLIGATORIOS = ("slug", "titulo", "precio", "categoria", "imagenes")
SLUG_VALIDO = re.compile(r"^[a-z0-9-]+$")

# La vigencia de la oferta relampago se guarda en hora de Bogota (-05:00 fijo,
# sin horario de verano). Formato JSON: "2026-10-05T20:00:00-05:00".
PROMO_VENCE_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00-05:00$")

# Tope de cordura: el producto mas caro cuesta $680.000. Un valor por encima
# casi siempre es un precio con ceros de mas.
PRECIO_MAXIMO = 3_000_000

# Peso maximo de una foto de producto ya preparada. Las del catalogo pesan
# entre 1 y 62 KB; 150 KB deja margen y atrapa la foto sin preparar.
IMAGEN_MAXIMA_KB = 150

SI_O_NO = {
    "stock": "true si hay existencias, false si esta agotado",
    "recomendado": "true para mostrarlo en Recomendaciones, false si no",
    "promo_flash": "true para mostrarlo en la ventana emergente de promocion, false si no",
    "oculto": "true si el producto no debe publicarse, false si si",
}


def es_entero(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def descuento_esperado(precio, antes):
    return round((antes - precio) / antes * 100)


def leer_catalogo(ruta):
    """Lee el archivo. Devuelve (productos, None) o (None, mensaje legible)."""
    texto = Path(ruta).read_text(encoding="utf-8")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as error:
        lineas = texto.splitlines()
        linea = lineas[error.lineno - 1] if 0 < error.lineno <= len(lineas) else ""
        pista = {
            "Expecting property name enclosed in double quotes":
                "sobra una coma, o falta una comilla antes del nombre del campo",
            "Expecting ',' delimiter": "falta una coma entre dos campos o dos productos",
            "Expecting value": "sobra una coma, o falta un valor despues de los dos puntos",
            "Unterminated string starting at": "hay una comilla sin cerrar",
            "Invalid control character": "hay una comilla sin cerrar: el texto sigue en la linea de abajo",
            "Extra data": "sobra algo despues del ultimo corchete ]",
        }
        explicacion = next(
            (texto_pista for clave, texto_pista in pista.items() if error.msg.startswith(clave)),
            error.msg,
        )
        return None, (
            f"El archivo tiene un error de escritura en la linea {error.lineno}, "
            f"columna {error.colno}: {explicacion}.\n\n"
            f"    {error.lineno} | {linea.strip()[:100]}\n\n"
            f"Nada del catalogo se publica hasta corregirlo."
        )
    if not isinstance(datos, list):
        return None, "El catalogo debe ser una lista de productos entre corchetes [ ]."
    return datos, None


def validar(productos, carpeta_imagenes=None, categorias=None, subcategorias=None):
    """Devuelve la lista de errores encontrados. Vacia significa que todo esta bien."""
    errores = []
    vistos = set()

    for indice, producto in enumerate(productos):
        if not isinstance(producto, dict):
            errores.append(f"producto #{indice}: no es un producto, revisa las llaves {{ }}")
            continue

        quien = producto.get("slug") or producto.get("titulo") or f"producto #{indice}"

        for campo in OBLIGATORIOS:
            if campo not in producto:
                errores.append(f"{quien}: falta el campo obligatorio '{campo}'")

        # --- titulo ---
        titulo = producto.get("titulo")
        if "titulo" in producto and (not isinstance(titulo, str) or not titulo.strip()):
            errores.append(f"{quien}: el titulo esta vacio; la tarjeta saldria sin nombre")

        # --- slug ---
        slug = producto.get("slug")
        if slug is not None:
            if not isinstance(slug, str) or not SLUG_VALIDO.match(slug):
                errores.append(
                    f"{quien}: el slug debe ser minusculas, numeros y guiones "
                    f"(es la URL del producto)"
                )
            elif slug in vistos:
                errores.append(f"{quien}: slug repetido, cada producto necesita el suyo")
            else:
                vistos.add(slug)

        # --- precios ---
        oculto = producto.get("oculto") is True
        precio = producto.get("precio")
        precio_ok = es_entero(precio) and (precio > 0 or (precio == 0 and oculto))
        if not precio_ok:
            if es_entero(precio) and precio == 0 and not oculto:
                errores.append(
                    f"{quien}: el precio es 0 y el producto no esta marcado como oculto. "
                    f"Ponle precio o marcalo oculto para que no se publique."
                )
            else:
                errores.append(
                    f"{quien}: el precio debe ser un numero entero de pesos mayor que cero "
                    f"(por ejemplo 350000, no \"$350.000\")"
                )

        if precio_ok and precio > PRECIO_MAXIMO:
            errores.append(
                f"{quien}: el precio ({precio:,}) parece tener ceros de mas; ".replace(",", ".")
                + f"el tope razonable es {PRECIO_MAXIMO:,}".replace(",", ".")
            )

        antes = producto.get("precio_antes")
        antes_ok = False
        if antes is not None:
            if not es_entero(antes):
                errores.append(f"{quien}: precio_antes debe ser un numero entero o estar vacio (null)")
            elif precio_ok and precio > 0 and antes <= precio:
                errores.append(
                    f"{quien}: precio_antes ({antes}) no es mayor que el precio ({precio}), "
                    f"asi que no hay oferta que mostrar"
                )
            else:
                antes_ok = precio_ok and precio > 0

        # --- descuento: sale de los precios, no se inventa ---
        descuento = producto.get("descuento")
        if antes is None:
            if descuento is not None:
                errores.append(
                    f"{quien}: tiene descuento ({descuento}) pero no precio_antes; "
                    f"o se agrega el precio anterior o el descuento va en null"
                )
        elif antes_ok:
            esperado = descuento_esperado(precio, antes)
            if descuento != esperado:
                errores.append(
                    f"{quien}: el descuento debe ser {esperado} "
                    f"(de {antes} a {precio}), no {descuento}"
                )

        # --- campos de si o no ---
        for campo, explicacion in SI_O_NO.items():
            if campo in producto and not isinstance(producto[campo], bool):
                errores.append(
                    f"{quien}: '{campo}' debe ser true o false, sin comillas "
                    f"({explicacion}); tiene {json.dumps(producto[campo], ensure_ascii=False)}"
                )

        # --- promocion relampago: solo productos disponibles ---
        if producto.get("promo_flash") is True and producto.get("stock") is False:
            errores.append(
                f"{quien}: 'promo_flash' no puede ser true porque el producto "
                f"esta agotado; la ventana emergente solo muestra productos disponibles"
            )

        # --- vigencia de la promocion ---
        vence = producto.get("promo_flash_vence")
        if vence is not None:
            if not isinstance(vence, str) or not PROMO_VENCE_ISO.match(vence):
                errores.append(
                    f"{quien}: 'promo_flash_vence' debe tener el formato "
                    f"AAAA-MM-DDTHH:MM:00-05:00 (hora de Bogota) o estar vacio (null); "
                    f"tiene {json.dumps(vence, ensure_ascii=False)}. Se edita desde la "
                    f"planilla, columna de vigencia de la promocion."
                )
            elif producto.get("promo_flash") is not True:
                errores.append(
                    f"{quien}: tiene 'promo_flash_vence' pero 'promo_flash' no es true; "
                    f"la vigencia no sirve de nada sin la promocion activa"
                )

        # --- donde aplica la promocion ---
        donde = producto.get("promo_flash_donde")
        if donde is not None:
            if not isinstance(donde, str) or not donde.strip():
                errores.append(
                    f"{quien}: 'promo_flash_donde' debe ser texto o estar vacio (null); "
                    f"tiene {json.dumps(donde, ensure_ascii=False)}"
                )
            elif producto.get("promo_flash") is not True:
                errores.append(
                    f"{quien}: tiene 'promo_flash_donde' pero 'promo_flash' no es true; "
                    f"no sirve de nada decir donde aplica una promocion que no esta activa"
                )

        # --- categoria y subcategoria ---
        categoria = producto.get("categoria")
        if categorias is not None and categoria is not None and categoria not in categorias:
            parecida = difflib.get_close_matches(str(categoria), sorted(categorias), n=1)
            sugerencia = f" ¿Querias decir '{parecida[0]}'?" if parecida else ""
            errores.append(
                f"{quien}: la categoria '{categoria}' no existe, y el producto no saldria "
                f"en ninguna categoria ni filtro.{sugerencia}"
            )

        subcategoria = producto.get("subcategoria")
        if (
            subcategorias is not None
            and subcategoria is not None
            and subcategoria not in subcategorias
            and producto.get("oculto") is not True
        ):
            parecida = difflib.get_close_matches(str(subcategoria), sorted(subcategorias), n=1)
            sugerencia = f" ¿Querias decir '{parecida[0]}'?" if parecida else ""
            errores.append(
                f"{quien}: la subcategoria '{subcategoria}' no existe, y el producto "
                f"no saldria en el filtro Tipo.{sugerencia}"
            )

        # --- imagenes ---
        imagenes = producto.get("imagenes")
        if not isinstance(imagenes, list) or not imagenes:
            errores.append(f"{quien}: necesita al menos una imagen")
        elif carpeta_imagenes:
            for imagen in imagenes:
                ruta = Path(carpeta_imagenes) / imagen
                if not ruta.exists():
                    errores.append(f"{quien}: la imagen '{imagen}' no existe en la carpeta")
                    continue
                if ruta.suffix.lower() != ".webp":
                    errores.append(
                        f"{quien}: la imagen '{imagen}' no esta en formato webp. "
                        f"Se prepara con: node tools/preparar-imagenes.mjs --force"
                    )
                    continue
                kb = ruta.stat().st_size / 1024
                if kb > IMAGEN_MAXIMA_KB:
                    errores.append(
                        f"{quien}: la imagen '{imagen}' pesa {kb:.0f} KB y el maximo es "
                        f"{IMAGEN_MAXIMA_KB} KB. Una foto asi hace lenta la pagina en "
                        f"celular. Se arregla con: node tools/preparar-imagenes.mjs --force"
                    )

    return errores


def _objetos_con_foto(dato, donde):
    """Recorre un JSON y devuelve (donde, objeto) por cada objeto con la clave 'foto'."""
    if isinstance(dato, dict):
        if "foto" in dato:
            yield donde, dato
        for clave, valor in dato.items():
            yield from _objetos_con_foto(valor, f"{donde} -> {clave}")
    elif isinstance(dato, list):
        for indice, valor in enumerate(dato):
            yield from _objetos_con_foto(valor, f"{donde}[{indice}]")


def _existe_alguna_version(carpeta_imagenes, foto):
    """La foto 'sitio/fachada' existe si hay 'sitio/fachada-<ancho>.webp'."""
    ruta = Path(carpeta_imagenes) / foto
    patron = re.compile(rf"^{re.escape(ruta.name)}-\d+\.webp$")
    return ruta.parent.is_dir() and any(patron.match(a.name) for a in ruta.parent.iterdir())


def validar_fotos(carpeta_datos, carpeta_imagenes):
    """Revisa las fotos elegidas en los JSON del sitio (portada, nosotros)."""
    errores = []
    for archivo in sorted(Path(carpeta_datos).glob("*.json")):
        if archivo.name == "productos.json":
            continue
        try:
            datos = json.loads(archivo.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        for donde, objeto in _objetos_con_foto(datos, archivo.name):
            foto = objeto["foto"]
            if not isinstance(foto, str) or not foto.strip():
                errores.append(f"{donde}: 'foto' esta vacia. Pon el nombre de la foto o quita el campo.")
                continue
            if not _existe_alguna_version(carpeta_imagenes, foto):
                errores.append(
                    f"{donde}: la foto '{foto}' no existe en public/img. Se prepara con: "
                    f"node tools/preparar-imagenes.mjs --force"
                )
            alt = objeto.get("foto_alt")
            if not isinstance(alt, str) or not alt.strip():
                errores.append(
                    f"{donde}: la foto '{foto}' necesita 'foto_alt', una frase que la describa "
                    f"para quien usa lector de pantalla."
                )
    return errores


def cargar_categorias(ruta_catalogo):
    """Las categorias validas, leidas de categorias.json junto al catalogo."""
    ruta = Path(ruta_catalogo).parent / "categorias.json"
    if not ruta.exists():
        return None, None
    categorias = json.loads(ruta.read_text(encoding="utf-8"))
    ids = {c["id"] for c in categorias}
    subs = set()
    for c in categorias:
        for sub in c.get("subcategorias", []):
            subs.add(sub["id"])
            if sub.get("original"):
                subs.add(sub["original"])
    return ids, subs


def main(ruta, carpeta_imagenes=None):
    productos, error = leer_catalogo(ruta)
    if error:
        print(error)
        return 1

    categorias, subcategorias = cargar_categorias(ruta)
    errores = validar(productos, carpeta_imagenes, categorias, subcategorias)
    if carpeta_imagenes:
        errores += validar_fotos(Path(ruta).parent, carpeta_imagenes)

    if errores:
        print(f"{len(errores)} problema(s) en {ruta}:\n")
        for mensaje in errores[:60]:
            print(f"  - {mensaje}")
        if len(errores) > 60:
            print(f"  ... y {len(errores) - 60} mas")
        return 1

    print(f"{len(productos)} productos validos en {ruta}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    carpeta = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(main(sys.argv[1], carpeta))
