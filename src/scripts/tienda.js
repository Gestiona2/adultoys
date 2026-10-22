/**
 * Arranque de la tienda: lo que necesita cualquier pagina.
 *
 * Se importa una sola vez desde el layout. Cada pieza vive en su modulo y aqui
 * solo se conectan, para que anadir una funcion no engorde este archivo.
 */
import { montarCarrito } from "./carrito.js";
import { montarBuscador } from "./buscador.js";
import { montarFavoritos } from "./favoritos.js";
import { montarCarrusel } from "./carrusel.js";
import { montarCatalogo } from "./filtros.js";
import { montarPaginasGuardadas } from "./paginas-guardadas.js";

const listo = (fn) =>
  document.readyState === "loading"
    ? document.addEventListener("DOMContentLoaded", fn, { once: true })
    : fn();

listo(() => {
  montarCarrito();
  montarBuscador();
  montarFavoritos();
  montarCarrusel();
  montarCatalogo();
  montarPaginasGuardadas();

  // Menu en pantallas pequenas
  const boton = document.getElementById("abrirMenu");
  boton?.addEventListener("click", () => {
    const abierto = document.body.classList.toggle("menu-abierto");
    boton.setAttribute("aria-expanded", String(abierto));
  });
});
