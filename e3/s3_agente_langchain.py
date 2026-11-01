"""Mismo caso con LangChain: middleware humano, límite, checkpoint y trazas."""
import os
from typing import Literal
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, ModelCallLimitMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from herramientas import buscar_cliente as buscar, consultar_pedidos as pedidos, crear_incidencia as incidencia
from s3_agente import SISTEMA
load_dotenv()
@tool
def buscar_cliente(texto:str)->list[dict]:
    """Busca un cliente por nombre antes de consultar su información."""
    return buscar(texto)
@tool
def consultar_pedidos(cliente_id:int)->list[dict]:
    """Lista los pedidos reales de un cliente identificado."""
    return pedidos(cliente_id)
@tool
def crear_incidencia(cliente_id:int,maquina:str,descripcion:str,prioridad:Literal['baja','media','alta'])->dict:
    """Registra una avería concreta, solo tras autorización humana."""
    return incidencia(cliente_id,maquina,descripcion,prioridad)

def main():
    agente=create_agent(model=f"anthropic:{os.environ['ANTHROPIC_MODEL']}",tools=[buscar_cliente,consultar_pedidos,crear_incidencia],system_prompt=SISTEMA,
      middleware=[HumanInTheLoopMiddleware(interrupt_on={'crear_incidencia':True}),ModelCallLimitMiddleware(run_limit=8)],checkpointer=InMemorySaver())
    cfg={'configurable':{'thread_id':'entrega-e3-lumbre'}}
    entrada={'messages':[{'role':'user','content':'Restaurante Lumbre: la cafetera de dos grupos no calienta y no podemos servir café. ¿Cuándo llega nuestro pedido pendiente?'}]}
    estado=agente.invoke(entrada,cfg)
    while True:
        for m in estado.get('messages',[]):
            print('[TRAZA]',getattr(m,'type','?'),str(getattr(m,'content',''))[:260])
        if '__interrupt__' not in estado: break
        decisiones=[]
        for peticion in estado['__interrupt__'][0].value['action_requests']:
            print('[INTERRUPCIÓN]',peticion)
            ok=input('¿Aprobar acción? [s/N] ').strip().lower()=='s'
            decisiones.append({'type':'approve' if ok else 'reject'})
        estado=agente.invoke(Command(resume={'decisions':decisiones}),cfg)
    print('\nRESPUESTA FINAL:',str(estado['messages'][-1].content))
if __name__=='__main__':main()
