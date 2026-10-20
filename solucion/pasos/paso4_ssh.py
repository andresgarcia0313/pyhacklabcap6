"""
Paso 4: abrir la sesión SSH al objetivo simulado y pedirle datos.
El simulador debe estar corriendo y LAB06_PASSWORD definida.
Uso: LAB06_PASSWORD='laboratorio123' python3 pasos/paso4_ssh.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PUERTO_SSH, TARGET_HOST, credenciales  # noqa: E402
from ssh_cliente import conectar, descargar, enumerar  # noqa: E402

usuario, clave = credenciales()
if not clave:
    sys.exit("[!] Defina LAB06_PASSWORD con la clave del laboratorio y vuelva a intentarlo")

cliente = conectar(TARGET_HOST, PUERTO_SSH, usuario, clave)
if cliente is None:
    sys.exit(1)
try:
    for nombre, valor in enumerar(cliente).items():
        print(f"[{nombre.upper()}] {valor.splitlines()[0]}")
    print(f"\nArchivo por SFTP: {descargar(cliente, '/informe.txt').decode().splitlines()[0]}")
finally:
    cliente.close()
