/**
 * Catálogo ligero que descarga el buscador y el filtrado.
 *
 * Se genera en la compilación a partir de productos.json, quitando lo que el
 * navegador no necesita (descripción larga, datos internos). Así no hay dos
 * archivos que mantener sincronizados: este sale del otro.
 */
import productos from "../../datos/productos.json";

export function GET() {
  const ligero = productos
    .filter((p) => !p.oculto)
    .map((p) => ({
      slug: p.slug,
      titulo: p.titulo,
      precio: p.precio,
      precio_antes: p.precio_antes,
      descuento: p.descuento,
      categoria: p.categoria,
      subcategoria: p.subcategoria,
      subcategoria_nombre: p.subcategoria_nombre,
      marca: p.marca,
      presentacion: p.presentacion,
      stock: p.stock,
      recomendado: p.recomendado,
      imagenes: p.imagenes.slice(0, 1),
    }));

  return new Response(JSON.stringify(ligero), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}
