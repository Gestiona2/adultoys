# Dónde vive cada texto

Todos los textos editables están en `src/datos/`. Los archivos `.astro` solo los leen.
Si un texto no está aquí, no es editable todavía: primero se agrega al archivo de datos.

## `config.json` — datos del negocio

Se usa en el encabezado, el pie, el contacto, las sedes y el mensaje de WhatsApp.

| Campo | Dónde se ve | Límite |
|---|---|---|
| `negocio`, `nombre_largo` | Títulos y logo | Texto corto |
| `tagline` | Pie | Una frase |
| `descripcion_corta` | Pie y metadatos | 1–2 frases |
| `whatsapp` | Enlaces de WhatsApp | Solo dígitos con 57 |
| `whatsapp_visible` | Barra superior, pie | Como se quiere leer |
| `correo`, `direccion`, `ciudad` | Contacto, sedes, legales | Dato real |
| `envio.*` | Barra superior, garantías, carrito | No prometer lo que no se cumple |
| `devoluciones_dias` | Servicios y legales | Número de días |
| `sedes[]` | Página Visítanos | Una sede real |
| `legal.nit`, `legal.razon_social` | Políticas | **PENDIENTE** |
| `redes[]` | Pie | Vacío = no se muestra |
| `medicion.*` | Códigos de analítica | Vacío = no carga nada |

## `home.json` — portada

| Bloque | Qué controla | Límite |
|---|---|---|
| `banners[]` | Carrusel de 3 diapositivas | Título de 2 líneas, texto de 2–3 líneas |
| `marquee[]` | Frases que se desplazan | 2–4 palabras cada una |
| `garantias[]` | Cuatro garantías | Título + una línea |
| `ofertas` | Título de la sección de ofertas | Solo se ve si hay descuentos |
| `recomendaciones_titulo/texto` | Sección de recomendados | Una línea de texto |
| `categorias_titulo/texto` | Bento de categorías | Una línea de texto |
| `manifiesto` | Bloque de marca | Título + párrafo + 3 puntos |
| `blog_titulo/texto` | Sección del blog | Una línea |
| `cierre` | Llamado final | Título + 1–2 líneas |
| `popup_oferta` | Etiquetas de la ventana de promoción | No cambiar salvo que se pida |

Las fotos se referencian sin tamaño (ej. `sitio/banner-hero-neon`); el componente
`Foto.astro` arma las versiones de 600, 900 y 1200 px. Siempre llevan `foto_alt`.

## `nosotros.json` — página Nosotros

Título, entrada, propósito, foto principal, tres bloques y cinco valores. Los valores son
frases cortas; no convertir la página en un texto médico.

## `servicios.json` — Envíos y pagos

Cinco servicios: asesoría, envío, pago, cambios y recogida. Cada uno tiene título,
resumen, detalle y tres puntos. Si se cambia una promesa (por ejemplo, el plazo de
entrega), hay que cambiarla también en `config.json` y `legal.json`.

## `legal.json` — textos legales

Cuatro documentos: `privacidad`, `datos`, `terminos`, `envios`. Cada uno tiene título,
entradilla y bloques. **No son asesoría jurídica**: el dueño o su abogado deben revisarlos.
No cambiar una obligación legal por iniciativa propia.

## `blog.json` — guías

Cuatro artículos con `slug`, `titulo`, `extracto`, `fecha`, `lectura`, `etiqueta`,
`imagen`, `imagen_alt` y `contenido` (bloques `p`, `h2`, `ul`). Los artículos son
informativos y no reemplazan una consulta médica.

## `productos.json` — catálogo

Lo genera `tools/construir-datos.py` y lo edita el dueño desde
`Catalogo-Adultoyss.xlsx`. **No se edita a mano** salvo que el proveedor lo indique.

Campos que se muestran:

| Campo | Uso |
|---|---|
| `titulo` | Nombre de la tarjeta y la ficha |
| `precio`, `precio_antes`, `descuento` | Precio y oferta |
| `categoria`, `subcategoria_nombre` | Navegación y filtros |
| `marca`, `presentacion` | Ficha técnica |
| `stock` | «Disponible» o «Agotado» |
| `recomendado` | Sección Recomendaciones |
| `promo_flash*` | Ventana de promoción relámpago |
| `descripcion`, `resumen` | Texto de la ficha y metadatos |
| `imagenes[]` | Foto principal |
| `oculto` | Si no se publica (precio 0) |

No cambiar el `slug`: es la URL y rompe enlaces e historial.

## `categorias.json` — navegación

Nombre, descripción, icono, orden, imagen y subcategorías. Se regenera al reconstruir el
catálogo. Los conteos se actualizan al aplicar la planilla.

## `sinonimos.json` — buscador

Palabras alternativas para que el buscador encuentre un producto aunque el visitante no
escriba el nombre exacto. Agregar sinonimos en minúsculas, sin duplicados.
