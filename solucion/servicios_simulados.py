"""
servicios_simulados.py
Objetivo falso que imita a un equipo de práctica. Escucha solo en 127.0.0.1, así
que ningún otro computador puede alcanzarlo y ningún paquete sale de su equipo.

Levanta:
  - Un servidor SSH real (con Paramiko) en el puerto 10022, que acepta un usuario
    y una clave fijos, responde a unos comandos con salidas de ejemplo y entrega un
    archivo por SFTP. No hay un sistema operativo real detrás: son respuestas guardadas.
  - Dos puertos TCP que solo aceptan la conexión (10021 y 10025), para que el
    escaneo encuentre puertos abiertos además del de SSH.
"""
import io
import logging
import socket
import threading

import paramiko

# El escaneo de puertos toca el puerto SSH y cierra sin saludar; eso haría que
# Paramiko imprima errores en la consola. Se silencia su registro para dejar la
# salida del laboratorio limpia: no son fallos, es el escaneo haciendo su trabajo.
logging.getLogger("paramiko").setLevel(logging.CRITICAL)

HOST_SIMULADOR = "127.0.0.1"
PUERTO_SSH_SIM = 10022
PUERTOS_TCP_ABIERTOS = (10021, 10025)  # solo aceptan la conexión; sin servicio real detrás
USUARIO_SIM = "laboratorio"            # usuario público del laboratorio
CLAVE_SIM = "laboratorio123"           # el servidor conoce su propia clave; el cliente la recibe por entorno

# Respuestas de ejemplo para cada comando de enumeración.
SALIDAS = {
    "uname -a": "Linux objetivo-lab 5.15.0-91-generic #1 SMP x86_64 GNU/Linux\n",
    "id": "uid=1000(laboratorio) gid=1000(laboratorio) grupos=1000(laboratorio)\n",
    "cat /etc/os-release": 'NAME="Ubuntu"\nVERSION="22.04.3 LTS (Jammy Jellyfish)"\n',
}
ARCHIVO_SFTP = b"informe de practica del objetivo simulado\nnada real detras\n"
_HOSTKEY = paramiko.RSAKey.generate(2048)  # identidad del servidor, nueva en cada arranque


class _Sesion(paramiko.ServerInterface):
    """Decide qué se permite en la sesión SSH y guarda el comando que pide el cliente."""

    def __init__(self):
        self._comandos, self._eventos = {}, {}

    def _evento(self, canal):
        return self._eventos.setdefault(canal.get_id(), threading.Event())

    def check_auth_password(self, usuario, clave):
        ok = usuario == USUARIO_SIM and clave == CLAVE_SIM
        return paramiko.AUTH_SUCCESSFUL if ok else paramiko.AUTH_FAILED

    def get_allowed_auths(self, usuario):
        return "password"

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, canal, comando):
        self._comandos[canal.get_id()] = comando.decode()
        self._evento(canal).set()
        return True


class _SFTP(paramiko.SFTPServerInterface):
    """Entrega siempre el mismo archivo de ejemplo, sin importar la ruta pedida."""

    def stat(self, path):
        attr = paramiko.SFTPAttributes()
        attr.st_size, attr.st_mode = len(ARCHIVO_SFTP), 0o100644
        return attr

    lstat = stat

    def open(self, path, flags, attr):
        handle = paramiko.SFTPHandle(flags)
        handle.readfile = io.BytesIO(ARCHIVO_SFTP)
        return handle


def _responder(sesion, canal):
    """Espera el comando del cliente, envía la salida de ejemplo y cierra el canal."""
    if not sesion._evento(canal).wait(10):
        canal.close()
        return
    comando = sesion._comandos.get(canal.get_id(), "")
    canal.sendall(SALIDAS.get(comando, f"sh: {comando}: no encontrado\n").encode())
    canal.send_exit_status(0 if comando in SALIDAS else 127)
    canal.close()


def _atender_ssh(conexion):
    """Negocia SSH sobre una conexión aceptada y atiende sus canales."""
    transporte = paramiko.Transport(conexion)
    transporte.add_server_key(_HOSTKEY)
    transporte.set_subsystem_handler("sftp", paramiko.SFTPServer, _SFTP)
    sesion = _Sesion()
    transporte.start_server(server=sesion)
    while transporte.is_active():
        canal = transporte.accept(5)
        if canal is None:
            break
        threading.Thread(target=_responder, args=(sesion, canal), daemon=True).start()


class _ServidorHilo(threading.Thread):
    """Base: un socket que acepta conexiones en un hilo hasta que se le pide parar."""

    def __init__(self, host, puerto):
        super().__init__(daemon=True)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, puerto))
        self._sock.listen(5)
        self.puerto = self._sock.getsockname()[1]
        self._parar = threading.Event()

    def manejar(self, conexion):
        raise NotImplementedError

    def run(self):
        self._sock.settimeout(0.5)
        while not self._parar.is_set():
            try:
                conexion, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self.manejar, args=(conexion,), daemon=True).start()

    def detener(self):
        self._parar.set()
        self._sock.close()


class ServidorSSH(_ServidorHilo):
    def manejar(self, conexion):
        try:
            _atender_ssh(conexion)
        except (paramiko.SSHException, OSError):
            pass


class PuertoAbierto(_ServidorHilo):
    """Acepta la conexión y la cierra enseguida: suficiente para que el escaneo lo vea abierto."""

    def manejar(self, conexion):
        conexion.close()


def iniciar(host: str = HOST_SIMULADOR, puerto_ssh: int = PUERTO_SSH_SIM) -> list:
    """Levanta el servidor SSH y los puertos TCP abiertos. Devuelve la lista para detenerlos."""
    servidores = [ServidorSSH(host, puerto_ssh)]
    servidores += [PuertoAbierto(host, p) for p in PUERTOS_TCP_ABIERTOS]
    for servidor in servidores:
        servidor.start()
    return servidores
