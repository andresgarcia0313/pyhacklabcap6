"""Pruebas de la sesión SSH contra el servidor simulado real, en 127.0.0.1 y puerto efímero."""
import io
import unittest
from contextlib import redirect_stdout

from servicios_simulados import ARCHIVO_SFTP, CLAVE_SIM, USUARIO_SIM, ServidorSSH
from ssh_cliente import COMANDOS, conectar, descargar, enumerar

HOST = "127.0.0.1"


class SSHSimuladoTest(unittest.TestCase):
    def setUp(self):
        self.servidor = ServidorSSH(HOST, 0)  # puerto 0: el sistema elige uno libre
        self.servidor.start()
        self.puerto = self.servidor.puerto

    def tearDown(self):
        self.servidor.detener()

    def test_conexion_correcta_enumera_los_tres_comandos(self):
        cliente = conectar(HOST, self.puerto, USUARIO_SIM, CLAVE_SIM)
        self.assertIsNotNone(cliente)
        try:
            datos = enumerar(cliente)
        finally:
            cliente.close()
        self.assertEqual(set(datos), set(COMANDOS))
        self.assertIn("laboratorio", datos["usuario"])
        self.assertIn("Linux", datos["sistema"])

    def test_clave_incorrecta_devuelve_none(self):
        with redirect_stdout(io.StringIO()):  # el aviso de credenciales no ensucia la salida
            resultado = conectar(HOST, self.puerto, USUARIO_SIM, "clave-mala")
        self.assertIsNone(resultado)

    def test_sftp_descarga_el_archivo_de_ejemplo(self):
        cliente = conectar(HOST, self.puerto, USUARIO_SIM, CLAVE_SIM)
        try:
            contenido = descargar(cliente, "/informe.txt")
        finally:
            cliente.close()
        self.assertEqual(contenido, ARCHIVO_SFTP)


if __name__ == "__main__":
    unittest.main()
