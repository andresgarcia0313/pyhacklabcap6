"""
Paso 2: mirar los puertos del objetivo simulado (debe estar corriendo en otra terminal).
Uso: python3 pasos/paso2_escaneo.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PUERTOS, TARGET_HOST  # noqa: E402
from escaneo import escanear  # noqa: E402

print(f"Mirando {len(PUERTOS)} puertos en {TARGET_HOST}...\n")
for puerto, estado in escanear(TARGET_HOST, PUERTOS).items():
    print(f"Puerto {puerto:>5}/tcp  {estado}  ({PUERTOS[puerto]})")
