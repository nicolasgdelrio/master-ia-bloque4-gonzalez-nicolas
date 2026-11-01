"""Herramientas locales de consulta y registro de incidencias de Tostadero Retiro."""
import sqlite3
from datetime import date
from pathlib import Path
BD = Path(__file__).with_name('tostadero.db')

def consulta(sql, params=()):
    with sqlite3.connect(BD) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(x) for x in conn.execute(sql, params)]

def buscar_cliente(texto: str):
    return consulta('SELECT id,nombre,tipo,distrito FROM clientes WHERE nombre LIKE ?', (f'%{texto}%',))

def consultar_pedidos(cliente_id: int):
    return consulta('SELECT id,fecha,estado,total FROM pedidos WHERE cliente_id=?', (cliente_id,))

def stock_producto(texto: str):
    return consulta('SELECT sku,nombre,stock,precio FROM productos WHERE nombre LIKE ? OR sku LIKE ?', (f'%{texto}%',f'%{texto}%'))

def crear_incidencia(cliente_id: int, maquina: str, descripcion: str, prioridad: str):
    if prioridad not in ('baja','media','alta'):
        return {'error':'Prioridad no válida'}
    if not consulta('SELECT id FROM clientes WHERE id=?',(cliente_id,)):
        return {'error':'Cliente inexistente; utiliza buscar_cliente'}
    with sqlite3.connect(BD) as conn:
        cur=conn.execute('INSERT INTO incidencias(cliente_id,maquina,descripcion,prioridad,fecha) VALUES (?,?,?,?,?)',(cliente_id,maquina,descripcion,prioridad,date.today().isoformat()))
    return {'id':cur.lastrowid,'estado':'abierta'}

FUNCIONES={n:globals()[n] for n in ('buscar_cliente','consultar_pedidos','stock_producto','crear_incidencia')}
def schema(p): return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
DEFINICIONES=[
 {'name':'buscar_cliente','description':'Identifica al cliente antes de consultar o crear incidencias.','parameters':schema({'texto':{'type':'string'}})},
 {'name':'consultar_pedidos','description':'Consulta pedidos reales de un cliente identificado.','parameters':schema({'cliente_id':{'type':'integer'}})},
 {'name':'stock_producto','description':'Consulta stock y precio de productos.','parameters':schema({'texto':{'type':'string'}})},
 {'name':'crear_incidencia','description':'Registra avería concreta. No usar sin avería explícita ni aprobación humana.','parameters':schema({'cliente_id':{'type':'integer'},'maquina':{'type':'string'},'descripcion':{'type':'string'},'prioridad':{'type':'string','enum':['baja','media','alta']}})}]
