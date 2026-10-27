#!/usr/bin/env python3
"""Crea las ilustraciones de Halloween de la web en public/img/halloween/.

    python3 tools/generar_halloween_web.py

Son las mismas del catalogo en PDF (tools/catalogo_halloween.py), todas SVG:
pesan unos pocos KB y se ven nitidas en cualquier pantalla.

El tema se enciende y se apaga con "tema_estacional" en src/datos/config.json
("halloween" o vacio). Pasada la temporada se deja vacio y se pueden borrar
estas imagenes: nada mas las usa.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogo_halloween as hw  # noqa: E402

SALIDA = Path(__file__).resolve().parent.parent / "public" / "img" / "halloween"


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    piezas = {
        "telarana-tr": hw.telarana("tr"),
        "telarana-tl": hw.telarana("tl"),
        "telarana-br": hw.telarana("br"),
        "telarana-bl": hw.telarana("bl"),
        "arana": hw.arana(90),
        "arana-corta": hw.arana(46),
        "murcielago": hw.murcielago(),
        "luna": hw.luna(),
        # contorno lila y relleno morado oscuro: se ve sobre el fondo oscuro de la web
        "bruja": hw.bruja("#1c0f33", "#b48cf0"),
        "calabaza": hw.calabaza(),
        "fantasma": hw.fantasma(),
        "caldero": hw.caldero(),
    }
    for nombre, svg in piezas.items():
        (SALIDA / f"{nombre}.svg").write_text(svg, encoding="utf-8")
    peso = sum(f.stat().st_size for f in SALIDA.glob("*.svg")) / 1000
    print(f"{len(piezas)} ilustraciones en {SALIDA} ({peso:.1f} KB en total)")


if __name__ == "__main__":
    main()
