/**
 * Carrusel de la portada.
 *
 * El tiempo lo marca la barra de progreso del punto activo (una animacion de
 * CSS): cuando termina, pasa a la siguiente pieza. Asi la barra y el cambio
 * nunca se desfasan, y pausar es solo congelar la animacion.
 *
 * Se detiene con el boton de pausa o al enfocar con el teclado. No se mueve
 * si la persona pidio menos movimiento en su sistema (el CSS quita la
 * animacion y por eso nunca llega el aviso de fin).
 */
export function montarCarrusel() {
  const carrusel = document.getElementById("carrusel");
  if (!carrusel) return;

  const piezas = [...carrusel.querySelectorAll(".carrusel-pieza")];
  if (piezas.length < 2) return;

  let actual = 0;
  let pausadoAMano = false;

  const mostrar = (indice) => {
    actual = (indice + piezas.length) % piezas.length;
    piezas.forEach((pieza, i) => {
      const activa = i === actual;
      pieza.classList.toggle("activa", activa);
      pieza.setAttribute("aria-hidden", String(!activa));
      // Lo que esta oculto no debe recibir el foco del teclado.
      pieza.inert = !activa;
    });
  };

  const pausar = (si) => carrusel.classList.toggle("pausado", si);

  carrusel.addEventListener("animationend", (evento) => {
    if (evento.animationName !== "carrusel-progreso") return;
    mostrar(actual + 1);
  });

  carrusel.addEventListener("click", (evento) => {
    const boton = evento.target.closest("button");
    if (!boton || !carrusel.contains(boton)) return;
    if (boton.dataset.ir !== undefined) mostrar(Number(boton.dataset.ir));
    if (boton.dataset.mover !== undefined) mostrar(actual + Number(boton.dataset.mover));
    if (boton.classList.contains("carrusel-pausa")) {
      pausadoAMano = !pausadoAMano;
      pausar(pausadoAMano);
      carrusel.querySelectorAll(".carrusel-pausa").forEach((b) => {
        b.setAttribute("aria-pressed", String(pausadoAMano));
        b.setAttribute("aria-label", pausadoAMano ? b.dataset.reanudar : b.dataset.pausar);
      });
    }
    // Despues de usar una flecha o un punto, el foco sigue en la pieza nueva.
    if (boton.dataset.ir !== undefined || boton.dataset.mover !== undefined) {
      const igual = piezas[actual].querySelector(
        boton.dataset.ir !== undefined ? `[data-ir="${boton.dataset.ir}"]` : `[data-mover="${boton.dataset.mover}"]`
      );
      igual?.focus({ preventScroll: true });
    }
  });

  // Con el teclado dentro, quieto: nadie quiere que el boton se le mueva.
  carrusel.addEventListener("focusin", (evento) => {
    if (evento.target.matches(":focus-visible")) pausar(true);
  });
  carrusel.addEventListener("focusout", () => {
    if (!pausadoAMano) pausar(false);
  });

  // Deslizar con el dedo en celular.
  let inicioX = null;
  let inicioY = null;
  carrusel.addEventListener("touchstart", (e) => {
    inicioX = e.touches[0].clientX;
    inicioY = e.touches[0].clientY;
  }, { passive: true });
  carrusel.addEventListener("touchend", (e) => {
    if (inicioX === null) return;
    const dx = e.changedTouches[0].clientX - inicioX;
    const dy = e.changedTouches[0].clientY - inicioY;
    inicioX = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) mostrar(actual + (dx < 0 ? 1 : -1));
  }, { passive: true });

  mostrar(0);
}
