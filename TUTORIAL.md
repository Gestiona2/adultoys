# Tu sitio web — cómo hacerle cambios

Tu sitio: **https://adultoyss.com**

Tienes un asistente que hace los cambios por ti. **Le hablas en español normal**, como le
pedirías algo a una persona. No hay que aprender nada técnico.

---

## Lo primero que debes saber

> **No le puedes hacer daño. Todo se puede devolver.**

Cada cambio queda guardado. Si algo no te gusta —hoy, mañana o el mes que viene— le dices
que lo devuelva y vuelve como estaba. Por eso puedes probar con confianza.

---

## Cómo abrirlo

1. Abre la **terminal** (el programa negro donde se escriben comandos)
2. Escribe esto y pulsa Enter:

```
cd web-adultoys
opencode
```

Ya está. Ahora escríbele lo que quieras.

---

## Cómo se le pide algo

Dile **qué quieres**, no cómo hacerlo. Ejemplos reales de tu sitio:

> *Cambia el precio de la Satisfyer Pro 2 a $320.000*

> *La Bala Afrodita está agotada, márcala sin existencias*

> *Agrega un artículo al blog sobre cómo limpiar un juguete*

> *En la página de contacto, corrige el horario de la sede de Milan Plaza*

> *Cambia la foto principal de la Lencería Encaje Dorado por la que dejé en el escritorio*

Si no entiende algo, te pregunta. Si le falta un dato, te lo pide. **Nunca inventa un
precio ni una existencia.**

---

## Cómo funciona cada cambio

**1. Se lo pides.** En español normal.

**2. Te lo muestra.** Antes de publicar nada, te enseña cómo quedó para que lo revises. Te
va a decir en qué dirección mirarlo.

**3. Tú apruebas.** Si te gusta, le dices que lo publique. Si no, le dices qué cambiar y lo
ajusta.

**4. Lo publica.** Tarda **de 2 a 4 minutos** en verse en internet. Si no lo ves de
inmediato, es normal: espera un momento y recarga con **Ctrl+F5**.

> **Nunca publica sin preguntarte.** Si no le dijiste que sí, tu sitio no cambió.

---

## Cómo deshacer

Solo díselo con tus palabras:

> *No me gustó, déjalo como estaba*

> *Vuelve a como estaba ayer*

> *Borré algo sin querer, ¿lo puedes recuperar?*

Nada se pierde de verdad. Todo queda guardado.

---

## El catálogo

Los productos, precios, existencias, recomendados y ofertas se editan en
**`Catalogo-Adultoyss.xlsx`**. Es la planilla del catálogo.

Puedes pedirle al asistente que abra la planilla y te explique una columna, o que aplique
un cambio que ya hiciste. Después de cualquier cambio revisa que el producto siga
apareciendo con el precio y la existencia correctos.

> **Un producto con precio $0 no se muestra en el sitio.** Si quieres retirar algo, se
> deja en $0; no se borra la fila.

---

## Lo que sí puede hacer

- Cambiar precios, existencias, recomendados y ofertas
- Cambiar cualquier texto de la portada, categorías, nosotros o servicios
- Cambiar o agregar fotos de producto
- Agregar artículos al blog
- Cambiar teléfonos, correos, horarios y dirección
- Corregir los textos de envío, cambios y devoluciones
- Publicar los cambios y volver atrás si algo no gustó

## Lo que no

- Rediseñar el sitio o cambiar los colores de la marca
- Agregar pasarela de pagos o cobrar con tarjeta dentro del sitio
- Conectar el inventario con otro sistema
- Cambiar el dominio o el correo
- Publicar contenido explícito o afirmaciones médicas

Para eso está **Emp2Web**: +57 302 552 6058 · ayuda@emp2web.com

---

## Si algo se ve raro

Ejecuta esto en la terminal, dentro de la carpeta del sitio:

```
bash doctor.sh
```

*(En Windows: `.\doctor.ps1`)*

> **Si Windows dice que "la ejecución de scripts está deshabilitada"**, escribe esto una
> sola vez y no vuelve a pasar:
>
> ```
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

Te dice si todo está bien y qué falta si algo falla. **Si sale algo en rojo, mándale esa
pantalla completa a tu proveedor.**

---

## Consejos

- **Un cambio a la vez.** Es más fácil de revisar, y de deshacer si no gusta.
- **Revísalo en el celular** antes de aprobar. Es donde entra la mayoría de la gente.
- **Si dudas, pregúntale.** *"¿Esto se puede?"* es una pregunta válida.
- **No tengas miedo de probar.** Todo se devuelve.

---

**Tienes 30 días de acompañamiento** desde la entrega. Cualquier duda, escribe a
Emp2Web: +57 302 552 6058 · ayuda@emp2web.com
