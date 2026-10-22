/**
 * Formateo compartido por toda la tienda.
 *
 * Los precios se guardan como enteros de pesos (62900) y se convierten a texto
 * solo al mostrarlos. Guardarlos ya formateados obligaria a desarmar la cadena
 * cada vez que hay que ordenar, filtrar o sumar.
 */

const FORMATO_PESOS = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

/** 62900 -> "$62.900". Un valor vacio devuelve cadena vacia, nunca "NaN". */
export function pesos(valor) {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return "";
  // Intl mete un espacio estrecho despues del simbolo que no queremos mostrar.
  return FORMATO_PESOS.format(valor).replace(/\s/g, "");
}

/**
 * Baja a minusculas y quita tildes y diereses, para que el buscador encuentre
 * "ACETAMINOFÉN" cuando alguien escribe "acetaminofen", que es lo que pasa
 * siempre en un celular.
 */
export function sinTildes(texto) {
  return String(texto ?? "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();
}

/** Porcentaje de ahorro, o null si no hay oferta real. */
export function porcentajeAhorro(precioAntes, precio) {
  if (!precioAntes || !precio || precioAntes <= precio) return null;
  return Math.round(((precioAntes - precio) / precioAntes) * 100);
}
