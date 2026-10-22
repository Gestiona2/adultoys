# Manual de Adultoyss

Este manual es para el dueño de la tienda. No hace falta saber programar.

## 1. Cómo está armado el sitio

- **Catálogo**: 554 productos publicados. Se ven en la página «Catálogo», en las
  categorías y en el buscador.
- **Pedido**: el cliente elige, deja sus datos y el sitio abre **WhatsApp** con el pedido
  escrito. No se cobra en línea.
- **Contenido**: la portada, «Nosotros», «Envíos y pagos», el blog y las políticas se
  cambian en archivos de texto que están en `src/datos/`.
- **Precios y stock**: se cambian en la planilla de Excel, no en el sitio.

## 2. Cambiar precios, stock y ofertas

Abre `Catalogo-Adultoyss.xlsx`.

### Las columnas

| Columna | Qué escribir |
|---|---|
| Código | No se toca. Es la dirección del producto. |
| Nombre | El nombre que se muestra. |
| Marca | La marca, si la tiene. |
| Presentación | Contenido o medida, si aplica. |
| Categoría | Se elige de la lista. |
| Subcategoría | Se elige de la lista. |
| Precio | Solo números, sin puntos ni `$`. Ejemplo: `350000`. |
| Precio anterior | Solo si hay oferta y es mayor al precio actual. |
| % descuento | Se calcula solo. No se toca. |
| ¿Hay existencias? | `SI` o `NO`. |
| ¿Recomendado? | `SI` para que salga en la portada. |
| ¿Promoción relámpago? | `SI` para la ventana de ofertas. |
| Vence la promoción | Opcional: `2026-12-31 20:00`. |
| ¿Dónde aplica? | Opcional: «Solo en la web», «En todas las sedes». |
| Descripción | Texto de la ficha. Sin promesas médicas. |
| Imagen | No se toca. |

### Reglas

1. Edita **solo las celdas amarillas**.
2. No borres ni agregues filas.
3. Si no sabes el precio, déjalo en `0`: el producto no se publica.
4. El descuento se calcula solo. Si no hay oferta, deja el precio anterior vacío.
5. Guarda el archivo y envíalo de vuelta.

## 3. Qué significa cada estado

- **Disponible**: se puede agregar al pedido.
- **Agotado**: se muestra, pero no se puede pedir.
- **Oculto**: no aparece. Pasa cuando el precio es `0`.
- **Recomendado**: sale en la portada.
- **Promoción relámpago**: sale en la ventana emergente.

## 4. Cambiar el WhatsApp, el correo o la dirección

Se cambian en `src/datos/config.json`. El número de WhatsApp debe ir sin `+`, sin
espacios y con `57` al inicio: `573102130278`.

Ese cambio se refleja en todos los botones del sitio. No hay que cambiar cada página.

## 5. Cambiar textos de la portada

En `src/datos/home.json` están:

- Las tres diapositivas del inicio (título, texto, botón y foto).
- Las frases que se desplazan.
- Las cuatro garantías.
- El texto de «Recomendaciones».
- El bloque «El placer también es bienestar».
- El cierre con el botón de WhatsApp.

Mantén los títulos cortos: se ven en celular.

## 6. Cambiar una foto

Las fotos las prepara el proveedor. Si quieres cambiar una:

1. Envía la foto original en la mejor calidad posible.
2. Indica qué producto o qué parte del sitio debe reemplazar.
3. El proveedor la prepara y la publica.

No se inventan fotos ni se usan fotos de otras tiendas.

## 7. El blog

Hay cuatro guías:

- Tu primer juguete sexual.
- Parejas y placer.
- Sexo y bienestar.
- Cómo limpiar tus juguetes.

Se pueden editar o agregar más. El contenido es informativo, no consejo médico.

## 8. Políticas y datos legales

El sitio tiene política de privacidad, autorización de datos, términos y política de
envíos. **Están redactadas como borrador para Colombia y deben ser revisadas por el
dueño o su abogado antes de publicar.**

Falta confirmar:

- NIT y razón social.
- Horario de atención.
- Si el envío es siempre gratis o tiene condiciones.
- Si los 30 días de cambios aplican a todos los productos.

## 9. Antes de publicar

El proveedor corre:

```bash
npm run verificar
```

Eso revisa el catálogo, las pruebas y la compilación. Si algo está mal, el sitio no se
publica.

Después se prueba en celular:

- Buscar un producto.
- Filtrar por categoría y precio.
- Agregar al carrito.
- Enviar un pedido de prueba.
- Abrir el WhatsApp correcto.
- Ver «Volver a comprar».

## 10. Qué no hacer

- No borres productos ni categorías.
- No cambies el código del producto (la columna «Código»).
- No inventes precios, marcas ni propiedades médicas.
- No publiques fotos de personas sin autorización.
- No cambies las políticas sin revisión legal.
- No prometas plazos de entrega nuevos sin confirmarlos.

## 11. A quién escribir

Para cambios de estructura, fotos nuevas, dominio o cualquier cosa que no esté en este
manual: al proveedor del sitio. Para precios, stock y ofertas: se hace en la planilla.
