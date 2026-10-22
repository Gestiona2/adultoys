/**
 * Panel del carrito: lo que se ve y se toca.
 *
 * La logica del pedido vive en pedido.js. El pedido se guarda en el navegador
 * para que no se pierda al cambiar de pagina ni al volver mas tarde.
 */
import { crearPedido, armarMensaje, enlaceWhatsApp } from "./pedido.js";
import { pesos } from "./formato.js";

const CLAVE = "adultoyss-pedido";
const HISTORIAL = "adultoyss-historial";

const guardar = (lineas) => {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(lineas));
  } catch {
    /* ventana privada: el carrito dura lo que la visita */
  }
};

const recuperar = () => {
  try {
    return JSON.parse(localStorage.getItem(CLAVE) || "[]");
  } catch {
    return [];
  }
};

const escapar = (texto) =>
  String(texto).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );

export function montarCarrito() {
  const panel = document.getElementById("carrito");
  const cuerpo = document.getElementById("carritoCuerpo");
  if (!panel || !cuerpo) return;

  const base = document.documentElement.dataset.base || "/";
  const whatsapp = panel.dataset.whatsapp || "";

  const fondo = document.getElementById("carritoFondo");
  const barra = document.getElementById("barraPago");
  const globoCarrito = document.querySelector('[data-contador="carrito"] .accion-globo');

  let alCambiar = () => {};
  const pedido = crearPedido();
  alCambiar = (p) => {
    guardar(p.exportar());
    pintarContadores(p);
    if (!panel.hidden) pintarPanel(p);
  };
  pedido.alCambiar = alCambiar;

  /* ---------- contadores ---------- */
  function pintarContadores(p) {
    const unidades = p.unidades();
    if (globoCarrito) {
      globoCarrito.textContent = unidades;
      globoCarrito.hidden = unidades === 0;
    }
    barra.hidden = unidades === 0;
    if (unidades > 0) {
      document.getElementById("barraPagoTotal").textContent = pesos(p.total());
      document.getElementById("barraPagoItems").textContent =
        unidades === 1 ? "1 producto" : `${unidades} productos`;
    }
  }

  /* ---------- panel ---------- */
  function leerFormulario() {
    const formulario = cuerpo.querySelector("#formPedido");
    if (!formulario) return {};
    return Object.fromEntries(new FormData(formulario));
  }

  function pintarPanel(p) {
    const lineas = p.lineas();
    const previos = leerFormulario();

    if (lineas.length === 0) {
      cuerpo.innerHTML = `
        <div class="carrito-vacio">
          <p>Tu pedido está vacío.</p>
          <p class="carrito-vacio-texto">Explora el catálogo y agrega lo que te guste. El pedido se guarda en este navegador.</p>
          <a class="boton boton-primario" href="${base}catalogo">Ver el catálogo</a>
        </div>`;
      return;
    }

    cuerpo.innerHTML = `
      <div class="carrito-columnas">
        <div class="carrito-lista">
          ${lineas
            .map(
              (linea) => `
            <article class="carrito-linea" data-slug="${linea.slug}">
              <img src="${base}img/${linea.imagen}" alt="" width="64" height="64" loading="lazy">
              <div class="carrito-linea-datos">
                <a href="${base}producto/${linea.slug}">${escapar(linea.titulo)}</a>
                <span class="carrito-linea-unitario">${pesos(linea.precio)} c/u</span>
              </div>
              <div class="carrito-cantidad">
                <button type="button" data-menos="${linea.slug}" aria-label="Quitar una unidad">−</button>
                <span aria-live="polite">${linea.cantidad}</span>
                <button type="button" data-mas="${linea.slug}" aria-label="Agregar una unidad">+</button>
              </div>
              <strong class="carrito-linea-total">${pesos(linea.precio * linea.cantidad)}</strong>
              <button type="button" class="carrito-quitar" data-quitar="${linea.slug}"
                      aria-label="Quitar ${escapar(linea.titulo)} del pedido">×</button>
            </article>`
            )
            .join("")}
        </div>

        <form class="carrito-datos" id="formPedido" novalidate>
          <h3>Datos de entrega</h3>

          <label>¿Cómo lo quieres recibir?
            <select name="entrega" id="campoEntrega">
              ${["Envío a domicilio", "Recogida en punto"].map((opcion) => `
                <option${(previos.entrega || "Envío a domicilio") === opcion ? " selected" : ""}>${opcion}</option>`).join("")}
            </select>
          </label>

          <label>Nombre y apellido
            <input name="nombre" required autocomplete="name" placeholder="Ana Gómez" value="${escapar(previos.nombre || "")}">
          </label>
          <label>Teléfono / WhatsApp
            <input name="telefono" required inputmode="tel" autocomplete="tel" placeholder="300 123 4567" value="${escapar(previos.telefono || "")}">
          </label>

          <div data-domicilio${(previos.entrega || "Envío a domicilio") === "Recogida en punto" ? " hidden" : ""}>
            <label>Dirección
              <input name="direccion" autocomplete="street-address" placeholder="Cra 6 # 4-12, apto 302" value="${escapar(previos.direccion || "")}">
            </label>
            <div class="carrito-fila">
              <label>Ciudad
                <input name="ciudad" autocomplete="address-level2" placeholder="Tocancipá" value="${escapar(previos.ciudad || "")}">
              </label>
              <label>Barrio <span class="opcional">(opcional)</span>
                <input name="barrio" autocomplete="address-level3" placeholder="Centro" value="${escapar(previos.barrio || "")}">
              </label>
            </div>
            <label>Indicaciones <span class="opcional">(opcional)</span>
              <input name="indicaciones" placeholder="Torre 2, timbre 301" value="${escapar(previos.indicaciones || "")}">
            </label>
          </div>

          <label>Forma de pago
            <select name="pago" id="campoPago">
              ${["Efectivo contraentrega", "Transferencia (Nequi / Daviplata)", "Acordar por WhatsApp"].map((opcion) => `
                <option${(previos.pago || "Efectivo contraentrega") === opcion ? " selected" : ""}>${opcion}</option>`).join("")}
            </select>
          </label>
          <label data-vueltas${(previos.pago || "Efectivo contraentrega") === "Efectivo contraentrega" ? "" : " hidden"}>¿De cuánto quieres las vueltas? <span class="opcional">(opcional)</span>
            <input name="vueltas" inputmode="numeric" placeholder="$50.000 o exacto" value="${escapar(previos.vueltas || "")}">
          </label>
          <label>Nota para la entrega <span class="opcional">(opcional)</span>
            <textarea name="nota" rows="2" placeholder="Llamar al llegar, no tocar el timbre">${escapar(previos.nota || "")}</textarea>
          </label>

          <div class="carrito-total">
            <p class="carrito-envio carrito-envio-listo">Envío estándar gratis · 2 a 3 días hábiles</p>
            <div class="carrito-total-linea">
              <span>Total</span>
              <strong>${pesos(p.total())}</strong>
            </div>
            <button type="submit" class="boton boton-primario carrito-enviar">
              Enviar pedido por WhatsApp
            </button>
            <p class="carrito-nota">
              Al enviar se abre WhatsApp con tu pedido escrito. Confirmamos disponibilidad,
              pago y tiempo de entrega antes de despachar. Empaque neutro.
            </p>
          </div>
        </form>
      </div>`;

    const formulario = cuerpo.querySelector("#formPedido");
    formulario.addEventListener("submit", enviarPedido);

    const campoPago = formulario.querySelector("#campoPago");
    const campoVueltas = formulario.querySelector("[data-vueltas]");
    campoPago?.addEventListener("change", () => {
      if (campoVueltas) campoVueltas.hidden = campoPago.value !== "Efectivo contraentrega";
    });

    const campoEntrega = formulario.querySelector("#campoEntrega");
    const bloqueDomicilio = formulario.querySelector("[data-domicilio]");
    campoEntrega?.addEventListener("change", () => {
      const recoge = campoEntrega.value === "Recogida en punto";
      if (bloqueDomicilio) bloqueDomicilio.hidden = recoge;
      const direccion = formulario.querySelector('[name="direccion"]');
      if (direccion) direccion.required = !recoge;
    });
    const direccion = formulario.querySelector('[name="direccion"]');
    if (direccion) direccion.required = (previos.entrega || "Envío a domicilio") !== "Recogida en punto";
  }

  /* ---------- enviar ---------- */
  function enviarPedido(evento) {
    evento.preventDefault();
    const formulario = evento.target;
    const datos = Object.fromEntries(new FormData(formulario));

    const faltantes = ["nombre", "telefono"];
    if (datos.entrega !== "Recogida en punto") {
      faltantes.push("direccion", "ciudad");
    }
    const sinLlenar = faltantes.filter((campo) => !String(datos[campo] || "").trim());
    if (sinLlenar.length > 0) {
      const campo = formulario.elements[sinLlenar[0]];
      campo.focus();
      campo.classList.add("campo-falta");
      avisar("Falta " + {
        nombre: "tu nombre",
        telefono: "tu teléfono",
        direccion: "la dirección",
        ciudad: "la ciudad",
      }[sinLlenar[0]]);
      return;
    }

    const mensaje = armarMensaje(pedido, datos);
    window.open(enlaceWhatsApp(whatsapp, mensaje), "_blank", "noopener");

    guardarEnHistorial(pedido);
    avisar("Pedido enviado. Revisa WhatsApp.");
  }

  function guardarEnHistorial(p) {
    try {
      const historial = JSON.parse(localStorage.getItem(HISTORIAL) || "[]");
      historial.unshift({ fecha: new Date().toISOString(), lineas: p.exportar() });
      localStorage.setItem(HISTORIAL, JSON.stringify(historial.slice(0, 20)));
    } catch {
      /* sin historial, el pedido igual se envio */
    }
  }

  /* ---------- abrir y cerrar ---------- */
  let ultimoFoco = null;

  const abrir = () => {
    ultimoFoco = document.activeElement;
    panel.hidden = false;
    fondo.hidden = false;
    requestAnimationFrame(() => panel.classList.add("abierto"));
    panel.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    pintarPanel(pedido);
    panel.querySelector("#cerrarCarrito")?.focus();
  };

  const cerrar = () => {
    panel.classList.remove("abierto");
    panel.setAttribute("aria-hidden", "true");
    fondo.hidden = true;
    document.body.style.overflow = "";
    setTimeout(() => (panel.hidden = true), 280);
    ultimoFoco?.focus();
  };

  document.getElementById("abrirCarrito")?.addEventListener("click", abrir);
  document.getElementById("barraPagoBoton")?.addEventListener("click", abrir);
  document.getElementById("cerrarCarrito")?.addEventListener("click", cerrar);
  fondo?.addEventListener("click", cerrar);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panel.hidden) cerrar();
  });

  /* ---------- botones de agregar ---------- */
  document.addEventListener("click", (evento) => {
    const agregar = evento.target.closest("[data-agregar]");
    if (agregar) {
      pedido.agregar(
        {
          slug: agregar.dataset.agregar,
          titulo: agregar.dataset.titulo,
          precio: Number(agregar.dataset.precio),
          imagen: agregar.dataset.imagen,
        },
        1
      );
      avisar(`${agregar.dataset.titulo} agregado`);
      return;
    }

    const mas = evento.target.closest("[data-mas]");
    if (mas) {
      const linea = pedido.lineas().find((l) => l.slug === mas.dataset.mas);
      if (linea) pedido.cambiarCantidad(mas.dataset.mas, linea.cantidad + 1);
      return;
    }

    const menos = evento.target.closest("[data-menos]");
    if (menos) {
      const linea = pedido.lineas().find((l) => l.slug === menos.dataset.menos);
      if (linea) pedido.cambiarCantidad(menos.dataset.menos, linea.cantidad - 1);
      return;
    }

    const quitar = evento.target.closest("[data-quitar]:not([data-valor])");
    if (quitar && quitar.classList.contains("carrito-quitar")) {
      pedido.quitar(quitar.dataset.quitar);
    }
  });

  /* ---------- aviso flotante ---------- */
  let temporizadorAviso = null;
  function avisar(texto) {
    let aviso = document.getElementById("aviso");
    if (!aviso) {
      aviso = document.createElement("div");
      aviso.id = "aviso";
      aviso.className = "aviso";
      aviso.setAttribute("role", "status");
      document.body.appendChild(aviso);
    }
    aviso.textContent = texto;
    aviso.classList.add("visible");
    clearTimeout(temporizadorAviso);
    temporizadorAviso = setTimeout(() => aviso.classList.remove("visible"), 2800);
  }

  document.addEventListener("pedido:agregar", (evento) => {
    const { producto, cantidad } = evento.detail;
    pedido.agregar(producto, cantidad || 1);
    avisar("Productos agregados a tu pedido");
  });

  pedido.importar(recuperar());
  pintarContadores(pedido);
}
