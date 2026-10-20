"""
Paso 1: revisar la configuración central (config.py).
Uso (desde la carpeta de trabajo): python3 pasos/paso1_configuracion.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402  (va después de ajustar sys.path)

print(f"Objetivo (TARGET_HOST): {config.TARGET_HOST}")
print(f"Red permitida (RED_PERMITIDA): {config.RED_PERMITIDA}")
print(f"Puerto donde se intenta SSH: {config.PUERTO_SSH}")
print(f"\n{'Puerto':>8}  {'Servicio esperado'}")
for puerto, servicio in config.PUERTOS.items():
    print(f"{puerto:>8}  {servicio}")
usuario, clave = config.credenciales()
print(f"\nUsuario del laboratorio: {usuario}")
print(f"¿Hay clave en el entorno (LAB06_PASSWORD)?: {'sí' if clave else 'no'}")
