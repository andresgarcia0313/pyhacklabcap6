"""
Paso 5: generar un reporte JSON con datos de ejemplo, sin tocar la red.
Uso: python3 pasos/paso5_reporte.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reporte import generar_json, imprimir_resumen  # noqa: E402

puertos = {10021: "ABIERTO", 10022: "ABIERTO", 10025: "ABIERTO", 10080: "CERRADO", 13306: "CERRADO"}
enumeracion = {"sistema": "Linux objetivo-lab 5.15.0", "usuario": "uid=1000(laboratorio)"}

imprimir_resumen(puertos, enumeracion, "127.0.0.1")
ruta = generar_json(puertos, enumeracion, "127.0.0.1")
print(f"Reporte de ejemplo guardado en: {ruta}")
