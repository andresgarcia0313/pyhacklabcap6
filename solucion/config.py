"""
config.py - Configuración central del reconocimiento (Paso 1).

Este texto entre tres comillas dobles es un DOCSTRING: una nota que describe el
archivo. Python no la ejecuta; está ahí para quien lee el código.

Qué hace este archivo: guarda en un solo lugar los valores que podrían cambiar
(a qué equipo se apunta, qué puertos se miran, qué red está permitida y de dónde
salen las credenciales). Los demás archivos toman estos valores de aquí.

Glosario de redes:
  - Host: el equipo con el que hablamos. "127.0.0.1" (también llamado "localhost"
    o "loopback") es SU PROPIO computador: el tráfico nunca sale de él.
  - Puerto: número de 0 a 65535 que identifica a un servicio dentro de un equipo.
    Por costumbre, SSH (Secure Shell, consola remota cifrada) usa el 22.
  - Red: conjunto de direcciones escrito como 127.0.0.0/8 (notación CIDR, Classless
    Inter-Domain Routing): el /8 indica cuántos bits iniciales son fijos.
"""
import ipaddress  # incluido en Python: entiende direcciones y redes IP
import os          # incluido en Python: lee variables del entorno del sistema

# Las líneas que empiezan con # son COMENTARIOS: Python las ignora por completo.
# Sirven para explicar el código. En este laboratorio hay muchos: léalos todos.

# ---------------------------------------------------------------------------
# OBJETIVO Y RED PERMITIDA
# ---------------------------------------------------------------------------
# Una VARIABLE es un nombre que guarda un valor. El signo = significa "guardar":
# a la izquierda el nombre, a la derecha el valor. Lo que va entre comillas es TEXTO.
# Por costumbre, los valores que no cambian se escriben en MAYÚSCULAS.
TARGET_HOST = "127.0.0.1"  # el objetivo simulado, dentro de su propio equipo

# RED PERMITIDA: el reconocimiento se niega a actuar sobre cualquier red que no esté
# contenida aquí. 127.0.0.0/8 es toda la familia loopback: su equipo, nada más.
# Mirar equipos sin autorización escrita es ilegal en muchos países.
RED_PERMITIDA = "127.0.0.0/8"

# ---------------------------------------------------------------------------
# PUERTOS A MIRAR
# ---------------------------------------------------------------------------
# Las llaves con pares "clave: valor" forman un DICCIONARIO (dict): una tabla que
# asocia cada clave con su valor. Aquí, cada puerto con el servicio que esperamos.
# El simulador abre los servicios en el puerto estándar + 10 000 (SSH, que usa el
# 22, queda en 10022), así no se necesitan permisos de administrador ni se choca
# con servicios reales del equipo. Dos de estos puertos quedan cerrados a propósito.
PUERTOS = {
    10021: "FTP",    # transferencia de archivos
    10022: "SSH",    # consola remota cifrada (el simulador sí responde aquí)
    10025: "SMTP",   # envío de correo
    10080: "HTTP",   # servidor web (cerrado en el simulador)
    13306: "MySQL",  # base de datos (cerrado en el simulador)
}
PUERTO_SSH = 10022  # el puerto donde el reconocimiento intentará la sesión SSH

# ---------------------------------------------------------------------------
# PARÁMETROS DE CONEXIÓN
# ---------------------------------------------------------------------------
# Un número con punto decimal es un FLOTANTE (float): 2.0 significa dos segundos.
TIMEOUT_PUERTO = 1.0   # segundos máximos esperando a que un puerto conteste
TIMEOUT_SSH    = 10.0  # segundos máximos esperando la sesión SSH
DIRECTORIO_SALIDA = "salida"  # carpeta RELATIVA donde se guardan los reportes


# ---------------------------------------------------------------------------
# CREDENCIALES: SIEMPRE DESDE EL ENTORNO, NUNCA ESCRITAS EN EL CÓDIGO
# ---------------------------------------------------------------------------
# "def" define una FUNCIÓN: un bloque con nombre que se ejecuta al llamarlo.
# "-> tuple" indica que devuelve una tupla (varios valores juntos).
def credenciales() -> tuple:
    """Lee usuario y clave de las variables de entorno. Nunca van en el código."""
    # os.environ.get("NOMBRE", "valor_por_defecto") lee una variable del entorno;
    # si no está definida, usa el valor de la derecha. El usuario del laboratorio
    # es público, pero la clave se exige por entorno para no dejarla escrita aquí.
    usuario = os.environ.get("LAB06_USUARIO", "laboratorio")
    clave = os.environ.get("LAB06_PASSWORD")  # sin valor por defecto: hay que darla
    return usuario, clave


# ---------------------------------------------------------------------------
# CONTROL DE USO RESPONSABLE
# ---------------------------------------------------------------------------
def verificar_red(objetivo: str) -> None:
    """Detiene el programa si el objetivo no está dentro de la red permitida."""
    # ip_network entiende tanto una IP suelta ("127.0.0.1") como una red ("127.0.0.0/8").
    # strict=False acepta una IP de host sin quejarse de los bits sobrantes.
    red_objetivo = ipaddress.ip_network(objetivo, strict=False)
    permitida = ipaddress.ip_network(RED_PERMITIDA)
    # subnet_of pregunta "¿esta red cabe entera dentro de la permitida?".
    # "not" invierte la respuesta: si NO cabe, se lanza un error ANTES de tocar la red.
    if not red_objetivo.subnet_of(permitida):
        raise PermissionError(f"El objetivo {objetivo} está fuera de la red permitida {RED_PERMITIDA}")
