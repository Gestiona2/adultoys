/**
 * El pedido: que hay dentro, cuanto suma y como se convierte en un mensaje
 * de WhatsApp.
 *
 * Esta separado de la interfaz para poder probarlo sin navegador.
 */
import { pesos } from "./formato.js";

export function crearPedido() {
  let lineas = [];

  const api = {
    lineas: () => lineas.map((l) => ({ ...l })),

    total: () => lineas.reduce((suma, l) => suma + l.precio * l.cantidad, 0),

    unidades: () => lineas.reduce((suma, l) => suma + l.cantidad, 0),

    agregar(producto, cantidad = 1) {
      const existente = lineas.find((l) => l.slug === producto.slug);
      if (existente) {
        existente.cantidad += cantidad;
      } else {
        lineas.push({
          slug: producto.slug,
          titulo: producto.titulo,
          precio: Number(producto.precio),
          imagen: producto.imagen,
          cantidad,
        });
      }
      avisar();
      return api;
    },

    cambiarCantidad(slug, cantidad) {
      const linea = lineas.find((l) => l.slug === slug);
      if (!linea) return api;
      if (cantidad <= 0) {
        lineas = lineas.filter((l) => l.slug !== slug);
      } else {
        linea.cantidad = cantidad;
      }
      avisar();
      return api;
    },

    quitar: (slug) => api.cambiarCantidad(slug, 0),

    vaciar() {
      lineas = [];
      avisar();
      return api;
    },

    exportar: () => lineas.map((l) => ({ ...l })),
    importar(guardadas) {
      if (Array.isArray(guardadas)) {
        lineas = guardadas.filter(
          (l) => l && l.slug && Number.isFinite(Number(l.precio)) && l.cantidad > 0
        );
        avisar();
      }
      return api;
    },
  };

  function avisar() {
    try {
      api.alCambiar?.(api);
    } catch {
      /* la interfaz no debe romper el pedido */
    }
  }

  return api;
}

/**
 * Arma el mensaje que se envia por WhatsApp. Se escribe pensando en quien lo
 * recibe: tiene que poder leerlo y despacharlo sin preguntar nada.
 */
export function armarMensaje(pedido, datos) {
  const lineas = pedido.lineas();
  if (lineas.length === 0) throw new Error("El pedido está vacío");

  const partes = ["*Nuevo pedido — Adultoyss*", ""];

  for (const linea of lineas) {
    partes.push(`• ${linea.titulo}`);
    partes.push(`   x${linea.cantidad} · ${pesos(linea.precio * linea.cantidad)}`);
  }

  partes.push("");
  partes.push(`*Total: ${pesos(pedido.total())}*`);
  partes.push("Envío estándar gratis");
  partes.push("");
  partes.push("*Datos de entrega*");
  partes.push(`Entrega: ${datos.entrega || "Envío a domicilio"}`);
  partes.push(`Nombre: ${datos.nombre}`);
  partes.push(`Teléfono: ${datos.telefono}`);
  if (datos.entrega !== "Recogida en punto") {
    partes.push(`Dirección: ${datos.direccion}`);
    if (datos.ciudad) partes.push(`Ciudad: ${datos.ciudad}`);
    if (datos.barrio) partes.push(`Barrio: ${datos.barrio}`);
    if (datos.indicaciones) partes.push(`Indicaciones: ${datos.indicaciones}`);
  }
  if (datos.pago === "Efectivo contraentrega" && datos.vueltas) {
    partes.push(`Pago: Efectivo contraentrega (vueltas de ${datos.vueltas})`);
  } else {
    partes.push(`Pago: ${datos.pago}`);
  }
  if (datos.nota) partes.push(`Nota: ${datos.nota}`);
  partes.push("");
  partes.push("Quiero confirmar disponibilidad y tiempo de entrega. ¡Gracias!");

  return partes.join("\n");
}

/**
 * Deja el numero como lo entiende WhatsApp: solo digitos y con el pais (57).
 */
export function numeroWhatsApp(numero) {
  const digitos = String(numero || "").replace(/\D/g, "");
  if (!digitos) return "";
  return digitos.startsWith("57") ? digitos : `57${digitos}`;
}

export function enlaceWhatsApp(numero, mensaje) {
  return `https://wa.me/${numeroWhatsApp(numero)}?text=${encodeURIComponent(mensaje)}`;
}
