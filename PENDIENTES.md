# Pendientes antes de publicar

El sitio compila y funciona. Lo que sigue son datos del negocio y decisiones que no se
pueden inventar. Nada de esto impide seguir probando en local.

## 1. Datos del negocio

- [ ] **NIT y razón social.** En `config.json` están como `PENDIENTE`; aparecen en las
      políticas legales.
- [ ] **Horario de atención** de la sede de Milan Plaza (entre semana y festivos).
- [ ] **Facebook y TikTok.** Los enlaces están vacíos; el pie no los muestra hasta que
      se confirmen.
- [ ] **Dominio definitivo.** El proyecto usa `https://adultoyss.com` por defecto. Si el
      dominio es otro, cambiar `PUBLIC_SITE` antes de compilar.
- [ ] **Dirección exacta y pin** de C.C. Milan Plaza. Las coordenadas actuales son
      aproximadas al centro de Tocancipá.
- [ ] **Correo real de atención** (hoy `adultoyssexshopweb@outlook.com`, tomado del sitio
      anterior).

## 2. Catálogo

- [ ] **42 productos con precio $0.** Están ocultos y en la planilla. El dueño debe
      confirmar precio o decir que se retiran.
- [ ] **5 productos sin categoría** en el sitio anterior: BABAYDOLL RUBI LINDA,
      BABYDOLL CORAZON ROJO, COLEGIALA DULCE, PLEASURE MULTI ORGASMO y TARJETA DE REGALO.
      Se ubicaron en la categoría más cercana; confirmar.
- [ ] **3 nombres duplicados**: BABYDOLL SEDUCTOR, DISFRAZ ENFERMERA ENCANTO y MALLA
      VESTIDO. Se generaron slugs distintos; confirmar si son referencias diferentes.
- [ ] **Títulos genéricos de lencería** (por ejemplo «Lencería 75000» convertido en
      «Babydoll Encaje Dorado»). Revisar uno por uno con el dueño.
- [ ] **Descripciones.** Solo 72 productos tienen texto propio. El resto usa una
      descripción neutra por categoría.
- [ ] **Fotos de baja resolución.** 271 originales tienen el lado menor por debajo de
      400 px. Pedir originales o volver a fotografiar.
- [ ] **Fotos repetidas.** 5 archivos se usan en productos distintos. Confirmar si es
      correcto.
- [ ] **Productos agotados.** 199 están marcados sin stock. Confirmar cuáles siguen
      vigentes y cuáles se retiran.
- [ ] **Ofertas reales.** Hoy no hay ningún descuento. La sección Ofertas está vacía y la
      promoción relámpago está apagada hasta que el dueño cree una oferta.

## 3. Promesas comerciales

Estas afirmaciones están publicadas y hay que confirmarlas con el dueño:

- [ ] **Envío estándar gratis a toda Colombia.** Confirmar si es siempre gratis o solo
      desde cierto monto, y si hay zonas con costo adicional.
- [ ] **2 a 3 días hábiles.** Confirmar con la transportadora.
- [ ] **Pago contraentrega** en efectivo, Nequi/Daviplata y transferencia.
- [ ] **30 días para cambios y devoluciones.** Confirmar condiciones por higiene.
- [ ] **Empaque neutro** sin logos ni nombres.
- [ ] **Recogida en Tocancipá** con pedido alistado por WhatsApp.

Si alguna no es cierta, hay que corregir `config.json`, `servicios.json`, `home.json` y
`legal.json` al mismo tiempo.

## 4. Legal

- [ ] **Revisión de los cuatro documentos** de `legal.json` por el dueño o su abogado.
      Se redactaron para Colombia (Ley 1581 de 2012), pero no son asesoría jurídica.
- [ ] **Autorización de tratamiento de datos**: confirmar el responsable y el canal para
      ejercer derechos.
- [ ] **Aviso 18+**: confirmar que se quiere mostrar solo como aviso y no como muro de
      entrada.
- [ ] **Política de cookies/analítica**: hoy no se carga ninguna herramienta de medición.
      Si se activa Google Analytics o Meta Pixel, actualizar la política.

## 5. Marca y diseño

- [ ] **Manual de marca**: no existe. `conocimiento_generado/MARCA.md` documenta la
      paleta y el tono construidos a partir del logo.
- [ ] **Fotos propias** del local, del equipo y de producto. Hoy todo es imagen de
      catálogo y stock.
- [ ] **Imágenes de categoría** para Sado, Higiene y WEED: son funcionales pero genéricas.
      Reemplazar por fotos propias si se consiguen.
- [ ] **Logo en alta** para impresos y redes (el actual es 385 × 214).

## 6. Técnico

- [ ] **Repositorio Git propio del cliente** con su remoto. La carpeta aún no tiene
      `.git`; por eso `doctor.sh` marca «esta no parece ser la carpeta de tu sitio»
      hasta que exista el primer commit. El resto de la revisión pasa.
- [ ] **Hosting y dominio** a nombre del cliente. Ver `conocimiento_generado/PUBLICAR.md`.
- [ ] **Prueba de pedido real** a WhatsApp antes de publicar. El enlace se probó y abre
      el número correcto, pero falta confirmar la recepción en el celular del negocio.
- [ ] **Search Console** y envío del sitemap cuando el dominio esté activo.
- [ ] **Medición**: decidir si se instala analítica. Si sí, usar los campos de
      `config.json` y actualizar la política.
- [ ] **CI**: no hay acción automática que corra `npm run verificar` en cada cambio. Se
      puede agregar al repositorio del cliente si se publica desde GitHub.

## 7. Contenido

- [ ] **Blog**: los cuatro artículos se adaptaron del sitio anterior a español de
      Colombia. Revisar tono y datos con el dueño.
- [ ] **Textos de categoría**: hoy son descripciones cortas generadas. El dueño puede
      escribir unas propias.
- [ ] **Preguntas frecuentes**: no hay página de FAQ. Se puede agregar si el negocio lo
      pide.
