/**
 * Favoritos y "volver a comprar".
 *
 * Los dos viven solo en el navegador de cada persona: no hay cuentas ni
 * servidor. Es una decision deliberada, no una limitacion: pedir registro en
 * una tienda erotica espanta mas clientes de los que fideliza.
 *
 * Consecuencia que hay que conocer: si alguien entra desde otro telefono, no
 * ve sus favoritos. Esta anotado en conocimiento_generado/LIMITES.md.
 */
const CLAVE = "adultoyss-favoritos";

const leer = () => {
  try {
    const guardados = JSON.parse(localStorage.getItem(CLAVE) || "[]");
    return new Set(Array.isArray(guardados) ? guardados : []);
  } catch {
    return new Set();
  }
};

const escribir = (conjunto) => {
  try {
    localStorage.setItem(CLAVE, JSON.stringify([...conjunto]));
  } catch {
    /* ventana privada: los favoritos duran lo que la visita */
  }
};

export function montarFavoritos() {
  let favoritos = leer();

  const pintarBotones = () => {
    document.querySelectorAll("[data-favorito]").forEach((boton) => {
      boton.setAttribute("aria-pressed", String(favoritos.has(boton.dataset.favorito)));
    });
  };

  const pintarContador = () => {
    const globo = document.querySelector('[data-contador="favoritos"] .accion-globo');
    if (!globo) return;
    globo.textContent = favoritos.size;
    globo.hidden = favoritos.size === 0;
  };

  document.addEventListener("click", (evento) => {
    const boton = evento.target.closest("[data-favorito]");
    if (!boton) return;
    evento.preventDefault();

    const slug = boton.dataset.favorito;
    if (favoritos.has(slug)) {
      favoritos.delete(slug);
    } else {
      favoritos.add(slug);
    }
    escribir(favoritos);
    pintarBotones();
    pintarContador();
  });

  // Las tarjetas que pinta el catalogo aparecen despues: hay que repintarlas.
  document.addEventListener("catalogo:pintado", pintarBotones);

  pintarBotones();
  pintarContador();
}

/** Slugs guardados, para las paginas de favoritos y de volver a comprar. */
export function listaFavoritos() {
  return [...leer()];
}

export function listaHistorial() {
  try {
    return JSON.parse(localStorage.getItem("adultoyss-historial") || "[]");
  } catch {
    return [];
  }
}
