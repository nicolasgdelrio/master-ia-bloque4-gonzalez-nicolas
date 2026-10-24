"""P3: Responses API del kit con registro completo de herramientas y tokens."""
import json
import os
import openai
import configuracion
from herramientas import para_openai
from trazas import ejecutar, nueva, guardar, lote

SISTEMA = ('Eres el asistente interno de Tostadero Retiro. Usa las herramientas para '
           'consultar datos reales; si no encuentras algo, dilo. No inventes cifras.')


def preguntar(pregunta: str, max_vueltas: int = 5, ruta_traza=None) -> str:
    entrada = [{'role': 'user', 'content': pregunta}]
    modelo = os.environ['OPENAI_MODEL']
    traza = nueva('OpenAI', modelo, pregunta)
    try:
        with openai.OpenAI(timeout=90, max_retries=1) as cliente:
            for numero in range(1, max_vueltas + 1):
                r = cliente.responses.create(model=modelo, instructions=SISTEMA,
                                              tools=para_openai(), input=entrada, max_output_tokens=1024)
                entrada += r.output
                uso = r.usage.model_dump() if r.usage else {}
                print(f'  Vuelta {numero}: usage={uso}', flush=True)
                vuelta = {'numero': numero, 'usage': uso, 'llamadas': []}
                traza['vueltas'].append(vuelta)
                llamadas = [item for item in r.output if item.type == 'function_call']
                if not llamadas:
                    traza.update(respuesta=r.output_text, completada=True)
                    return r.output_text
                for llamada in llamadas:
                    args = json.loads(llamada.arguments)
                    resultado = ejecutar(llamada.name, args)
                    vuelta['llamadas'].append(dict(nombre=llamada.name, argumentos=args, resultado=resultado))
                    print(f'  -> {llamada.name}({args}) = {resultado}', flush=True)
                    entrada.append({'type': 'function_call_output', 'call_id': llamada.call_id,
                                    'output': json.dumps(resultado, ensure_ascii=False)})
        traza['respuesta'] = 'No he podido completar la consulta en el número de pasos permitido.'
        return traza['respuesta']
    except Exception as exc:
        traza['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        guardar(traza, ruta_traza)


if __name__ == '__main__':
    lote(preguntar, 'openai')
