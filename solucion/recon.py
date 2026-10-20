#!/usr/bin/env python3
"""
recon.py - Programa principal (Paso 6).

(La primera línea le dice a Linux con qué programa ejecutar el archivo. Para
Python es solo un comentario.)

Este archivo no mira puertos ni abre sesiones por sí mismo: ORQUESTA a los demás.
Flujo:
  1. Comprueba que el objetivo esté dentro de la red permitida   (config.py)
  2. Mira qué puertos están abiertos                             (escaneo.py)
  3. Si SSH está abierto, abre la sesión y pide datos            (ssh_cliente.py)
  4. Muestra el resumen y guarda el reporte JSON                 (reporte.py)

Uso exclusivo sobre entornos autorizados: aquí, el objetivo simulado en 127.0.0.1.
Ejecútelo con:  python3 recon.py
"""
from config import PUERTO_SSH, PUERTOS, TARGET_HOST, credenciales, verificar_red
from escaneo import ABIERTO, escanear
from reporte import generar_json, imprimir_resumen
from ssh_cliente import conectar, enumerar


def reconocer(host: str, puertos: dict, usuario: str, clave: str,
              mirar=escanear, abrir=conectar, enumerar_host=enumerar) -> tuple:
    """
    Recorre el flujo completo y devuelve (estados de puertos, datos SSH).
    Recibe mirar/abrir/enumerar_host para poder probarlo con piezas simuladas,
    sin tocar la red. verificar_red corta cualquier objetivo fuera del laboratorio.
    """
    verificar_red(host)  # control de uso responsable: ANTES de mirar nada
    estados = mirar(host, puertos)
    enumeracion = {}
    # Solo se intenta SSH si ese puerto quedó ABIERTO y hay una clave disponible.
    if estados.get(PUERTO_SSH) == ABIERTO and clave:
        cliente = abrir(host, PUERTO_SSH, usuario, clave)
        if cliente is not None:
            try:
                enumeracion = enumerar_host(cliente)
            finally:
                cliente.close()  # pase lo que pase, se cierra la sesión
    return estados, enumeracion


def main() -> int:
    """
    Ejecuta el reconocimiento y devuelve un CÓDIGO DE SALIDA que otros programas leen:
    0 = todo bien, 2 = objetivo fuera de la red permitida. Se consulta con: echo $?
    """
    print("+" + "-" * 58 + "+")
    print("|  RECONOCIMIENTO CONTROLADO - Laboratorio 6".ljust(59) + "|")
    print("|  Solo sobre sistemas con autorización escrita".ljust(59) + "|")
    print("+" + "-" * 58 + "+")
    usuario, clave = credenciales()
    try:
        verificar_red(TARGET_HOST)  # lista permitida, antes de cualquier conexión
    except PermissionError as e:
        print(f"[!] {e}")
        return 2
    if not clave:
        print("[!] Sin LAB06_PASSWORD: se miran los puertos, pero no se abre la sesión SSH.")
    estados, enumeracion = reconocer(TARGET_HOST, puertos=PUERTOS, usuario=usuario, clave=clave)
    imprimir_resumen(estados, enumeracion, TARGET_HOST)
    print("[!] El reporte lleva direcciones y datos del objetivo: trátelo como sensible.")
    print(f"[+] Reporte guardado en: {generar_json(estados, enumeracion, TARGET_HOST)}")
    return 0


# __name__ vale "__main__" solo si se ejecuta este archivo directamente.
# raise SystemExit(...) termina el programa entregando al sistema el código de main().
if __name__ == "__main__":
    raise SystemExit(main())
