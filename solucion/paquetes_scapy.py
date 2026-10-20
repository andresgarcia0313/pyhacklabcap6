"""
paquetes_scapy.py - Arma paquetes de red a mano con Scapy (Paso 3).

Scapy es una librería que permite CONSTRUIR un paquete de red capa por capa y
mirar cada campo, como armar un sobre y leer lo que lleva escrito. Construir y
mirar un paquete no necesita permisos especiales y no envía nada.

Enviarlo de verdad y leer la respuesta sí necesita permisos de administrador
(se ejecuta con sudo), porque el sistema reserva esa capacidad. Por eso este
archivo separa las dos cosas: construir y clasificar (cualquiera puede) y enviar
(solo con sudo y la opción --enviar). Para mirar puertos sin permisos, use escaneo.py.

Banderas TCP que aparecen aquí (son letras en inglés):
  S = SYN (synchronize, sincronizar): "quiero empezar una conexión".
  A = ACK (acknowledge, confirmar): "recibido".
  R = RST (reset, reiniciar): "corto la conexión".
"""
import random  # incluido en Python: números al azar
import sys      # incluido en Python: argumentos de la línea de comandos

# De Scapy se traen solo las piezas que se usan: IP es la capa de dirección, TCP la
# de puertos y banderas, conf guarda la configuración, send envía un paquete y
# sr1 (send and receive 1, enviar y recibir una respuesta) envía y espera la respuesta.
from scapy.all import IP, TCP, L3RawSocket, conf, send, sr1

from config import verificar_red

conf.verb = 0  # silencia los mensajes automáticos de Scapy
# En la interfaz loopback (127.0.0.1) Scapy necesita un socket "raw" (crudo) para
# leer bien las respuestas; sin este ajuste, un puerto abierto parecería cerrado.
conf.L3socket = L3RawSocket


def construir_syn(host: str, puerto: int, origen: int) -> IP:
    """
    Arma un paquete que toca la puerta de un puerto, sin completar la conexión.
    El signo / en Scapy APILA capas: IP(...) / TCP(...) mete la capa TCP dentro de la IP.
    dst (destination) es el destino; sport y dport (source/destination port) son los
    puertos de origen y de destino. flags="S" marca el inicio de conexión. No se envía aquí.
    """
    verificar_red(host)  # control de uso responsable: incluso al solo construir
    return IP(dst=host) / TCP(sport=origen, dport=puerto, flags="S")


def clasificar_respuesta(respuesta) -> str:
    """Traduce la respuesta del objetivo a una palabra: ABIERTO, CERRADO o FILTRADO."""
    # "is None" es verdadero cuando no llegó respuesta. haslayer ("tiene capa")
    # pregunta si el paquete trae una capa TCP; sin ella, no hay nada que interpretar.
    if respuesta is None or not respuesta.haslayer(TCP):
        return "FILTRADO"
    banderas = str(respuesta[TCP].flags)  # las banderas como texto, por ejemplo "SA"
    if banderas == "SA":   # SYN + ACK: el objetivo aceptó, puerto abierto
        return "ABIERTO"
    if "R" in banderas:    # RST: el objetivo cortó en seco, puerto cerrado
        return "CERRADO"
    return f"DESCONOCIDO ({banderas})"  # f-string: {banderas} se reemplaza por su valor


def syn_scan(host: str, puertos: list, timeout: float = 1.0) -> dict:
    """
    Envía un paquete a cada puerto y clasifica la respuesta. REQUIERE sudo.
    timeout es el tiempo máximo de espera, en segundos. Si un puerto acepta, se
    envía de inmediato un RST para no dejar la conexión a medias. Devuelve {puerto: estado}.
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


# __name__ vale "__main__" solo cuando este archivo se ejecuta directamente.
if __name__ == "__main__":
    # sys.argv es la lista de palabras escritas después de "python3": aquí se
    # pregunta si entre ellas está "--enviar".
    enviar = "--enviar" in sys.argv
    paquete = construir_syn("127.0.0.1", 10022, 40000)
    print("Paquete armado (todavía sin enviar):")
    print("   ", paquete.summary())  # summary: resumen en una línea de lo que lleva el paquete
    print(f"    Bandera TCP: {paquete[TCP].flags}  destino: puerto {paquete[TCP].dport}")
    if enviar:  # solo con permisos de administrador
        for puerto, estado in syn_scan("127.0.0.1", [10022, 10080]).items():
            print(f"    Enviado al puerto {puerto}: {estado}")
    else:
        print("\nPara enviarlo de verdad se necesitan permisos de administrador:")
        print("    sudo .venv/bin/python paquetes_scapy.py --enviar")
        print("Sin permisos, los puertos se miran con escaneo.py (Paso 2).")
