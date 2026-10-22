/**
 * Pinta las paginas de favoritos y de volver a comprar, que llegan vacias
 * porque su contenido esta en el navegador de cada persona.
 */
import { listaFavoritos, listaHistorial } from "./favoritos.js";
import { pesos } from "./formato.js";

const escapar = (t) =>
  String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const vacio = (mensaje, base) => `
  <div class="carrito-vacio">
    <p>${mensaje}</p>
    <a class="boton boton-azul" href="${base}catalogo">Ver el catálogo</a>
  </div>`;

export async function montarPaginasGuardadas() {
  const cajaFavoritos = document.getElementById("listaFavoritos");
  const cajaHistorial = document.getElementById("listaHistorial");
  if (!cajaFavoritos && !cajaHistorial) return;

  const base = document.documentElement.dataset.base || "/";

  if (cajaFavoritos) {
    const guardados = listaFavoritos();
    if (guardados.length === 0) {
      cajaFavoritos.innerHTML = vacio(
        "Todavía no has guardado ningún producto. Toca el corazón de cualquier producto para guardarlo aquí.",
        base
      );
    } else {
      const catalogo = await fetch(`${base}datos/catalogo.json`).then((r) => r.json());
      const productos = catalogo.filter((p) => guardados.includes(p.slug));
      const { tarjetaHTML } = await import("./tarjeta.js");
      cajaFavoritos.innerHTML = `<div class="grilla">${productos
        .map((p) => tarjetaHTML(p, base))
        .join("")}</div>`;
      document.dispatchEvent(new CustomEvent("catalogo:pintado"));
    }
  }

  if (cajaHistorial) {
    const pedidos = listaHistorial();
    if (pedidos.length === 0) {
      cajaHistorial.innerHTML = vacio(
        "Aquí aparecerán los pedidos que envíes, para poder repetirlos de un toque.",
        base
      );
      return;
    }

    cajaHistorial.innerHTML = pedidos
      .map((pedido, indice) => {
        const fecha = new Date(pedido.fecha).toLocaleDateString("es-CO", {
          day: "numeric", month: "long", year: "numeric",
        });
        const total = pedido.lineas.reduce((s, l) => s + l.precio * l.cantidad, 0);
        return `
        <article class="pedido-anterior">
          <header>
            <div>
              <strong>Pedido del ${fecha}</strong>
              <span>${pedido.lineas.length} producto${pedido.lineas.length === 1 ? "" : "s"} · ${pesos(total)}</span>
            </div>
            <button type="button" class="boton boton-primario" data-repetir="${indice}">Repetir pedido</button>
          </header>
          <ul>
            ${pedido.lineas
              .map((l) => `<li>${escapar(l.titulo)} <span>x${l.cantidad}</span></li>`)
              .join("")}
          </ul>
        </article>`;
      })
      .join("");

    cajaHistorial.addEventListener("click", (evento) => {
      const boton = evento.target.closest("[data-repetir]");
      if (!boton) return;
      const pedido = pedidos[Number(boton.dataset.repetir)];
      pedido.lineas.forEach((linea) => {
        document.dispatchEvent(
          new CustomEvent("pedido:agregar", { detail: { producto: linea, cantidad: linea.cantidad } })
        );
      });
    });
  }
}
