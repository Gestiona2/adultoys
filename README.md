# Adultoyss

Sitio de comercio de **Adultoyss Tienda Erótica**: 554 productos visibles, catálogo
filtrable, recomendaciones, blog y pedido que se cierra por WhatsApp.

Tienda física en C.C. Milan Plaza, Tocancipá (Cundinamarca). Envío discreto a toda
Colombia y pago contraentrega.

## Empezar

```bash
npm install
npm run dev      # http://localhost:4321
```

## Comandos

| Comando | Qué hace |
|---|---|
| `npm run dev` | Levanta el sitio en tu computador, con recarga automática |
| `npm run build` | Compila el sitio en `dist/` |
| `npm run preview` | Sirve lo compilado, como se verá publicado |
| `npm test` | Corre las pruebas de JavaScript y de Python |
| `npm run validar` | Revisa el catálogo y las imágenes |
| `npm run verificar` | Validar + pruebas + compilar. **Antes de publicar** |
| `npm run datos` | Reconstruye el catálogo desde los insumos originales |
| `npm run excel` | Genera `Catalogo-Adultoyss.xlsx` |
| `npm run imagenes` | Prepara fotos de producto y del sitio en WebP |

`npm run datos` es para la construcción inicial o para volver a procesar los insumos.
**Después de editar la planilla no lo ejecutes:** sobrescribe el catálogo con los datos
originales.

## Dónde está cada cosa

| Qué quieres cambiar | Archivo |
|---|---|
| Precios, productos, stock, ofertas | `Catalogo-Adultoyss.xlsx` → `src/datos/productos.json` |
| WhatsApp, correo, dirección, envíos | `src/datos/config.json` |
| Textos y banners de la portada | `src/datos/home.json` |
| Nosotros | `src/datos/nosotros.json` |
| Servicios | `src/datos/servicios.json` |
| Textos legales | `src/datos/legal.json` |
| Blog | `src/datos/blog.json` |
| Colores y tipografía | `src/styles/global.css` |
| Palabras que la gente busca | `src/datos/sinonimos.json` |

**Ningún texto se escribe dentro del código.** Todo el contenido editable vive en
`src/datos/`.

## Documentación

- `AGENTS.md` y `CLAUDE.md` — instrucciones para el asistente del sitio.
- `conocimiento_generado/` — sitio, secciones, marca, cómo editar, cómo publicar y
  reglas del catálogo.
- `TUTORIAL.md` — guía corta para el dueño, con ejemplos de este catálogo.
- `MANUAL.md` — manual completo para el dueño, sin tecnicismos.
- `PENDIENTES.md` — lo que falta antes de publicar en el dominio definitivo.
- `instalar.sh` / `doctor.sh` (y versiones `.ps1`) — instalación y revisión del equipo.

## Herramientas

Las de `tools/` se ejecutan **en tu computador**, no en el servidor. El sitio publicado
no necesita Python para nada.
