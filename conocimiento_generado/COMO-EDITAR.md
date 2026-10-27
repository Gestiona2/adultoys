# Cómo editar

Recetas para los cambios más comunes. Todas terminan con `npm run verificar` antes de
publicar.

## Cambiar un precio, el stock o una oferta

1. Abrir `Catalogo-Adultoyss.xlsx`.
2. Buscar el producto por nombre (fila 1 tiene filtros).
3. Editar solo las celdas amarillas:
   - **Precio ($)**: número entero, sin puntos ni `$`. Ejemplo: `350000`.
   - **Precio anterior**: solo si hay oferta y es mayor al precio actual.
   - **¿Hay existencias?**: `SI` o `NO`.
4. Guardar.
5. Aplicar y verificar:

```bash
python3 tools/excel_catalogo.py revisar Catalogo-Adultoyss.xlsx
python3 tools/excel_catalogo.py aplicar Catalogo-Adultoyss.xlsx
npm run verificar
```

El descuento se calcula solo. No se escribe a mano.

## Marcar un producto como recomendado

En la planilla, columna **¿Recomendado en portada?**, poner `SI`. La portada muestra
hasta 12; si hay más, rota entre ellos.

## Activar una promoción relámpago

1. Poner `SI` en **¿Promoción relámpago?**.
2. Opcional: escribir la vigencia en **Vence la promoción** con el formato
   `2026-12-31 20:00` (hora de Bogotá).
3. Opcional: escribir dónde aplica en **¿Dónde aplica la promoción?**.
4. El producto debe estar disponible (`SI` en existencias).

Sin fecha de vigencia, la promoción sigue hasta que alguien la apague.

## Ocultar un producto sin borrarlo

Dejar el **Precio** en `0`. El producto queda guardado, no se publica y no aparece en
el catálogo. Si después se pone un precio, vuelve a publicarse.

## Cambiar el WhatsApp o el correo

Editar `src/datos/config.json`:

```json
"whatsapp": "573102130278",
"whatsapp_visible": "+57 310 213 0278",
"correo": "adultoyssexshopweb@outlook.com"
```

El número de `whatsapp` va sin `+`, sin espacios y con `57` al inicio. Se usa en todos
los botones; no hay que tocarlos uno por uno.

## Cambiar el texto de la portada

Editar `src/datos/home.json`. Los banners tienen `titulo`, `texto`, `boton` y `enlace`.
Mantener el título en dos líneas como máximo y el texto en dos o tres.

## Cambiar una foto de la portada

1. Guardar la foto original en `insumos/fotos/sitio/` con un nombre en minúsculas y sin
   espacios (ej. `banner-navidad.jpg`).
2. Ejecutar `npm run imagenes` para generar las versiones WebP.
3. En `home.json`, cambiar `foto` por `sitio/banner-navidad` (sin tamaño ni extensión).
4. Escribir un `foto_alt` que describa la imagen.

## Cambiar la foto de un producto

1. Guardar la original en `insumos/fotos/catalogo/` con el nombre del slug
   (ej. `satisfyer-pro-2.jpg`).
2. Ejecutar `npm run imagenes` (o `npm run imagenes -- --force`).
3. Verificar que la ficha muestre la foto nueva.

Si la foto no existe o pesa demasiado, `npm run validar` lo dice.

## Publicar un artículo del blog

Editar `src/datos/blog.json` y agregar un objeto en `posts` con `slug` único, `titulo`,
`extracto`, `fecha`, `lectura`, `etiqueta`, `imagen`, `imagen_alt` y `contenido`. Los
bloques pueden ser `p`, `h2` y `ul`.

No copiar artículos de otras webs sin permiso. No dar consejos médicos.

## Cambiar una política legal

Editar `src/datos/legal.json`. **Antes de publicar, que el dueño o su abogado lo
revisen.** Si el cambio afecta envíos o devoluciones, actualizar también
`config.json`, `servicios.json` y `home.json` para que no se contradigan.

## Agregar un producto nuevo

No se hace desde la planilla. Hay que:
1. Agregar el producto a los insumos originales (o al catálogo fuente).
2. Ejecutar `npm run datos`.
3. Ejecutar `npm run imagenes`.
4. `npm run excel` para regenerar la planilla.
5. `npm run verificar`.

Esto lo hace el proveedor, no el dueño.

## Encender o apagar el tema de Halloween

En `src/datos/config.json`, el campo `"tema_estacional"`:

- `"halloween"` → telarañas, arañas, murciélagos, una bruja que cruza la portada, la luna
  detrás de la foto, calabazas en el pie y colores naranja.
- `""` (vacío) → el sitio queda como siempre. No se cambia nada más.

Después: `npm run verificar` y publicar. Pasada la temporada se pueden borrar
`public/img/halloween/` y `src/styles/halloween.css`; nada más los usa.

El catálogo en PDF tiene su propia edición:

```
python3 tools/catalogo_pdf.py --tema halloween
```

Sin `--tema` sale el catálogo normal.
