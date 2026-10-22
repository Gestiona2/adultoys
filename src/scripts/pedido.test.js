import test from "node:test";
import assert from "node:assert/strict";

import { crearPedido, armarMensaje, numeroWhatsApp, enlaceWhatsApp } from "./pedido.js";

const PRODUCTO = {
  slug: "bala-afrodita",
  titulo: "Bala Afrodita",
  precio: 65000,
  imagen: "productos/bala-afrodita.webp",
};

test("el pedido suma cantidades y total", () => {
  const pedido = crearPedido();
  pedido.agregar(PRODUCTO);
  pedido.agregar(PRODUCTO, 2);
  assert.equal(pedido.unidades(), 3);
  assert.equal(pedido.total(), 195000);
  assert.equal(pedido.lineas().length, 1);
});

test("cambiar cantidad a cero quita la linea", () => {
  const pedido = crearPedido().agregar(PRODUCTO).cambiarCantidad(PRODUCTO.slug, 0);
  assert.equal(pedido.lineas().length, 0);
  assert.equal(pedido.total(), 0);
});

test("el mensaje de WhatsApp lleva productos, total y datos", () => {
  const pedido = crearPedido().agregar(PRODUCTO, 2);
  const mensaje = armarMensaje(pedido, {
    nombre: "Ana Gómez",
    telefono: "3001234567",
    direccion: "Calle 1 #2-3",
    ciudad: "Tocancipá",
    entrega: "Envío a domicilio",
    pago: "Efectivo contraentrega",
  });
  assert.match(mensaje, /Nuevo pedido/);
  assert.match(mensaje, /Bala Afrodita/);
  assert.match(mensaje, /x2/);
  assert.match(mensaje, /\$130\.000/);
  assert.match(mensaje, /Ana Gómez/);
  assert.match(mensaje, /Calle 1 #2-3/);
});

test("recoger en tienda no pide direccion en el mensaje", () => {
  const pedido = crearPedido().agregar(PRODUCTO);
  const mensaje = armarMensaje(pedido, {
    nombre: "Ana",
    telefono: "3001234567",
    entrega: "Recoger en Tocancipá",
    pago: "Acordar por WhatsApp",
  });
  assert.doesNotMatch(mensaje, /Dirección:/);
  assert.match(mensaje, /Recoger en Tocancipá/);
});

test("el numero de WhatsApp queda con indicativo 57", () => {
  assert.equal(numeroWhatsApp("310 213 0278"), "573102130278");
  assert.equal(numeroWhatsApp("+57 310 213 0278"), "573102130278");
  assert.equal(numeroWhatsApp(""), "");
});

test("el enlace de WhatsApp codifica el mensaje", () => {
  const enlace = enlaceWhatsApp("573102130278", "Hola & gracias");
  assert.match(enlace, /^https:\/\/wa\.me\/573102130278\?text=/);
  assert.match(enlace, /Hola%20%26%20gracias/);
});

test("un pedido vacio no se puede enviar", () => {
  assert.throws(() => armarMensaje(crearPedido(), {}), /vacío/);
});
