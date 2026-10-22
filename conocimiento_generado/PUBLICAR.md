# Cómo publicar

## Antes de publicar

1. Confirmar que el catálogo está bien:

```bash
npm run verificar
```

Ese comando valida el catálogo, corre las pruebas y compila. Si algo falla, **no
publicar**: el mensaje dice qué producto o archivo hay que corregir.

2. Revisar el sitio con `npm run preview` en el celular y en el computador.
3. Confirmar con el dueño los pendientes de `PENDIENTES.md` (NIT, horarios, redes,
   promesas de envío y textos legales).

## Publicar

El sitio es estático. Se genera con:

```bash
npm run build
```

y se sube el contenido de `dist/` al hosting.

### Opción A — Netlify o Vercel

- Conectar el repositorio del cliente.
- Comando de compilación: `npm run build`.
- Carpeta de salida: `dist`.
- Configurar el dominio del cliente.

### Opción B — GitHub Pages

- Publicar `dist/` en la rama de Pages.
- Si se publica en un subdirectorio, definir `PUBLIC_BASE` antes de compilar
  (ej. `PUBLIC_BASE=/adultoyss/`).

### Opción C — Servidor propio

- Subir `dist/` a la carpeta pública del dominio.
- Servir `index.html` para las rutas y respetar `/sitemap.xml` y `/robots.txt`.

## Dominio

El dominio definitivo **no está decidido**. El valor por defecto del proyecto es
`https://adultoyss.com`, pero hay que confirmarlo con el dueño y ajustar `PUBLIC_SITE`
antes de compilar para que las URLs canónicas y el sitemap sean correctas.

## Después de publicar

1. Abrir el sitio en celular y computador.
2. Probar: buscar, filtrar, abrir un producto, agregar al carrito, enviar un pedido de
   prueba a WhatsApp y volver a comprar.
3. Revisar que el WhatsApp que abre sea el del negocio.
4. Enviar el sitemap a Google Search Console cuando el dominio esté listo.
5. Confirmar que el aviso 18+ y las políticas estén visibles.

## Cómo deshacer

Si el hosting guarda versiones anteriores, volver a la última que funcionaba. Si se
publica desde un repositorio, revertir el cambio y volver a compilar. Nunca borrar la
versión anterior antes de confirmar que la nueva funciona.
