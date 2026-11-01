"""Agente desde cero: Claude Messages API, trazas, límite de pasos, aprobación."""
import json
import os
import anthropic
from dotenv import load_dotenv
from herramientas import DEFINICIONES, FUNCIONES
load_dotenv()
SISTEMA=('Eres agente de soporte técnico de Tostadero Retiro. Identifica siempre al cliente '
         'mediante buscar_cliente antes de utilizar cliente_id. Si hay avería, registra '
         'una incidencia (alta si no pueden servir cafés). Consulta pedidos reales; '
         'nunca inventes resultados. Responde brevemente y en español. Si se rechaza '
         'una acción, no la repitas.')
class Agente:
    def __init__(self,max_pasos=8):
        self.max_pasos=max_pasos
        self.cliente=anthropic.Anthropic()
        self.modelo=os.environ['ANTHROPIC_MODEL']
    def ejecutar(self,correo):
        mensajes=[{'role':'user','content':correo}]
        herramientas=[{'name':d['name'],'description':d['description'],'input_schema':d['parameters']} for d in DEFINICIONES]
        for n in range(1,self.max_pasos+1):
            respuesta=self.cliente.messages.create(model=self.modelo,max_tokens=1400,system=SISTEMA,messages=mensajes,tools=herramientas)
            mensajes.append({'role':'assistant','content':respuesta.content})
            print(f'[PASO {n}] parada={respuesta.stop_reason}')
            if respuesta.stop_reason!='tool_use':
                return '\n'.join(b.text for b in respuesta.content if b.type=='text')
            salidas=[]
            for b in respuesta.content:
                if b.type!='tool_use': continue
                print(f'[HERRAMIENTA] {b.name}: {b.input}')
                error=False
                if b.name=='crear_incidencia' and input('¿Aprobar registro de incidencia? [s/N] ').strip().lower()!='s':
                    resultado={'error':'Acción rechazada por una persona; no reintentar.'};error=True
                else:
                    try: resultado=FUNCIONES[b.name](**b.input)
                    except Exception as ex: resultado={'error':str(ex)};error=True
                print('[RESULTADO]',resultado)
                salidas.append({'type':'tool_result','tool_use_id':b.id,'content':json.dumps(resultado,ensure_ascii=False),'is_error':error})
            mensajes.append({'role':'user','content':salidas})
        return 'Se ha alcanzado el límite de pasos. Escalo el caso a una persona.'
if __name__=='__main__':
    correo='Restaurante Lumbre: la cafetera de dos grupos no calienta; hoy no podemos servir café. ¿Cuándo llega el pedido pendiente?'
    print('\nRESPUESTA FINAL:\n'+Agente(max_pasos=int(os.getenv('MAX_PASOS','8'))).ejecutar(correo))
