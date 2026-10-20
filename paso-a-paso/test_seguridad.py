"""Pruebas de los controles de uso responsable. Usan mocks: nada sale a la red."""
import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

import config
import escaneo
import recon
import ssh_cliente

FUERA_DE_RED = "8.8.8.8"  # un equipo de Internet: jamás debe tocarse desde el laboratorio


class SeguridadTest(unittest.TestCase):
    def test_solo_loopback_permitido(self):  # laboratorio 100 % local
        self.assertEqual(config.RED_PERMITIDA, "127.0.0.0/8")
        self.assertEqual(config.TARGET_HOST, "127.0.0.1")

    def test_verificar_red_rechaza_internet(self):
        with self.assertRaises(PermissionError):
            config.verificar_red("8.8.8.0/24")

    def test_escaneo_fuera_de_red_no_abre_socket(self):
        with mock.patch.object(escaneo.socket, "socket") as falso:
            with self.assertRaises(PermissionError):
                escaneo.estado_puerto(FUERA_DE_RED, 22)
        falso.assert_not_called()

    def test_ssh_fuera_de_red_no_conecta(self):
        with mock.patch.object(ssh_cliente.paramiko, "SSHClient") as falso:
            with self.assertRaises(PermissionError):
                ssh_cliente.conectar(FUERA_DE_RED, 22, "u", "c")
        falso.assert_not_called()

    def test_reconocer_rechaza_red_ajena(self):
        with self.assertRaises(PermissionError):
            recon.reconocer("8.8.8.0/24", {}, "u", "c", mirar=lambda *a: {})

    def test_main_rechaza_objetivo_no_permitido(self):
        with mock.patch.object(recon, "TARGET_HOST", FUERA_DE_RED), \
             mock.patch.object(recon, "reconocer") as reconocer, \
             redirect_stdout(io.StringIO()):
            self.assertEqual(recon.main(), 2)
        reconocer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
