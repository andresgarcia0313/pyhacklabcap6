"""
ssh_cliente.py - Sesión SSH automatizada con Paramiko (Paso 4).

SSH (Secure Shell) es una consola remota cifrada: permite entrar a otro equipo y
ejecutar comandos como si estuviera sentado frente a él. Paramiko es la librería
que habla SSH desde Python. Aquí nos conectamos al objetivo simulado, pedimos unos
datos del sistema y descargamos un archivo por SFTP (SSH File Transfer Protocol,
transferencia de archivos sobre SSH).

La clave NUNCA se escribe en el código: llega desde el entorno (config.credenciales).
"""
import io    # incluido en Python: manejar datos en memoria como si fueran un archivo
import sys   # incluido en Python: argumentos y salida del programa

import paramiko  # librería EXTERNA para hablar SSH (se instaló con pip en el Paso 0)

from config import PUERTO_SSH, TARGET_HOST, TIMEOUT_SSH, credenciales, verificar_red

# Comandos de reconocimiento: nombre legible -> orden que se ejecuta en el objetivo.
COMANDOS = {"sistema": "uname -a", "usuario": "id", "version": "cat /etc/os-release"}


def conectar(host: str, puerto: int, usuario: str, clave: str, timeout: float = TIMEOUT_SSH):
    """Abre la sesión SSH. Devuelve el cliente, o None si la autenticación o la red fallan."""
    verificar_red(host)  # control de uso responsable: ANTES de conectar
    cliente = paramiko.SSHClient()
    # En el laboratorio aceptamos la identidad del servidor sin verificarla. En
    # un sistema real esto se revisa: aceptar a ciegas permitiría a un impostor colarse.
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        cliente.connect(hostname=host, port=puerto, username=usuario, password=clave,
                        timeout=timeout, look_for_keys=False, allow_agent=False)
        return cliente
    except paramiko.AuthenticationException:  # usuario o clave incorrectos
        print("[!] Credenciales incorrectas")
    except (paramiko.SSHException, OSError) as error:  # sin servicio, red caída, etc.
        print(f"[!] Error de conexión: {error}")
    return None  # cualquiera de los fallos deja el resultado en None


def enumerar(cliente, comandos: dict = COMANDOS) -> dict:
    """Ejecuta cada comando en el objetivo y devuelve {nombre: salida de texto}."""
    resultados = {}
    for nombre, comando in comandos.items():
        # exec_command devuelve tres canales: entrada, salida y errores. Solo leemos
        # salida y errores. El guion bajo _ es "no me interesa este valor".
        _, salida, error = cliente.exec_command(comando)
        texto = salida.read().decode("utf-8", errors="replace").strip()
        # "a or b" entrega a si a tiene contenido, o b si a está vacío: si no hubo
        # salida, guardamos el texto del error en su lugar.
        resultados[nombre] = texto or error.read().decode("utf-8", errors="replace").strip()
    return resultados


def descargar(cliente, remoto: str) -> bytes:
    """Descarga un archivo del objetivo por SFTP y devuelve su contenido en bytes."""
    sftp = cliente.open_sftp()  # abre el canal de archivos sobre la misma sesión
    try:
        buffer = io.BytesIO()        # un "archivo" que vive en memoria, no en disco
        sftp.getfo(remoto, buffer)   # copia el archivo remoto dentro del buffer
        return buffer.getvalue()
    finally:
        sftp.close()  # pase lo que pase, se cierra el canal de archivos


# __name__ vale "__main__" solo cuando este archivo se ejecuta directamente
# (python3 ssh_cliente.py), y no cuando otro archivo lo importa.
if __name__ == "__main__":
    usuario, clave = credenciales()  # una función que devuelve 2 valores se recibe en 2 variables
    if not clave:  # sin clave en el entorno no se intenta nada
        sys.exit("[!] Defina LAB06_PASSWORD con la clave del laboratorio y vuelva a intentarlo")
    cliente = conectar(TARGET_HOST, PUERTO_SSH, usuario, clave)
    if cliente is None:
        sys.exit(1)  # sys.exit termina el programa; 1 avisa al sistema que algo falló
    try:
        for nombre, valor in enumerar(cliente).items():
            # f"..." es un f-string: lo que va entre { } se reemplaza por su valor.
            # .upper() pasa a mayúsculas y .splitlines()[0] toma solo la primera línea.
            print(f"[{nombre.upper()}] {valor.splitlines()[0]}")
        # .decode() convierte los bytes recibidos en texto para poder mostrarlos.
        print(f"\nArchivo por SFTP: {descargar(cliente, '/informe.txt').decode().splitlines()[0]}")
    finally:
        cliente.close()
