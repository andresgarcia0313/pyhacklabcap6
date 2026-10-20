"""Pruebas del escaneo contra sockets locales en 127.0.0.1 y de los paquetes de Scapy."""
import socket
import unittest

from scapy.all import IP, TCP

from escaneo import ABIERTO, CERRADO, escanear, estado_puerto
from paquetes_scapy import clasificar_respuesta, construir_syn

HOST = "127.0.0.1"


def puerto_escuchando() -> tuple:
    """Abre un socket que escucha en un puerto libre y lo devuelve junto con el número."""
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, 0))
    servidor.listen(1)
    return servidor, servidor.getsockname()[1]


def puerto_cerrado() -> int:
    """Reserva un puerto y lo libera de inmediato: queda cerrado, nadie escucha."""
    with socket.socket() as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]


class EscaneoLocalTest(unittest.TestCase):
    def test_puerto_con_servicio_es_abierto(self):
        servidor, puerto = puerto_escuchando()
        try:
            self.assertEqual(estado_puerto(HOST, puerto), ABIERTO)
        finally:
            servidor.close()

    def test_puerto_sin_servicio_es_cerrado(self):
        self.assertEqual(estado_puerto(HOST, puerto_cerrado()), CERRADO)

    def test_escanear_devuelve_estado_por_puerto_ordenado(self):
        servidor, abierto = puerto_escuchando()
        cerrado = puerto_cerrado()
        try:
            resultado = escanear(HOST, {cerrado: "x", abierto: "y"})
        finally:
            servidor.close()
        self.assertEqual(resultado[abierto], ABIERTO)
        self.assertEqual(resultado[cerrado], CERRADO)
        self.assertEqual(list(resultado), sorted(resultado))  # ordenado por puerto

    def test_construir_syn_marca_inicio_y_apunta_al_puerto(self):
        paquete = construir_syn(HOST, 10022, 40000)
        self.assertEqual(str(paquete[TCP].flags), "S")
        self.assertEqual(paquete[TCP].dport, 10022)

    def test_clasificar_respuesta_sa_abierto_r_cerrado_none_filtrado(self):
        self.assertEqual(clasificar_respuesta(IP() / TCP(flags="SA")), "ABIERTO")
        self.assertEqual(clasificar_respuesta(IP() / TCP(flags="RA")), "CERRADO")
        self.assertEqual(clasificar_respuesta(None), "FILTRADO")


if __name__ == "__main__":
    unittest.main()
