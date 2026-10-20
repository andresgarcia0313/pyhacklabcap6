"""
Paso 3: armar un paquete con Scapy y mirar sus campos, sin enviarlo.
No necesita el simulador ni permisos de administrador.
Uso: python3 pasos/paso3_paquete.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paquetes_scapy import construir_syn  # noqa: E402
from scapy.all import TCP  # noqa: E402

paquete = construir_syn("127.0.0.1", 10022, 40000)
print("Resumen del paquete:")
print("   ", paquete.summary())
print(f"\nBandera TCP: {paquete[TCP].flags}  (S = inicio de conexión)")
print(f"Puerto de origen: {paquete[TCP].sport}  ->  Puerto de destino: {paquete[TCP].dport}")
