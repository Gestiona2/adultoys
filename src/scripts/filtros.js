/**
 * Filtrado y orden del catalogo, en el navegador.
 *
 * El estado vive en la direccion de la pagina. Eso resuelve tres cosas de una:
 * el filtro se puede compartir por WhatsApp, el boton atras del navegador
 * funciona, y si alguien recarga no pierde lo que habia filtrado.
 */
import { construirIndice, buscar } from "./busqueda.js";
import { pesos } from "./formato.js";
import { tarjetaHTML as tarjeta } from "./tarjeta.js";

const POR_TANDA = 24;

const ORDENES = {
  "precio-asc": (a, b) => a.precio - b.precio,
  "precio-desc": (a, b) => b.precio - a.precio,
  descuento: (a, b) => (b.descuento || 0) - (a.descuento || 0),
  nombre: (a, b) => a.titulo.localeCompare(b.titulo, "es"),
};

const escapar = (texto) =>
  String(texto).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );

export async function montarCatalogo() {
  const contenedor = document.getElementById("catalogoResultados");
  if (!contenedor) return;

  const base = document.documentElement.dataset.base || "/";
  const [productos, sinonimos] = await Promise.all([
    fetch(`${base}datos/catalogo.json`).then((r) => r.json()),
    fetch(`${base}datos/sinonimos.json`).then((r) => r.json()).catch(() => ({})),
  ]);
  const indice = construirIndice(productos, sinonimos);

  const resumen = document.getElementById("catalogoResumen");
  const fichas = document.getElementById("fichasActivas");
  const botonMas = document.getElementById("verMas");
  const selectOrden = document.getElementById("ordenar");
  const filtros = document.getElementById("filtros");

  let mostrados = 0;
  let filtrados = [];

  /* ---------- la direccion es la fuente de la verdad ---------- */
  const leerUrl = () => new URLSearchParams(location.search);

  const escribirUrl = (parametros) => {
    const texto = parametros.toString();
    history.replaceState(null, "", texto ? `?${texto}` : location.pathname);
  };

  function aplicarUrlAControles() {
    const p = leerUrl();
    const cat = p.get("cat") || "";
    filtros.querySelectorAll('input[name="cat"]').forEach((r) => (r.checked = r.value === cat));
    document.getElementById("precioMin").value = p.get("min") || "";
    document.getElementById("precioMax").value = p.get("max") || "";
    ["marca", "sub"].forEach((campo) => {
      const activos = p.getAll(campo);
      filtros
        .querySelectorAll(`input[name="${campo}"]`)
        .forEach((c) => (c.checked = activos.includes(c.value)));
    });
    filtros.querySelector('input[name="oferta"]').checked = p.get("oferta") === "1";
    filtros.querySelector('input[name="disponible"]').checked = p.get("disponible") === "1";
    selectOrden.value = p.get("orden") || "relevancia";
  }

  function leerControles() {
    const p = new URLSearchParams();
    const cat = filtros.querySelector('input[name="cat"]:checked')?.value;
    if (cat) p.set("cat", cat);

    const min = document.getElementById("precioMin").value;
    const max = document.getElementById("precioMax").value;
    if (min) p.set("min", min);
    if (max) p.set("max", max);

    ["marca", "sub"].forEach((campo) =>
      filtros
        .querySelectorAll(`input[name="${campo}"]:checked`)
        .forEach((c) => p.append(campo, c.value))
    );

    if (filtros.querySelector('input[name="oferta"]').checked) p.set("oferta", "1");
    if (filtros.querySelector('input[name="disponible"]').checked) p.set("disponible", "1");
    if (selectOrden.value !== "relevancia") p.set("orden", selectOrden.value);

    const consulta = leerUrl().get("q");
    if (consulta) p.set("q", consulta);
    return p;
  }

  /* ---------- filtrar ---------- */
  function calcular(p) {
    const consulta = p.get("q");
    let lista = consulta ? buscar(indice, consulta, { limite: 500 }) : [...productos];

    const cat = p.get("cat");
    if (cat) lista = lista.filter((x) => x.categoria === cat);

    const min = Number(p.get("min")) || 0;
    const max = Number(p.get("max")) || Infinity;
    lista = lista.filter((x) => x.precio >= min && x.precio <= max);

    const marcas = p.getAll("marca");
    if (marcas.length) lista = lista.filter((x) => marcas.includes(x.marca));

    const subs = p.getAll("sub");
    if (subs.length) lista = lista.filter((x) => subs.includes(x.subcategoria));

    if (p.get("oferta") === "1") lista = lista.filter((x) => x.descuento);
    if (p.get("disponible") === "1") lista = lista.filter((x) => x.stock !== false);

    const orden = p.get("orden");
    // Con busqueda, "relevancia" es el orden que ya trae el buscador.
    if (orden && ORDENES[orden]) lista.sort(ORDENES[orden]);

    return lista;
  }

  /* ---------- pintar ---------- */
  function pintarTanda() {
    const tanda = filtrados.slice(mostrados, mostrados + POR_TANDA);
    const grilla = contenedor.querySelector(".grilla");
    if (grilla) grilla.insertAdjacentHTML("beforeend", tanda.map((x) => tarjeta(x, base)).join(""));
    mostrados += tanda.length;
    botonMas.hidden = mostrados >= filtrados.length;
    document.dispatchEvent(new CustomEvent("catalogo:pintado"));
  }

  function pintarTodo() {
    mostrados = 0;
    if (filtrados.length === 0) {
      const consulta = leerUrl().get("q");
      contenedor.innerHTML = `<p class="grilla-vacia">
        No encontramos productos${consulta ? ` para "${escapar(consulta)}"` : ""} con esos filtros.
      </p>`;
      botonMas.hidden = true;
    } else {
      contenedor.innerHTML = '<div class="grilla"></div>';
      pintarTanda();
    }

    resumen.textContent =
      filtrados.length === productos.length
        ? `${productos.length} productos`
        : `${filtrados.length} de ${productos.length} productos`;

    pintarFichas();
  }

  function pintarFichas() {
    const p = leerUrl();
    const etiquetas = [];
    if (p.get("q")) etiquetas.push(["q", `“${p.get("q")}”`]);
    if (p.get("cat")) etiquetas.push(["cat", p.get("cat").replace(/-/g, " ")]);
    p.getAll("marca").forEach((m) => etiquetas.push(["marca", m, m]));
    p.getAll("sub").forEach((s) => etiquetas.push(["sub", s.replace(/-/g, " "), s]));
    if (p.get("oferta")) etiquetas.push(["oferta", "en oferta"]);
    if (p.get("disponible")) etiquetas.push(["disponible", "disponibles"]);
    if (p.get("min") || p.get("max")) {
      etiquetas.push(["precio", `${pesos(Number(p.get("min")) || 0)} – ${p.get("max") ? pesos(Number(p.get("max"))) : "∞"}`]);
    }

    fichas.innerHTML = etiquetas
      .map(
        ([campo, texto, valor]) =>
          `<button type="button" class="ficha-filtro" data-quitar="${campo}"
             ${valor ? `data-valor="${escapar(valor)}"` : ""}>
             ${escapar(texto)} <span aria-hidden="true">×</span>
             <span class="visualmente-oculto">Quitar filtro</span>
           </button>`
      )
      .join("");
  }

  function actualizar({ desdeControles = true } = {}) {
    if (desdeControles) escribirUrl(leerControles());
    filtrados = calcular(leerUrl());
    pintarTodo();
  }

  /* ---------- eventos ---------- */
  filtros.addEventListener("change", () => actualizar());
  filtros.addEventListener("input", (e) => {
    if (e.target.type === "number") {
      clearTimeout(filtros._espera);
      filtros._espera = setTimeout(() => actualizar(), 400);
    }
  });
  selectOrden.addEventListener("change", () => actualizar());
  botonMas.addEventListener("click", pintarTanda);

  document.getElementById("limpiarFiltros").addEventListener("click", () => {
    history.replaceState(null, "", location.pathname);
    aplicarUrlAControles();
    actualizar({ desdeControles: false });
  });

  fichas.addEventListener("click", (evento) => {
    const boton = evento.target.closest("[data-quitar]");
    if (!boton) return;
    const p = leerUrl();
    const campo = boton.dataset.quitar;
    if (campo === "precio") {
      p.delete("min");
      p.delete("max");
    } else if (boton.dataset.valor) {
      const quedan = p.getAll(campo).filter((v) => v !== boton.dataset.valor);
      p.delete(campo);
      quedan.forEach((v) => p.append(campo, v));
    } else {
      p.delete(campo);
    }
    escribirUrl(p);
    aplicarUrlAControles();
    actualizar({ desdeControles: false });
  });

  // Panel de filtros en celular
  const fondo = document.getElementById("filtrosFondo");
  const abrir = () => {
    filtros.classList.add("abierto");
    fondo.hidden = false;
  };
  const cerrar = () => {
    filtros.classList.remove("abierto");
    fondo.hidden = true;
  };
  document.getElementById("abrirFiltros")?.addEventListener("click", abrir);
  document.getElementById("cerrarFiltros")?.addEventListener("click", cerrar);
  fondo?.addEventListener("click", cerrar);

  aplicarUrlAControles();
  actualizar({ desdeControles: false });
}
