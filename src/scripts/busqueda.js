/**
 * Busqueda dentro del catalogo.
 *
 * Pensada para como escribe la gente de verdad en un celular: sin tildes, en
 * minusculas, con el nombre a medias y a veces mal. "acetaminofen" tiene que
 * encontrar "ACETAMINOFÉN", y "acetaminofeno" tambien.
 *
 * Son 407 productos, asi que se busca recorriendo la lista. Con este tamano es
 * instantaneo y no hace falta ninguna libreria.
 */
import { sinTildes } from "./formato.js";

/**
 * Palabras que no aportan nada al buscar. Sin esto, "crema para la cara" no
 * encontraria nada, porque exigiria que el producto contuviera "para" y "la".
 */
const VACIAS = new Set([
  "de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas",
  "para", "por", "con", "sin", "en", "y", "o", "a", "al", "que", "mi",
  "me", "te", "se", "es", "algo", "necesito", "quiero", "tengo", "busco",
  "sirve", "bueno", "buena", "mucho", "muy", "hay", "tiene", "cual", "como",
]);

/**
 * Prepara el catalogo para buscar: deja el texto ya normalizado para no
 * repetir el trabajo en cada tecla que pulsa la persona.
 */
export function construirIndice(productos, sinonimos = {}) {
  const tabla = new Map(
    Object.entries(sinonimos)
      .filter(([clave]) => !clave.startsWith("_"))
      .map(([clave, valores]) => [sinTildes(clave), valores.map(sinTildes)])
  );

  return productos.map((producto) => ({
    producto,
    texto: sinTildes(
      [
        producto.titulo,
        producto.marca,
        producto.categoria,
        producto.subcategoria,
        producto.presentacion,
      ]
        .filter(Boolean)
        .join(" ")
        .replace(/-/g, " ")
    ),
    titulo: sinTildes(producto.titulo),
    tabla,
  }));
}

/**
 * Traduce lo que escribe la persona a lo que de verdad esta en el catalogo.
 * Nadie busca "winny": busca "panales". Ver src/datos/sinonimos.json.
 */
function expandir(palabra, tabla) {
  const equivalentes = tabla?.get(palabra);
  return equivalentes ? [palabra, ...equivalentes] : [palabra];
}

/**
 * Distancia de edicion con un tope.
 *
 * Cuenta como UN solo error el intercambio de dos letras seguidas ("nivae" por
 * "nivea"), que es el error de tipeo mas comun de todos. El algoritmo clasico
 * lo cobraria como dos cambios y dejaria de encontrar el producto.
 *
 * Solo interesa saber si dos palabras estan a uno o dos cambios; si estan mas
 * lejos da igual cuanto, y cortar por lo sano evita recorrer sin necesidad.
 */
function distancia(a, b, tope) {
  if (Math.abs(a.length - b.length) > tope) return tope + 1;

  let dosAtras = null;
  let anterior = Array.from({ length: b.length + 1 }, (_, i) => i);

  for (let i = 1; i <= a.length; i++) {
    const actual = [i];
    let mejorFila = i;
    for (let j = 1; j <= b.length; j++) {
      const coste = a[i - 1] === b[j - 1] ? 0 : 1;
      let valor = Math.min(actual[j - 1] + 1, anterior[j] + 1, anterior[j - 1] + coste);

      // Dos letras seguidas intercambiadas: un solo error.
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        valor = Math.min(valor, dosAtras[j - 2] + 1);
      }

      actual[j] = valor;
      mejorFila = Math.min(mejorFila, valor);
    }
    if (mejorFila > tope) return tope + 1;
    dosAtras = anterior;
    anterior = actual;
  }
  return anterior[b.length];
}

/** Cuantos cambios se le perdonan a una palabra segun su largo. */
const toleranciaPara = (palabra) =>
  palabra.length <= 4 ? 0 : palabra.length <= 7 ? 1 : 2;

/**
 * Puntua que tan bien encaja una palabra buscada en un producto.
 * Cuanto mas alto, mas arriba sale.
 */
function puntuarPalabra(entrada, palabra) {
  if (entrada.titulo.startsWith(palabra)) return 100;

  const posicion = entrada.texto.indexOf(palabra);
  if (posicion === 0) return 90;
  // Empieza una palabra dentro del texto: "milk" en "body milk".
  if (posicion > 0 && entrada.texto[posicion - 1] === " ") return 70;
  if (posicion > 0) return 45;

  const tolerancia = toleranciaPara(palabra);
  if (tolerancia === 0) return 0;

  // Buscar la palabra del producto mas parecida a la escrita.
  let mejor = tolerancia + 1;
  for (const suya of entrada.texto.split(" ")) {
    if (!suya) continue;
    mejor = Math.min(mejor, distancia(palabra, suya, tolerancia));
    if (mejor === 0) break;
  }
  if (mejor > tolerancia) return 0;
  return 30 - mejor * 8;
}

export function buscar(indice, consulta, opciones = {}) {
  const { limite = 40 } = opciones;

  const palabras = sinTildes(consulta)
    .trim()
    .split(/\s+/)
    .filter((palabra) => palabra && !VACIAS.has(palabra));
  if (palabras.length === 0) return [];

  const resultados = [];
  for (const entrada of indice) {
    let total = 0;
    // Todas las palabras escritas tienen que aparecer de alguna forma: quien
    // busca "crema almendras" no quiere todas las cremas del catalogo.
    for (const palabra of palabras) {
      // Basta con que encaje la palabra escrita o alguno de sus equivalentes.
      let punto = 0;
      for (const variante of expandir(palabra, entrada.tabla)) {
        punto = Math.max(punto, puntuarPalabra(entrada, variante));
        if (punto >= 90) break;
      }
      if (punto === 0) {
        total = 0;
        break;
      }
      total += punto;
    }
    if (total > 0) resultados.push({ producto: entrada.producto, punto: total });
  }

  return resultados
    .sort((a, b) => b.punto - a.punto || a.producto.precio - b.producto.precio)
    .slice(0, limite)
    .map((r) => r.producto);
}
