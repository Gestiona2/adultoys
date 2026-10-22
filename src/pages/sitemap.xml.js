/**
 * Mapa del sitio. Se genera en la compilación, así que nunca se desactualiza.
 */
import productos from "../datos/productos.json";
import categorias from "../datos/categorias.json";
import blog from "../datos/blog.json";
import legal from "../datos/legal.json";

export function GET({ site }) {
  const raiz = (site?.href || "https://adultoyss.com/").replace(/\/$/, "");
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  const hoy = new Date().toISOString().slice(0, 10);

  const url = (ruta, prioridad) =>
    `  <url><loc>${raiz}${base}/${ruta}</loc><lastmod>${hoy}</lastmod><priority>${prioridad}</priority></url>`;

  const documentos = Object.keys(legal).filter((clave) => !clave.startsWith("_") && clave !== "actualizado");

  const paginas = [
    url("", "1.0"),
    url("catalogo", "0.9"),
    url("ofertas", "0.8"),
    url("sedes", "0.7"),
    url("servicios", "0.7"),
    url("nosotros", "0.5"),
    url("contacto", "0.5"),
    url("blog", "0.6"),
    ...categorias.map((c) => url(`categoria/${c.id}`, "0.8")),
    ...productos.filter((p) => !p.oculto).map((p) => url(`producto/${p.slug}`, "0.7")),
    ...blog.posts.map((p) => url(`blog/${p.slug}`, "0.5")),
    ...documentos.map((tipo) => url(`legal/${tipo}`, "0.3")),
  ];

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${paginas.join("\n")}\n</urlset>`,
    { headers: { "Content-Type": "application/xml; charset=utf-8" } }
  );
}
