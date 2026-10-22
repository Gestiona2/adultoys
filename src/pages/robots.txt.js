export function GET({ site }) {
  const raiz = (site?.href || "https://adultoyss.com/").replace(/\/$/, "");
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return new Response(
    `User-agent: *\nAllow: /\n\nSitemap: ${raiz}${base}/sitemap.xml\n`,
    { headers: { "Content-Type": "text/plain; charset=utf-8" } }
  );
}
