import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

// El sitio puede publicarse en la raiz del dominio o como demo en un
// subdirectorio. Las dos cosas se controlan con variables de entorno; ninguna
// ruta del codigo lleva el nombre del proyecto escrito a mano.
export default defineConfig({
  site: process.env.PUBLIC_SITE || "https://adultoyss.com",
  base: process.env.PUBLIC_BASE || "/",
  vite: {
    plugins: [tailwindcss()],
  },
});
