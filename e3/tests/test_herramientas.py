"""Pruebas de las herramientas y del esquema SQLite con una BD temporal."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import herramientas


class HerramientasTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / 'test.db'
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE clientes(id INTEGER PRIMARY KEY,nombre TEXT,tipo TEXT,distrito TEXT);
                CREATE TABLE pedidos(id INTEGER PRIMARY KEY,cliente_id INTEGER,fecha TEXT,estado TEXT,total REAL);
                CREATE TABLE productos(sku TEXT PRIMARY KEY,nombre TEXT,stock INTEGER,precio REAL);
                CREATE TABLE incidencias(id INTEGER PRIMARY KEY AUTOINCREMENT,cliente_id INTEGER,maquina TEXT,descripcion TEXT,prioridad TEXT,fecha TEXT);
                INSERT INTO clientes VALUES(1,'Restaurante Lumbre','restaurante','Retiro');
                INSERT INTO pedidos VALUES(101,1,'2026-10-28','pendiente',238.5);
                INSERT INTO productos VALUES('MAQ-010','Cafetera dos grupos',3,2400);
            ''')
        self.patch = patch.object(herramientas, 'BD', self.db_path)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def test_busqueda_cliente(self):
        self.assertEqual(herramientas.buscar_cliente('Lumbre')[0]['id'], 1)

    def test_pedido_pendiente(self):
        self.assertEqual(herramientas.consultar_pedidos(1)[0]['estado'], 'pendiente')

    def test_stock(self):
        self.assertEqual(herramientas.stock_producto('Cafetera')[0]['stock'], 3)

    def test_incidencia_valida(self):
        resultado = herramientas.crear_incidencia(1, 'Cafetera dos grupos', 'No calienta', 'alta')
        self.assertEqual(resultado['estado'], 'abierta')
        self.assertEqual(herramientas.consulta('SELECT COUNT(*) AS n FROM incidencias')[0]['n'], 1)

    def test_incidencia_prioridad_invalida(self):
        self.assertIn('error', herramientas.crear_incidencia(1, 'Cafetera', 'Fallo', 'urgente'))
        self.assertEqual(herramientas.consulta('SELECT COUNT(*) AS n FROM incidencias')[0]['n'], 0)

    def test_incidencia_cliente_inexistente(self):
        self.assertIn('error', herramientas.crear_incidencia(999, 'Cafetera', 'Fallo', 'alta'))
        self.assertEqual(herramientas.consulta('SELECT COUNT(*) AS n FROM incidencias')[0]['n'], 0)


if __name__ == '__main__':
    unittest.main()
