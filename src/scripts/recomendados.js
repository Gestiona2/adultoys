/**
 * Elige los productos de la fila "Recomendaciones para ti".
 *
 * El orden, de mayor a menor prioridad:
 *   1. Los marcados a mano con "recomendado": true en productos.json.
 *   2. Los que tienen mayor ahorro real en pesos.
 *   3. El resto, en un orden variado pero estable.
 *
 * Nunca entran agotados ni productos sin precio. `excluir` evita que un
 * producto salga dos veces en la misma pantalla.
 */
function semilla(texto) {
  let valor = 0;
  for (let i = 0; i < texto.length; i++) {
    valor = (valor * 31 + texto.charCodeAt(i)) % 2147483647;
  }
  return valor;
}

const ahorro = (producto) =>
  producto.precio_antes && producto.precio_antes > producto.precio
    ? producto.precio_antes - producto.precio
    : 0;

export function elegirRecomendados(productos, cantidad, opciones = {}) {
  const { excluir = new Set() } = opciones;

  const elegibles = productos.filter(
    (p) => !p.oculto && !excluir.has(p.slug) && p.stock !== false && p.precio > 0
  );

  const marcados = elegibles.filter((p) => p.recomendado === true);
  const resto = elegibles.filter((p) => p.recomendado !== true);

  const conAhorro = resto
    .filter((p) => ahorro(p) > 0)
    .sort((a, b) => ahorro(b) - ahorro(a));

  const sinAhorro = resto
    .filter((p) => ahorro(p) === 0)
    .sort((a, b) => semilla(a.slug) - semilla(b.slug));

  const vistos = new Set();
  const salida = [];
  for (const producto of [...marcados, ...conAhorro, ...sinAhorro]) {
    if (salida.length >= cantidad) break;
    if (vistos.has(producto.slug)) continue;
    vistos.add(producto.slug);
    salida.push(producto);
  }
  return salida;
}
