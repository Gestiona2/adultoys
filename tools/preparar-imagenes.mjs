#!/usr/bin/env node
/**
 * Prepara todas las imagenes del sitio.
 *
 *   node tools/preparar-imagenes.mjs
 *   node tools/preparar-imagenes.mjs --force
 *
 * - Fotos de producto: recorta el aire de sobra y las centra en un lienzo
 *   blanco de 560x560 en WebP. Una foto pequena se agranda como maximo al doble.
 * - Fotos de seccion (hero, categorias, blog): tres anchos para que el celular
 *   baje solo la version que necesita.
 * - Logo: version transparente y version clara para fondos oscuros.
 *
 * Es idempotente: si el archivo final ya existe y es mas nuevo que el origen,
 * no lo vuelve a procesar. Con --force se rehace todo.
 */
import { existsSync } from "node:fs";
import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const RAIZ = dirname(dirname(fileURLToPath(import.meta.url)));
const PUBLIC = join(RAIZ, "public", "img");
const FUERZA = process.argv.includes("--force");
const CONCURRENCIA = 6;

const SITIO = join(PUBLIC, "sitio");
const PRODUCTOS = join(PUBLIC, "productos");
const MARCA = join(PUBLIC, "marca");
const ENTRADA = join(RAIZ, "insumos", "fotos");

const CATEGORIAS = {
  "categoria-vibradores": "sitio/categoria-juguetes.webp",
  "categoria-dildos": "sitio/banner-newsletter.webp",
  "categoria-parejas": "sitio/blog-parejas-y-placer.webp",
  "categoria-lenceria": "sitio/categoria-lenceria.webp",
  "categoria-lubricantes": "sitio/categoria-cosmeticos.webp",
  "categoria-salud": "sitio/categoria-suplementos.webp",
  "categoria-sado": "sitio/banner-sado.webp",
  "categoria-higiene": "sitio/categoria-higiene.webp",
  "categoria-weed": "producto/2608_AT_0000075-caletas-para-fumar.png",
};

const FOTOS_SITIO = [
  "banner-hero-neon.webp",
  "banner-hero-juguetes.webp",
  "banner-hero-daily-deals.webp",
  "banner-sado.webp",
  "banner-newsletter.webp",
  "blog-fondo-home.webp",
  "blog-portada.webp",
  "blog-parejas-y-placer.webp",
  "blog-primer-juguete.webp",
  "blog-sexo-y-bienestar.webp",
  "categoria-lenceria.webp",
  "categoria-cosmeticos.webp",
  "categoria-suplementos.webp",
  "categoria-higiene.webp",
  "categoria-juguetes.webp",
];

// La foto de producto no necesita mas de 560 px: en la ficha se ve a ~520 y en
// la tarjeta a ~280. Guardar 1200 solo haria la pagina mas lenta.
const LADO_PRODUCTO = 560;
const INTERIOR_PRODUCTO = 492; // 6 % de margen por lado
const CALIDAD_PRODUCTO = 72;
const ANCHOS_SITIO = [600, 900, 1200];
const CALIDAD_SITIO = 80;

async function masNuevoQue(origen, destino) {
  if (FUERZA || !existsSync(destino)) return true;
  try {
    const [a, b] = await Promise.all([stat(origen), stat(destino)]);
    return a.mtimeMs > b.mtimeMs;
  } catch {
    return true;
  }
}

async function fotoProducto(slug, origen) {
  const destino = join(PRODUCTOS, `${slug}.webp`);
  if (!(await masNuevoQue(origen, destino))) return false;
  if (!existsSync(origen)) {
    console.warn(`  falta la foto de ${slug}: ${origen}`);
    return false;
  }
  // Todas las fotos salen en el mismo lienzo cuadrado y blanco, con el producto
  // centrado y el mismo margen. Asi la grilla se ve pareja aunque los originales
  // vengan de proveedores distintos.
  const base = await sharp(origen).rotate().flatten({ background: "#ffffff" }).toBuffer();
  let recorte;
  try {
    recorte = await sharp(base).trim({ background: "#ffffff", threshold: 20 }).toBuffer({ resolveWithObject: true });
  } catch {
    recorte = await sharp(base).toBuffer({ resolveWithObject: true });
  }
  const { width: w, height: h } = recorte.info;
  // Una foto chica se agranda como maximo al doble: mas alla se ve borrosa.
  const escala = Math.min(INTERIOR_PRODUCTO / w, INTERIOR_PRODUCTO / h, 2);
  const ancho = Math.max(1, Math.round(w * escala));
  const alto = Math.max(1, Math.round(h * escala));
  let foto = sharp(recorte.data).resize(ancho, alto, { kernel: "lanczos3" });
  if (escala > 1.05) foto = foto.sharpen({ sigma: 0.8 });
  await sharp({ create: { width: LADO_PRODUCTO, height: LADO_PRODUCTO, channels: 3, background: "#ffffff" } })
    .composite([{ input: await foto.toBuffer(), gravity: "centre" }])
    .webp({ quality: CALIDAD_PRODUCTO, effort: 6, smartSubsample: true })
    .toFile(destino);
  return true;
}

async function fotoSitio(nombre) {
  const origen = join(ENTRADA, "sitio", nombre);
  if (!existsSync(origen)) return false;
  const meta = await sharp(origen).metadata();
  const ancho = meta.width || 1200;
  const anchos = ANCHOS_SITIO.filter((w) => w <= ancho);
  if (!anchos.length) anchos.push(ancho);
  for (const w of anchos) {
    const destino = join(SITIO, `${nombre.replace(/\.webp$/, "")}-${w}.webp`);
    if (!(await masNuevoQue(origen, destino))) continue;
    await sharp(origen)
      .rotate()
      .resize({ width: w, withoutEnlargement: true })
      .webp({ quality: CALIDAD_SITIO, effort: 5 })
      .toFile(destino);
  }
  return true;
}

async function fotoCategoria(nombre, origenRelativo) {
  const origen = origenRelativo.startsWith("producto/")
    ? join(ENTRADA, "catalogo", origenRelativo.replace("producto/", ""))
    : join(ENTRADA, origenRelativo);
  if (!existsSync(origen)) {
    console.warn(`  falta la foto de categoria ${nombre}: ${origen}`);
    return false;
  }
  for (const w of [600, 900]) {
    const destino = join(SITIO, `${nombre}-${w}.webp`);
    if (!(await masNuevoQue(origen, destino))) continue;
    await sharp(origen)
      .rotate()
      .resize({ width: w, height: w, fit: "cover", position: "centre" })
      .flatten({ background: "#0b0712" })
      .webp({ quality: CALIDAD_SITIO, effort: 5 })
      .toFile(destino);
  }
  return true;
}

async function logo() {
  const origen = join(RAIZ, "insumos", "marca", "logo-adultoyss.png");
  if (!existsSync(origen)) return;
  // Quitar el fondo blanco. El logo original es RGB sin alfa.
  const { data, info } = await sharp(origen).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  for (let i = 0; i < data.length; i += 4) {
    const [r, g, b] = [data[i], data[i + 1], data[i + 2]];
    if (r > 242 && g > 242 && b > 242) data[i + 3] = 0;
  }
  await sharp(data, { raw: { width: info.width, height: info.height, channels: 4 } })
    .png()
    .toFile(join(MARCA, "logo-adultoyss.png"));

  // Version clara: el gris del logo se vuelve un lila muy claro para que se
  // lea sobre el fondo oscuro. El magenta y el azul no se tocan.
  const claro = Buffer.from(data);
  for (let i = 0; i < claro.length; i += 4) {
    const [r, g, b] = [claro[i], claro[i + 1], claro[i + 2]];
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    if (max - min < 26 && max < 180 && claro[i + 3] > 0) {
      claro[i] = 233;
      claro[i + 1] = 226;
      claro[i + 2] = 244;
    }
  }
  await sharp(claro, { raw: { width: info.width, height: info.height, channels: 4 } })
    .png()
    .toFile(join(MARCA, "logo-adultoyss-claro.png"));
}

async function compartir() {
  const destino = join(PUBLIC, "compartir-adultoyss.jpg");
  if (!FUERZA && existsSync(destino)) return;
  const fondo = join(ENTRADA, "sitio", "banner-hero-neon.webp");
  const svg = `
  <svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="t" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#07040d" stop-opacity="0.1"/>
        <stop offset="0.55" stop-color="#07040d" stop-opacity="0.55"/>
        <stop offset="1" stop-color="#07040d" stop-opacity="0.96"/>
      </linearGradient>
      <linearGradient id="g" x1="0" x2="1">
        <stop offset="0" stop-color="#ff2e9a"/>
        <stop offset="0.55" stop-color="#a855f7"/>
        <stop offset="1" stop-color="#2f7bff"/>
      </linearGradient>
    </defs>
    <rect width="1200" height="630" fill="#07040d"/>
    <rect width="1200" height="630" fill="url(#t)"/>
    <text x="80" y="455" font-family="Arial, sans-serif" font-size="86" font-weight="800" fill="#ffffff">TU DESEO,</text>
    <text x="80" y="545" font-family="Arial, sans-serif" font-size="86" font-weight="800" fill="url(#g)">NUESTRA MISIÓN.</text>
    <text x="84" y="592" font-family="Arial, sans-serif" font-size="24" letter-spacing="8" fill="#d8cfe9">ADULTOYSS · TIENDA ERÓTICA</text>
  </svg>`;
  await sharp(fondo)
    .resize(1200, 630, { fit: "cover", position: "centre" })
    .composite([{ input: Buffer.from(svg) }])
    .jpeg({ quality: 88 })
    .toFile(destino);
}

async function main() {
  await Promise.all([mkdir(SITIO, { recursive: true }), mkdir(PRODUCTOS, { recursive: true }), mkdir(MARCA, { recursive: true })]);

  const productos = JSON.parse(await readFile(join(RAIZ, "src", "datos", "productos.json"), "utf8"));
  const fuentes = JSON.parse(await readFile(join(RAIZ, "src", "datos", "_fuentes.json"), "utf8"));

  console.log(`Fotos de producto: ${productos.length}`);
  let hechas = 0;
  let pendientes = [...productos];
  const trabajadoras = Array.from({ length: CONCURRENCIA }, async () => {
    while (pendientes.length) {
      const producto = pendientes.pop();
      if (!producto) break;
      const origen = join(RAIZ, fuentes[producto.slug]);
      if (await fotoProducto(producto.slug, origen)) hechas++;
    }
  });
  await Promise.all(trabajadoras);
  console.log(`  convertidas: ${hechas}`);

  console.log("Fotos de seccion");
  for (const foto of FOTOS_SITIO) await fotoSitio(foto);
  for (const [nombre, origen] of Object.entries(CATEGORIAS)) await fotoCategoria(nombre, origen);

  await logo();
  await compartir();
  console.log("Listo: public/img/productos, public/img/sitio y public/img/marca");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
