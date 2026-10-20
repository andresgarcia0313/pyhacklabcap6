"""
escaneo.py - Mira qué puertos están abiertos (Paso 2).

Para saber si un servicio está escuchando en un puerto, se intenta abrir una
conexión TCP (Transmission Control Protocol, protocolo de control de transmisión)
a ese puerto. Si la conexión se completa, el puerto está ABIERTO. Si el equipo
contesta "aquí no hay nadie", está CERRADO. Si no contesta nada, está FILTRADO.

Esta forma de mirar usa el mismo tipo de conexión que un navegador o un cliente
de correo, así que funciona en su propio equipo sin permisos de administrador.
"""
import concurrent.futures  # incluido en Python: hacer varias cosas a la vez
import socket              # incluido en Python: conexiones de red de bajo nivel

from config import TIMEOUT_PUERTO, verificar_red

# Etiquetas de estado, en un solo lugar para no escribir el texto repetido.
ABIERTO, CERRADO, FILTRADO = "ABIERTO", "CERRADO", "FILTRADO"


def estado_puerto(host: str, puerto: int, timeout: float = TIMEOUT_PUERTO) -> str:
    """
    Intenta conectar a host:puerto y traduce el resultado a una palabra.
    Devuelve ABIERTO, CERRADO o FILTRADO. No envía ni lee datos: solo toca la puerta.
    """
    verificar_red(host)  # control de uso responsable: ANTES de abrir la conexión
    # socket() crea el "teléfono" de red; AF_INET es IPv4 y SOCK_STREAM es TCP.
    # "with ... as s" garantiza que el socket se cierre al salir del bloque.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)  # cuánto esperar antes de rendirse
        # connect_ex devuelve 0 si la conexión se logró, o un número de error si no.
        # A diferencia de connect, no lanza excepción: entrega el código y seguimos.
        codigo = s.connect_ex((host, puerto))
    if codigo == 0:
        return ABIERTO
    # errno 111 (ECONNREFUSED) es "conexión rechazada": alguien dijo que no, puerto cerrado.
    if codigo == socket.errno.ECONNREFUSED:
        return CERRADO
    return FILTRADO  # cualquier otro caso (por ejemplo, se agotó el tiempo sin respuesta)


def escanear(host: str, puertos: dict, max_hilos: int = 10) -> dict:
    """
    Mira todos los puertos a la vez y devuelve {puerto: estado}.
    Mirar es sobre todo ESPERAR a la red; con varios hilos las esperas ocurren
    en paralelo y todo termina antes.
    """
    verificar_red(host)  # una sola comprobación para todo el escaneo
    resultados = {}  # diccionario vacío que se irá llenando
    # ThreadPoolExecutor arma un grupo de trabajadores; "with" los cierra al terminar.
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_hilos) as ejecutor:
        # submit entrega una tarea y devuelve un FUTURO (un resultado que llegará luego).
        # Se arma {futuro: puerto} para saber, al final, a qué puerto corresponde cada uno.
        # Se lee: "para cada p de puertos, guarda futuro -> p" (comprensión de diccionario).
        futuros = {ejecutor.submit(estado_puerto, host, p): p for p in puertos}
        for futuro in concurrent.futures.as_completed(futuros):  # cada uno apenas termina
            resultados[futuros[futuro]] = futuro.result()
    # Los hilos terminan en cualquier orden: se reordena por número de puerto.
    # sorted(...) ordena las claves; se arma un diccionario nuevo ya ordenado.
    return {p: resultados[p] for p in sorted(resultados)}


if __name__ == "__main__":
    # __name__ vale "__main__" solo si se ejecuta este archivo directamente
    # (python3 escaneo.py), y no cuando otro archivo lo importa.
    from config import PUERTOS, TARGET_HOST
    for puerto, estado in escanear(TARGET_HOST, PUERTOS).items():
        # En un f-string, {puerto:>5} alinea el número a la derecha en 5 espacios.
        print(f"Puerto {puerto:>5}/tcp  {estado}  ({PUERTOS[puerto]})")
