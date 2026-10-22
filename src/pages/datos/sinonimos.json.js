/**
 * Sinónimos del buscador, tal como los usa el navegador.
 */
import sinonimos from "../../datos/sinonimos.json";

export function GET() {
  return new Response(JSON.stringify(sinonimos), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}
