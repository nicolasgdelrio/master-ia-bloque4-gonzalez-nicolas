"""Crea datos de demostración; nunca usar para información real de clientes."""
import sqlite3
from pathlib import Path
p=Path(__file__).with_name('tostadero.db')
with sqlite3.connect(p) as db:
    db.executescript('''
    CREATE TABLE IF NOT EXISTS clientes(id INTEGER PRIMARY KEY,nombre TEXT,tipo TEXT,distrito TEXT);
    CREATE TABLE IF NOT EXISTS pedidos(id INTEGER PRIMARY KEY,cliente_id INTEGER,fecha TEXT,estado TEXT,total REAL);
    CREATE TABLE IF NOT EXISTS productos(sku TEXT PRIMARY KEY,nombre TEXT,stock INTEGER,precio REAL);
    CREATE TABLE IF NOT EXISTS incidencias(id INTEGER PRIMARY KEY AUTOINCREMENT,cliente_id INTEGER,maquina TEXT,descripcion TEXT,prioridad TEXT,fecha TEXT);
    ''')
    db.execute('INSERT OR IGNORE INTO clientes VALUES (1,?,?,?)',('Restaurante Lumbre','restaurante','Retiro'))
    db.execute('INSERT OR IGNORE INTO pedidos VALUES (101,1,?,?,?)',('2026-10-28','pendiente',238.50))
    db.execute('INSERT OR IGNORE INTO productos VALUES (?,?,?,?)',('MAQ-010','Cafetera dos grupos',3,2400))
print('Base de datos de demostración creada:',p)
