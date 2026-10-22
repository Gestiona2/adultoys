/**
 * Carrusel de la portada.
 *
 * Se detiene al pasar el raton o al enfocar con el teclado, y no se mueve si
 * la persona pidio menos movimiento en su sistema.
 */
const SEGUNDOS = 6000;

export function montarCarrusel() {
  const carrusel = document.getElementById("carrusel");
  if (!carrusel) return;

  const piezas = [...carrusel.querySelectorAll(".carrusel-pieza")];
  const puntos = [...carrusel.querySelectorAll(".carrusel-punto")];
  if (piezas.length < 2) return;

  const quietoPorPreferencia = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let actual = 0;
  let temporizador = null;

  const mostrar = (indice) => {
    actual = (indice + piezas.length) % piezas.length;
    piezas.forEach((pieza, i) => {
      const activa = i === actual;
      pieza.classList.toggle("activa", activa);
      pieza.setAttribute("aria-hidden", String(!activa));
    });
    puntos.forEach((punto, i) => {
      punto.classList.toggle("activo", i === actual);
      punto.setAttribute("aria-selected", String(i === actual));
    });
  };

  const arrancar = () => {
    if (quietoPorPreferencia) return;
    detener();
    temporizador = setInterval(() => mostrar(actual + 1), SEGUNDOS);
  };
  const detener = () => {
    if (temporizador) clearInterval(temporizador);
    temporizador = null;
  };

  puntos.forEach((punto) =>
    punto.addEventListener("click", () => {
      mostrar(Number(punto.dataset.ir));
      arrancar();
    })
  );

  carrusel.addEventListener("mouseenter", detener);
  carrusel.addEventListener("mouseleave", arrancar);
  carrusel.addEventListener("focusin", detener);
  carrusel.addEventListener("focusout", arrancar);
  // No gastar bateria animando una pestana que nadie esta viendo.
  document.addEventListener("visibilitychange", () =>
    document.hidden ? detener() : arrancar()
  );

  arrancar();
}
