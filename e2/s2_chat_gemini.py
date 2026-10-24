"""P4: mismo asistente mediante Chat Completions, Gemini en OpenRouter."""
import json
import os
import openai
import configuracion
from herramientas import para_chat
from s2_chat_herramientas import SISTEMA
from trazas import ejecutar, nueva, guardar, lote


def preguntar_gemini(pregunta: str, max_vueltas: int = 5, ruta_traza=None) -> str:
    mensajes = [{'role': 'system', 'content': SISTEMA}, {'role': 'user', 'content': pregunta}]
    modelo = os.environ['GEMINI_MODEL']
    traza = nueva('Gemini', modelo, pregunta)
    try:
        with openai.OpenAI(base_url='https://openrouter.ai/api/v1',
                           api_key=os.environ['OPENROUTER_API_KEY'], timeout=90, max_retries=1) as cliente:
            for numero in range(1, max_vueltas + 1):
                r = cliente.chat.completions.create(model=modelo, messages=mensajes, tools=para_chat(), max_tokens=1024)
                mensaje = r.choices[0].message
                uso = r.usage.model_dump() if r.usage else {}
                print(f'  Vuelta {numero}: usage={uso}', flush=True)
                vuelta = {'numero': numero, 'usage': uso, 'llamadas': []}
                traza['vueltas'].append(vuelta)
                llamadas = mensaje.tool_calls or []
                if not llamadas:
                    if r.choices[0].finish_reason != 'stop' or not mensaje.content:
                        raise ValueError('El modelo no devolvió una respuesta final completa')
                    traza.update(respuesta=mensaje.content, completada=True)
                    return mensaje.content
                # Conservar el mensaje completo mantiene IDs y metadatos del proveedor.
                mensajes.append(mensaje.model_dump(exclude_none=True))
                for llamada in llamadas:
                    args = json.loads(llamada.function.arguments)
                    resultado = ejecutar(llamada.function.name, args)
                    vuelta['llamadas'].append(dict(nombre=llamada.function.name, argumentos=args, resultado=resultado))
                    print(f'  -> {llamada.function.name}({args}) = {resultado}', flush=True)
                    mensajes.append({'role': 'tool', 'tool_call_id': llamada.id,
                                     'content': json.dumps(resultado, ensure_ascii=False)})
        traza['respuesta'] = 'No he podido completar la consulta en el número de pasos permitido.'
        return traza['respuesta']
    except Exception as exc:
        traza['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        guardar(traza, ruta_traza)


if __name__ == '__main__':
    lote(preguntar_gemini, 'gemini')
