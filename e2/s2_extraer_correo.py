"""E2 / P1. Evaluación reproducible y validación de clientes en SQLite."""
import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import anthropic
import openai
from pydantic import BaseModel, Field
import configuracion
from herramientas import buscar_cliente


class Linea(BaseModel):
    producto: str = Field(description='Producto tal y como lo menciona el cliente')
    cantidad: int = Field(description='Unidades o kilos pedidos')


class CorreoClasificado(BaseModel):
    tipo: Literal['pedido', 'incidencia', 'consulta', 'mixto']
    cliente: str | None = Field(description='Nombre del negocio si aparece; si no, null')
    lineas: list[Linea] = Field(description='Vacía si no hay pedido')
    urgente: bool
    resumen: str = Field(description='Una sola frase en español')


SISTEMA = 'Extraes información de correos de clientes de un distribuidor de café para hostelería.'

# Se conservan los seis casos iniciales. Etiquetas fijadas antes de ejecutar.
CASOS = [
    ('Necesito 20 kg del blend de hostelería para el viernes. Bar La Esquina.', 'pedido'),
    ('El molino hace un ruido raro desde ayer, ¿podéis venir?', 'incidencia'),
    ('¿Tenéis café descafeinado de especialidad?', 'consulta'),
    ('Mandadme 5 kg de Etiopía y, de paso, la cafetera gotea. Lumbre.', 'mixto'),
    ('URGENTE: sin café para mañana, 10 kg de blend. Hotel Prado Suites', 'pedido'),
    ('Buenas, ¿la factura de septiembre ya está emitida?', 'consulta'),
    ('Qué maravilla: otra vez el molino averiado. Así da gusto abrir el bar. Necesitamos que lo reparéis. Bar La Esquina.', 'incidencia'),
    ('Soy del Bar La Esquina. Enviadnos 4 kg de descafeinado. El Restaurante Lumbre nos recomendó vuestro café, pero este pedido es solo para nosotros.', 'pedido'),
    ('Hello, please send 6 kg of your house blend to Hotel Prado Suites next Monday. Thank you.', 'pedido'),
    ('Enviadme 3 kg de café de Etiopía. Gracias, Marta.', 'pedido'),
    ('Somos el Bar Inexistente. Queremos 2 kg de descafeinado.', 'pedido'),
    ('¿Cuál es el precio por kilo del blend y cuánto cuesta el envío? Panadería Ibiza.', 'consulta'),
    ('En Cafetería Atocha 12 la cafetera pierde agua. Además, enviadnos 8 kg de blend.', 'mixto'),
    ('No enviéis café todavía. Solo quiero saber si tenéis existencias de Etiopía. Restaurante Lumbre.', 'consulta'),
    ('El último pedido llegó con las bolsas rotas. Por favor, revisad la incidencia. Hotel Prado Suites.', 'incidencia'),
    ('Para Bar La Esquina: 2 kg de Etiopía y 3 kg de descafeinado, por favor.', 'pedido'),
    ('Soy de Cafetería Luna Azul. ¿Vendéis vasos compostables?', 'consulta'),
    ('Panadería Ibiza: enviad 0 kg de blend. Es la cantidad que figura en nuestra solicitud.', 'pedido'),
]


def con_openai(correo):
    with openai.OpenAI(timeout=90, max_retries=1) as c:
        r = c.responses.parse(model=os.environ['OPENAI_MODEL'], instructions=SISTEMA,
                              input=correo, text_format=CorreoClasificado, max_output_tokens=1024)
    if r.output_parsed is None:
        raise ValueError('OpenAI no devolvió un objeto estructurado')
    return r.output_parsed


def con_claude(correo):
    with anthropic.Anthropic(timeout=90, max_retries=1) as c:
        r = c.messages.parse(model=os.environ['ANTHROPIC_MODEL'], max_tokens=1024,
            system=SISTEMA, messages=[{'role': 'user', 'content': correo}],
            output_format=CorreoClasificado)
    if r.parsed_output is None:
        raise ValueError('Claude no devolvió un objeto estructurado')
    return r.parsed_output


def con_gemini(correo):
    with openai.OpenAI(base_url='https://openrouter.ai/api/v1',
                       api_key=os.environ['OPENROUTER_API_KEY'], timeout=90, max_retries=1) as c:
        r = c.chat.completions.parse(model=os.environ['GEMINI_MODEL'],
            messages=[{'role': 'system', 'content': SISTEMA}, {'role': 'user', 'content': correo}],
            response_format=CorreoClasificado, max_tokens=1024)
    if r.choices[0].message.parsed is None:
        raise ValueError('Gemini no devolvió un objeto estructurado')
    return r.choices[0].message.parsed


def validar_negocio(resultado):
    avisos = []
    clientes = buscar_cliente(resultado.cliente) if resultado.cliente else []
    if resultado.cliente and not clientes:
        avisos.append(f'Cliente no encontrado: {resultado.cliente}')
    elif len(clientes) > 1:
        avisos.append(f'Cliente ambiguo: {resultado.cliente}')
    if any(linea.cantidad <= 0 for linea in resultado.lineas):
        avisos.append('Cantidad no válida: debe ser mayor que cero')
    return {'clientes_en_bd': clientes, 'avisos': avisos}


PROVEEDORES = {'OpenAI': (con_openai, 'OPENAI_MODEL'),
               'Claude': (con_claude, 'ANTHROPIC_MODEL'),
               'Gemini': (con_gemini, 'GEMINI_MODEL')}


def evaluar(destino, proveedores=None):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for nombre in proveedores or PROVEEDORES:
        extraer, variable = PROVEEDORES[nombre]
        registros = []
        for numero, (correo, esperado) in enumerate(CASOS, 1):
            fila = dict(caso=numero, proveedor=nombre, modelo=os.environ[variable], correo=correo,
                        esperado=esperado, fecha_utc=datetime.now(timezone.utc).isoformat())
            try:
                resultado = extraer(correo)
                fila.update(resultado=resultado.model_dump(), acierto=resultado.tipo == esperado,
                            error=None, **validar_negocio(resultado))
                print(f'{nombre} {numero:02}: {resultado.tipo}; esperado={esperado}; {fila["avisos"]}', flush=True)
            except Exception as exc:
                # No se confunde un fallo técnico con una respuesta del modelo.
                fila.update(resultado=None, acierto=False, error=f'{type(exc).__name__}: {exc}',
                            clientes_en_bd=[], avisos=[])
                print(f'{nombre} {numero:02}: ERROR {type(exc).__name__}', flush=True)
            registros.append(fila)
            (destino / f'clasificacion_{nombre.lower()}.json').write_text(
                json.dumps(registros, ensure_ascii=False, indent=2), encoding='utf-8')
        with (destino / f'clasificacion_{nombre.lower()}.csv').open('w', encoding='utf-8-sig', newline='') as f:
            escritor = csv.DictWriter(f, fieldnames=['caso','proveedor','modelo','esperado','obtenido','acierto','error','avisos'])
            escritor.writeheader()
            for fila in registros:
                escritor.writerow({k: fila[k] for k in ['caso','proveedor','modelo','esperado','acierto','error']} |
                    {'obtenido': (fila['resultado'] or {}).get('tipo'), 'avisos': '; '.join(fila['avisos'])})
        print(f'{nombre}: {sum(f["acierto"] for f in registros)}/{len(CASOS)} tipos correctos', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--proveedor', choices=list(PROVEEDORES))
    p.add_argument('--salida', default=str(Path(__file__).with_name('resultados')))
    args = p.parse_args()
    evaluar(args.salida, [args.proveedor] if args.proveedor else None)
