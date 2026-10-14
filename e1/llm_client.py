"""Sesión 1. Una interfaz común para varios proveedores (patrón Adapter)."""

import os
import time
from dataclasses import dataclass

import anthropic
import openai
from dotenv import load_dotenv
from google import genai

load_dotenv()

OPENROUTER = "https://openrouter.ai/api/v1"

# Precios de referencia consultados el 13/10/2026 en OpenRouter.
# Dólares por millón de tokens: (entrada, salida).
# Estimación para texto, sin descuentos por caché.
PRECIOS: dict[str, tuple[float, float]] = {
    "openai/gpt-5.4-mini": (0.75, 4.50),
    "anthropic/claude-haiku-4.5": (1.00, 5.00),
    "google/gemini-3.8-flash": (0.75, 3.75),
}


@dataclass
class Respuesta:
    texto: str
    tokens_entrada: int
    tokens_salida: int
    segundos: float
    modelo: str

    @property
    def coste_usd(self) -> float | None:
        precios = PRECIOS.get(self.modelo)

        if precios is None:
            return None

        precio_entrada, precio_salida = precios

        return (
            self.tokens_entrada * precio_entrada
            + self.tokens_salida * precio_salida
        ) / 1_000_000


class LLM:
    """Interfaz común para OpenAI, Claude, Gemini y Ollama."""

    def __init__(self, proveedor: str, modelo: str | None = None):
        self.proveedor = proveedor

        modelos_defecto = {
            "openai": os.getenv("OPENAI_MODEL"),
            "claude": os.getenv("ANTHROPIC_MODEL"),
            "gemini": os.getenv("GEMINI_MODEL"),
            "ollama": "llama3.2",
        }

        if proveedor not in modelos_defecto:
            raise ValueError(f"Proveedor no soportado: {proveedor}")

        self.modelo = modelo or modelos_defecto[proveedor]

        if not self.modelo:
            raise ValueError(
                f"Falta configurar el modelo de {proveedor} en el archivo .env"
            )

        if proveedor == "openai":
            self.formato = "responses"
            # Lee OPENAI_API_KEY y OPENAI_BASE_URL del entorno.
            self._c = openai.OpenAI(max_retries=3)

        elif proveedor == "claude":
            self.formato = "messages"
            # Lee ANTHROPIC_API_KEY y ANTHROPIC_BASE_URL del entorno.
            self._c = anthropic.Anthropic(max_retries=3)

        elif proveedor == "gemini" and os.getenv("GEMINI_API_KEY"):
            self.formato = "interactions"
            self._c = genai.Client()

        elif proveedor == "gemini":
            self.formato = "chat"
            self._c = openai.OpenAI(
                base_url=OPENROUTER,
                api_key=os.environ["OPENROUTER_API_KEY"],
                max_retries=3,
            )

        else:
            self.formato = "chat"
            self._c = openai.OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )

    def responder(
        self,
        sistema: str,
        prompt: str,
        temperatura: float | None = None,
        max_tokens: int = 1024,
    ) -> Respuesta:
        """Genera una respuesta con un límite de tokens configurable."""

        if (
            isinstance(max_tokens, bool)
            or not isinstance(max_tokens, int)
            or max_tokens <= 0
        ):
            raise ValueError("max_tokens debe ser un entero positivo.")

        extra = {}
        if temperatura is not None:
            extra["temperature"] = temperatura

        inicio = time.perf_counter()

        if self.formato == "responses":
            r = self._c.responses.create(
                model=self.modelo,
                instructions=sistema,
                input=prompt,
                max_output_tokens=max_tokens,
                **extra,
            )

            texto = r.output_text
            tokens_entrada = r.usage.input_tokens
            tokens_salida = r.usage.output_tokens

        elif self.formato == "messages":
            r = self._c.messages.create(
                model=self.modelo,
                system=sistema,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                **extra,
            )

            texto = "".join(
                bloque.text
                for bloque in r.content
                if bloque.type == "text"
            )
            tokens_entrada = r.usage.input_tokens
            tokens_salida = r.usage.output_tokens

        elif self.formato == "interactions":
            config = {
                **extra,
                "max_output_tokens": max_tokens,
            }

            r = self._c.interactions.create(
                model=self.modelo.removeprefix("google/"),
                system_instruction=sistema,
                input=prompt,
                generation_config=config,
            )

            texto = r.output_text
            tokens_entrada = r.usage.total_input_tokens
            tokens_salida = r.usage.total_output_tokens

        else:
            r = self._c.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                **extra,
            )

            texto = r.choices[0].message.content or ""
            tokens_entrada = r.usage.prompt_tokens
            tokens_salida = r.usage.completion_tokens

        segundos = time.perf_counter() - inicio

        return Respuesta(
            texto=texto,
            tokens_entrada=tokens_entrada,
            tokens_salida=tokens_salida,
            segundos=segundos,
            modelo=self.modelo,
        )


if __name__ == "__main__":
    for proveedor in ["openai", "claude", "gemini"]:
        respuesta = LLM(proveedor).responder(
            sistema="Responde en una frase.",
            prompt="¿Qué es un token?",
            max_tokens=1024,
        )

        coste = respuesta.coste_usd
        coste_texto = (
            f"{coste:.8f} USD"
            if coste is not None
            else "sin precio configurado"
        )

        print(
            f"\n=== {proveedor.upper()} | "
            f"{respuesta.segundos:.2f} s | "
            f"{respuesta.tokens_entrada} tokens entrada | "
            f"{respuesta.tokens_salida} tokens salida | "
            f"Coste estimado: {coste_texto}"
        )
        print(respuesta.texto)