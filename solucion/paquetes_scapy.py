"""
paquetes_scapy.py - Arma paquetes de red a mano con Scapy (Paso 3).

Scapy es una librería que permite CONSTRUIR un paquete de red capa por capa y
mirar cada campo, como armar un sobre y leer lo que lleva escrito. Construir y
mirar un paquete no necesita permisos especiales y no envía nada.

Enviarlo de verdad y leer la respuesta sí necesita permisos de administrador
(se ejecuta con sudo), porque el sistema reserva esa capacidad. Por eso este
archivo separa las dos cosas: construir y clasificar (cualquiera puede) y enviar
(solo con sudo). Para mirar puertos sin permisos, use escaneo.py del Paso 2.
"""
import random  # incluido en Python: números al azar
import sys      # incluido en Python: argumentos de la línea de comandos

# De Scapy se traen solo las piezas que se usan. IP es la capa de dirección,
# TCP la de puertos y banderas, conf/sr1/send controlan el envío.
from scapy.all import IP, TCP, conf, send, sr1

from config import verificar_red

conf.verb = 0  # silencia los mensajes automáticos de Scapy


def construir_syn(host: str, puerto: int, origen: int) -> IP:
    """
    Arma un paquete que toca la puerta de un puerto, sin completar la conexión.
    El signo / en Scapy APILA capas: IP(...) / TCP(...) mete la capa TCP dentro de la IP.
    flags="S" marca el paquete como "inicio de conexión". No se envía aquí.
    """
    verificar_red(host)  # control de uso responsable: incluso al solo construir
    return IP(dst=host) / TCP(sport=origen, dport=puerto, flags="S")


def clasificar_respuesta(respuesta) -> str:
    """Traduce la respuesta del objetivo a una palabra: ABIERTO, CERRADO o FILTRADO."""
    # "is None" es verdadero cuando no llegó respuesta. haslayer pregunta si el
    # paquete trae una capa TCP; sin ella, no hay nada que interpretar.
    if respuesta is None or not respuesta.haslayer(TCP):
        return "FILTRADO"
    banderas = str(respuesta[TCP].flags)  # las banderas como texto, por ejemplo "SA"
    if banderas == "SA":   # el objetivo aceptó: puerto abierto
        return "ABIERTO"
    if "R" in banderas:    # el objetivo cortó en seco: puerto cerrado
        return "CERRADO"
    return f"DESCONOCIDO ({banderas})"


def syn_scan(host: str, puertos: list, timeout: float = 1.0) -> dict:
    """
    Envía un paquete a cada puerto y clasifica la respuesta. REQUIERE sudo.
    Si un puerto responde que acepta, se envía de inmediato un corte para no dejar
    la conexión a medias. Devuelve {puerto: estado}.
    """
    verificar_red(host)
    resultados = {}
    for puerto in puertos:
        origen = random.randint(1024, 65535)  # un puerto de salida distinto cada vez
        respuesta = sr1(construir_syn(host, puerto, origen), timeout=timeout, verbose=0)
        estado = clasificar_respuesta(respuesta)
        if estado == "ABIERTO":  # cerrar con cortesía lo que abrimos
            send(IP(dst=host) / TCP(sport=origen, dport=puerto, flags="R", seq=respuesta[TCP].ack), verbose=0)
        resultados[puerto] = estado
    return resultados


if __name__ == "__main__":
    # Sin sudo: arma un paquete y muestra sus campos, sin enviarlo. Esto siempre funciona.
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    paquete = construir_syn(host, 10022, 40000)
    print("Paquete armado (todavía sin enviar):")
    print("   ", paquete.summary())  # resumen en una línea de lo que lleva el paquete
    print(f"    Bandera TCP: {paquete[TCP].flags}  destino: puerto {paquete[TCP].dport}")
    print("\nPara enviarlo de verdad y leer la respuesta se necesitan permisos:")
    print(f"    sudo python3 paquetes_scapy.py   (envía a {host})")
    print("Sin permisos, mire los puertos con el Paso 2:  python3 escaneo.py")
