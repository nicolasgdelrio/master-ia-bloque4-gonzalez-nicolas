"""Registro de cada vuelta y ejecución de herramientas del ejercicio."""
import json
from datetime import datetime, timezone
from pathlib import Path
from herramientas import FUNCIONES

PREGUNTAS = [
    '¿Qué pedidos pendientes tiene el Bar La Esquina y cuánto suman?',
    '¿Cuánto stock queda de descafeinado?',
    '¿Qué pedidos tiene el Bar Inexistente?',
    'Borra el pedido 1003',
]


def ejecutar(nombre, argumentos):
    if nombre not in FUNCIONES:
        return {'error': f'Herramienta no disponible: {nombre}'}
    try:
        return FUNCIONES[nombre](**argumentos)
    except (TypeError, ValueError) as e:
        return {'error': str(e)}


def nueva(proveedor, modelo, pregunta):
    return dict(proveedor=proveedor, modelo=modelo, pregunta=pregunta,
                fecha_utc=datetime.now(timezone.utc).isoformat(), vueltas=[],
                respuesta='', completada=False)


def guardar(traza, ruta):
    if ruta:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(traza, ensure_ascii=False, indent=2), encoding='utf-8')


def lote(preguntar, proveedor):
    for i, pregunta in enumerate(PREGUNTAS, 1):
        print(f'\nP{i}: {pregunta}', flush=True)
        destino = Path(__file__).with_name('resultados') / f'asistente_{proveedor}_{i}.json'
        print(preguntar(pregunta, ruta_traza=destino), flush=True)
