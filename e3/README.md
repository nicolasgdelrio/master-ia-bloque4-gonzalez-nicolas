# E3 — Agente de atención técnica

Proyecto de soporte para Tostadero Retiro S.L. con dos implementaciones: un bucle de herramientas en Python y una versión basada en LangChain.

## Archivos

- `s3_agente.py`: bucle de agente con límite de pasos, registro de llamadas y confirmación de operaciones de escritura.
- `s3_agente_langchain.py`: agente con middleware de aprobación humana y límite de llamadas.
- `herramientas.py`: consultas y registro de incidencias sobre SQLite.
- `crear_bd.py`: inicialización de la base de datos de ejemplo.
- `comparacion_E3.pdf`: comparación de las implementaciones.
- `tests/`: pruebas automatizadas de las herramientas y la base de datos.

## Ejecución

Python 3.11 o superior. Desde la carpeta `e3`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configurar `ANTHROPIC_API_KEY` y `ANTHROPIC_MODEL` en `.env`. El archivo `.env` queda excluido del repositorio.

```powershell
.\.venv\Scripts\python.exe crear_bd.py
.\.venv\Scripts\python.exe s3_agente.py
.\.venv\Scripts\python.exe s3_agente_langchain.py
```

Los dos agentes emplean el mismo caso de consulta: la avería de la cafetera de dos grupos y un pedido pendiente del Restaurante Lumbre. Toda escritura de incidencias requiere confirmación previa.

## Pruebas locales

```powershell
python -m unittest discover -s tests -v
```

Para conservar las trazas de ejecución se puede redirigir la salida de cada agente a un archivo de texto. La introducción de la aprobación humana se hace de forma interactiva en la terminal.
