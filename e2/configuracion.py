"""Carga la configuración existente sin incluir claves en la entrega."""
import os
from pathlib import Path
from dotenv import load_dotenv


def cargar():
    ruta = os.getenv('E2_ENV_FILE')
    if ruta:
        load_dotenv(ruta)
    else:
        for carpeta in (Path(__file__).parent, Path(__file__).parent.parent, Path.cwd()):
            if (carpeta / '.env').is_file():
                load_dotenv(carpeta / '.env')
                break


cargar()
