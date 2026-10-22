# Reglas del catálogo

## De dónde sale

El catálogo se descargó del sitio anterior en Odoo
(`https://adultoyssexshopcol.odoo.com/`) el 21 de octubre de 2026. Son **596 productos**
con foto, precio y categoría. El material original está en `insumos/` y no se publica.

`tools/construir-datos.py` transforma ese material en:

- `src/datos/productos.json` — el catálogo que lee el sitio.
- `src/datos/categorias.json` — 10 grupos de navegación.
- `src/datos/_fuentes.json` — de qué foto original salió cada imagen.

## Por qué se publican 554 y no 596

**42 productos tienen precio $0** en el sitio anterior. No se puede vender algo sin
precio, así que quedan `oculto: true` y no se muestran. Siguen en el catálogo y en la
planilla para que el dueño les ponga precio cuando lo sepa.

Cuando un producto oculto recibe precio, vuelve a publicarse solo.

## Stock

199 productos están agotados según el dato original. Se muestran igual, con la etiqueta
«Agotado», y no se pueden agregar al pedido. El dueño actualiza el stock en la planilla.

## Precios y descuentos

- Todos los precios son enteros de pesos colombianos.
- El precio anterior solo existe si es **mayor** que el actual.
- El descuento se calcula: `(antes - precio) / antes × 100`, redondeado.
- **Hoy no hay descuentos reales**: en el sitio anterior `precio_antes` era igual a
  `precio`, así que el campo quedó vacío. La sección Ofertas existe y funciona, pero
  está vacía hasta que el dueño cree una oferta real.
- No se inventan descuentos para llenar la página.

## Recomendaciones

La portada muestra hasta 12 productos marcados con `recomendado: true`. La selección
inicial incluye:

- Satisfyer Pro 2
- Succionador Galaku
- Bala Faire App
- Dildo David
- Arnés Dalias
- Lubricante Multi Frío-Calor Sen Íntimo
- Preservativos Today x3
- Fantasía Erótica
- Anillo Vibrador Bunny Ring Blue
- Cerdito Lamedor Pink con Lengua
- Babydoll Encaje Dorado
- Huevo Remote Control Egg

Si el dueño marca más de 12, la sección rota entre ellos. Si marca menos, muestra los que
haya.

## Promoción relámpago

La ventana emergente solo aparece si hay al menos un producto con `promo_flash: true`.
Reglas:

- El producto debe estar disponible.
- Puede tener fecha de vencimiento (`promo_flash_vence`, hora de Bogotá).
- Puede indicar dónde aplica (`promo_flash_donde`).
- Sin fecha, sigue activa hasta que se apague a mano.

Hoy no hay promociones activas. La funcionalidad está lista.

## Categorías

El sitio anterior tenía **55 categorías planas** y un menú mal armado. Se agruparon en
**10 grupos** para que el visitante encuentre algo sin perderse:

vibradores, dildos, parejas, lencería, lubricantes, salud, sado, higiene, weed y otros.

Cada producto conserva su subcategoría original (por ejemplo `BALAS`) y un nombre
legible (`Balas vibradoras`) para los filtros. «Otros» no aparece en el menú.

## Nombres corregidos

El sitio anterior tenía errores de escritura en los nombres. Se corrigieron estos:

| Antes | Ahora |
|---|---|
| SATISFAYER PRO 2 | Satisfyer Pro 2 |
| SUBCIONADOR GALAKU | Succionador Galaku |
| FANTASIA EROTICA | Fantasía Erótica |
| ARNES DALIAS | Arnés Dalias |
| LENCERIA 75000 | Babydoll Encaje Dorado |

Los demás nombres se pasaron de mayúsculas a formato de frase, respetando marcas y
siglas (KLG, WEED, XL, etc.).

## Descripciones

Solo **72 productos** traían descripción propia. Los demás tienen una descripción neutra
por categoría, sin inventar propiedades. Cuando el dueño escriba una descripción real, se
reemplaza.

Las descripciones no llevan propiedades médicas, curas ni resultados garantizados.

## Imágenes

- 596 fotos de producto en WebP, entre 1 y 62 KB.
- 271 fotos originales tienen el lado menor por debajo de 400 px: se ven bien en la
  ficha actual, pero conviene pedir originales para un catálogo más grande.
- La foto principal es la que tenía el producto en Odoo. No se inventan fotos.
- Si falta una foto, se conserva la actual y se anota en `PENDIENTES.md`.

## Lo que no se toca

- El `slug`: es la URL del producto y la clave del historial.
- El orden de las filas de la planilla.
- Los campos `imagenes`, `sku` y `descripcion_generada` desde Excel.
- Los conteos de categorías a mano: se recalculan al aplicar la planilla.
