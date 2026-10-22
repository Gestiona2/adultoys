"""Pruebas del validador del catalogo.

   python3 -m unittest discover -s tools -p "test_*.py" -v
"""
import json
import tempfile
import unittest
from pathlib import Path

from validar import validar, leer_catalogo

BUENO = {
    "slug": "bala-afrodita",
    "titulo": "Bala Afrodita",
    "precio": 65000,
    "precio_antes": None,
    "descuento": None,
    "categoria": "vibradores",
    "subcategoria": "BALAS",
    "imagenes": ["productos/bala-afrodita.webp"],
    "descripcion": "x",
    "stock": True,
    "recomendado": False,
    "promo_flash": False,
    "oculto": False,
}
CATEGORIAS = {"vibradores", "lenceria"}
SUBCATEGORIAS = {"BALAS", "balas"}


class ValidarTest(unittest.TestCase):
    def test_producto_correcto_no_da_errores(self):
        self.assertEqual(validar([BUENO], None, CATEGORIAS, SUBCATEGORIAS), [])

    def test_precio_cero_oculto_es_valido(self):
        p = {**BUENO, "precio": 0, "oculto": True}
        self.assertEqual(validar([p]), [])

    def test_precio_cero_visible_es_error(self):
        p = {**BUENO, "precio": 0, "oculto": False}
        errores = validar([p])
        self.assertEqual(len(errores), 1)
        self.assertIn("precio es 0", errores[0])

    def test_descuento_que_no_cuadra_es_error(self):
        p = {**BUENO, "precio": 80000, "precio_antes": 100000, "descuento": 30}
        errores = validar([p])
        self.assertEqual(len(errores), 1)
        self.assertIn("el descuento debe ser 20", errores[0])

    def test_descuento_correcto_pasa(self):
        p = {**BUENO, "precio": 80000, "precio_antes": 100000, "descuento": 20}
        self.assertEqual(validar([p]), [])

    def test_categoria_inexistente_es_error(self):
        p = {**BUENO, "categoria": "vibrador"}
        errores = validar([p], None, CATEGORIAS)
        self.assertEqual(len(errores), 1)
        self.assertIn("no existe", errores[0])

    def test_subcategoria_inexistente_en_producto_visible_es_error(self):
        p = {**BUENO, "subcategoria": "OTRA"}
        errores = validar([p], None, CATEGORIAS, SUBCATEGORIAS)
        self.assertEqual(len(errores), 1)
        self.assertIn("subcategoria", errores[0])

    def test_subcategoria_inexistente_en_producto_oculto_se_ignora(self):
        p = {**BUENO, "subcategoria": "OTRA", "precio": 0, "oculto": True}
        self.assertEqual(validar([p], None, CATEGORIAS, SUBCATEGORIAS), [])

    def test_promo_flash_en_agotado_es_error(self):
        p = {**BUENO, "promo_flash": True, "stock": False}
        errores = validar([p])
        self.assertEqual(len(errores), 1)
        self.assertIn("agotado", errores[0])

    def test_vigencia_bien_escrita_pasa(self):
        p = {**BUENO, "promo_flash": True, "promo_flash_vence": "2026-10-05T20:00:00-05:00"}
        self.assertEqual(validar([p]), [])

    def test_vigencia_mal_escrita_es_error(self):
        p = {**BUENO, "promo_flash": True, "promo_flash_vence": "05/10/2026 8pm"}
        errores = validar([p])
        self.assertEqual(len(errores), 1)
        self.assertIn("promo_flash_vence", errores[0])

    def test_booleano_entre_comillas_es_error(self):
        p = {**BUENO, "stock": "true"}
        errores = validar([p])
        self.assertTrue(any("stock" in e and "true o false" in e for e in errores))

    def test_imagen_inexistente_es_error(self):
        with tempfile.TemporaryDirectory() as carpeta:
            errores = validar([BUENO], carpeta)
        self.assertTrue(any("no existe" in e for e in errores))

    def test_catalogo_roto_explica_la_linea(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "productos.json"
            ruta.write_text('[{"slug": "a",}]', encoding="utf-8")
            datos, error = leer_catalogo(ruta)
        self.assertIsNone(datos)
        self.assertIn("linea 1", error)

    def test_catalogo_valido_se_lee(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "productos.json"
            ruta.write_text(json.dumps([BUENO], ensure_ascii=False), encoding="utf-8")
            datos, error = leer_catalogo(ruta)
        self.assertIsNone(error)
        self.assertEqual(len(datos), 1)


if __name__ == "__main__":
    unittest.main()
