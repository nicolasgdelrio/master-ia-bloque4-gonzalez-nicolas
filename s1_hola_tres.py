"""Sesión 1. El mismo encargo a tres proveedores: respuesta, tokens y latencia."""
import os
import time

import anthropic
import openai
from dotenv import load_dotenv
from google import genai

load_dotenv()

OPENROUTER = "https://openrouter.ai/api/v1"
SISTEMA = (
    "Eres el asistente de atención al cliente de Tostadero Retiro S.L. "
    "Responde en español y en dos frases como máximo."
)
CORREO = (
    "Hola, soy Marta del Bar La Esquina. La cafetera vuelve a perder presión y mañana "
    "tenemos el pedido 1004 pendiente. ¿Me decís algo? Gracias"
)
PETICION = (
    "Clasifica este correo como pedido, incidencia, consulta o mixto y redacta "
    f"una respuesta breve:\n\n{CORREO}"
)


def con_openai() -> tuple[str, int, int]:
    cliente = openai.OpenAI()
    r = cliente.responses.create(
        model=os.environ["OPENAI_MODEL"],
        instructions=SISTEMA,
        input=PETICION,
        max_output_tokens=1024,
    )
    return r.output_text, r.usage.input_tokens, r.usage.output_tokens


def con_claude() -> tuple[str, int, int]:
    cliente = anthropic.Anthropic()
    r = cliente.messages.create(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=512,
        system=SISTEMA,
        messages=[{"role": "user", "content": PETICION}],
    )
    texto = "".join(b.text for b in r.content if b.type == "text")
    return texto, r.usage.input_tokens, r.usage.output_tokens


def con_gemini() -> tuple[str, int, int]:
    if os.getenv("GEMINI_API_KEY"):
        # Opcional: API nativa de Gemini.
        cliente = genai.Client()
        r = cliente.interactions.create(
            model=os.environ["GEMINI_MODEL"].removeprefix("google/"),
            system_instruction=SISTEMA,
            input=PETICION,
        )
        return r.output_text, r.usage.total_input_tokens, r.usage.total_output_tokens

    # Por defecto: Gemini a través de OpenRouter.
    cliente = openai.OpenAI(
        base_url=OPENROUTER,
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
    r = cliente.chat.completions.create(
        model=os.environ["GEMINI_MODEL"],
        messages=[
            {"role": "system", "content": SISTEMA},
            {"role": "user", "content": PETICION},
        ],
        max_tokens=1024,
    )
    return r.choices[0].message.content, r.usage.prompt_tokens, r.usage.completion_tokens


if __name__ == "__main__":
    for nombre, llamar in [
        ("OpenAI", con_openai),
        ("Claude", con_claude),
        ("Gemini", con_gemini),
    ]:
        inicio = time.perf_counter()
        texto, t_in, t_out = llamar()
        print(
            f"\n=== {nombre} | {time.perf_counter() - inicio:.2f} s | "
            f"{t_in} tokens entrada | {t_out} tokens salida\n{texto}"
        )