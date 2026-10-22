# Cómo está hecho

## Tecnología

- **Astro 7** con TypeScript y Tailwind 4 (plugin de Vite).
- Sitio **estático**: se compila a HTML, CSS y JavaScript. No necesita base de datos ni
  servidor propio.
- **Sin pasarela de pago.** El pedido se cierra por WhatsApp.
- Imágenes en **WebP** generadas con `sharp`.
- Fuentes locales en `public/fonts/`.

## Estructura

```
src/
├── datos/          Textos y catálogo (lo único que se edita a mano)
├── layouts/        Tienda.astro: encabezado, pie, SEO, carrito
├── components/     Piezas visuales (tarjetas, banners, header, footer)
├── pages/          Una página por archivo; las rutas dinámicas usan [slug]
├── scripts/        Carrito, buscador, filtros, favoritos, pedido
└── styles/         global.css (base y tema) y tienda.css (páginas)
public/
├── fonts/          Sora e Inter
└── img/
    ├── productos/  596 fotos WebP
    ├── sitio/      Banners y fotos de secciones
    └── marca/      Logo, iconos y OG
tools/              Scripts de construcción (no se publican)
insumos/            Material original del negocio (no se publica)
```

## Rutas

- `/` portada.
- `/catalogo` catálogo con filtros en el navegador.
- `/categoria/[cat]` y `/producto/[slug]` se generan en la compilación.
- `/blog/[slug]`, `/legal/[tipo]` también.
- `/datos/catalogo.json` y `/datos/sinonimos.json` alimentan el buscador y los filtros.
- `/sitemap.xml` y `/robots.txt` se generan solos.

## Comandos

```bash
npm install
npm run dev
npm run build
npm run preview
npm run validar
npm test
npm run verificar
npm run datos
npm run excel
npm run imagenes
```

## Variables de entorno

| Variable | Para qué | Por defecto |
|---|---|---|
| `PUBLIC_SITE` | Dominio canónico | `https://adultoyss.com` |
| `PUBLIC_BASE` | Subdirectorio si se publica como demo | `/` |

## Carrito y datos del visitante

- El carrito y los favoritos viven en `localStorage` del navegador.
- Claves: `adultoyss-pedido`, `adultoyss-favoritos`, `adultoyss-historial`.
- No hay cuentas de usuario ni datos en servidor.
- El pedido se arma en el navegador y se abre WhatsApp con el mensaje listo.

## Compilación

`npm run build` genera `dist/`. Son unas 583 páginas. Se puede publicar en cualquier
hosting estático (Netlify, Vercel, Cloudflare Pages, GitHub Pages o un servidor propio).

No hay que subir `node_modules/`, `insumos/` ni `tools/` al servidor.
