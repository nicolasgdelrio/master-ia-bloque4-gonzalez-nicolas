# Sesión 1 — Prácticas P1 a P5

Nicolás González del Río

La entrega E1 está en la carpeta `e1` e incluye:
- `llm_client.py`: interfaz común.
- `comparativa.csv`: resultados y puntuaciones.
- `analisis.md`: análisis de los resultados.

## Preparación del entorno
He creado el entorno virtual, instalado las dependencias, creado la base de datos y configurado la clave de OpenRouter en un archivo .env que no se publica.

## Modificaciones del código
He añadido max_output_tokens=1024 en OpenAI y max_tokens=1024 en Gemini mediante OpenRouter para solucionar el error 402 por solicitar un máximo de tokens demasiado alto.

## 1. ¿Qué proveedor responde antes? ¿Se mantiene entre ejecuciones?
OpenAI fue el más rápido en ambas ejecuciones. El orden se mantuvo: OpenAI, Claude y Gemini.

| Proveedor | Primera ejecución | Segunda ejecución |
|---|---:|---:|
| OpenAI | 2,20 s | 2,27 s |
| Claude | 2,79 s | 2,34 s |
| Gemini | 6,44 s | 5,82 s |

## 2. ¿Por qué no coinciden los tokens de entrada?
Cada modelo utiliza un tokenizador diferente y divide el texto en fragmentos distintos. También puede influir cómo cada API representa los mensajes. OpenAI registró 93 tokens de entrada, Claude 131 y Gemini 85 en ambas ejecuciones.

## 3. ¿Lo clasifican bien los tres?
Sí. Los tres clasificaron el correo como mixto en ambas ejecuciones porque incluye una incidencia con la cafetera y una consulta sobre el pedido 1004.

## 4. ¿Cambia la redacción entre ejecuciones?
Sí, cambia la redacción y algunos detalles, aunque se mantiene la clasificación. Por ejemplo, Claude primero promete contactar en la próxima hora y después asegura que el pedido saldrá mañana por la mañana. Gemini mantiene una respuesta muy parecida.

También he observado que algunas respuestas afirman acciones no comprobadas, como haber avisado al servicio técnico o garantizar la entrega del pedido.
