#!/usr/bin/env python3
"""
simulador_lab06.py
Enciende el objetivo simulado del laboratorio 6 en 127.0.0.1: un servidor SSH que
responde con datos de ejemplo y un par de puertos TCP abiertos. Solo escucha en
loopback, así que ningún otro equipo puede alcanzarlo.

Uso:  python3 simulador_lab06.py
Se detiene con Ctrl+C.
"""
import signal
import threading

from servicios_simulados import HOST_SIMULADOR, iniciar


def main() -> None:
    servidores = iniciar()
    puertos = sorted(s.puerto for s in servidores)
    print(f"[sim] objetivo simulado en {HOST_SIMULADOR}, puertos {puertos}", flush=True)
    print("[sim] usuario del laboratorio: laboratorio (la clave la da el instructor)", flush=True)
    print("[sim] Ctrl+C para detener", flush=True)
    detener = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: detener.set())
    try:
        detener.wait()
    except KeyboardInterrupt:
        pass
    for servidor in servidores:
        servidor.detener()
    print("[sim] detenido", flush=True)


if __name__ == "__main__":
    main()
