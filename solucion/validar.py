#!/usr/bin/env python3
"""
validar.py
Comprobaciones finales que SÍ pueden fallar, sobre el último reporte generado:
  1. el reporte JSON existe, es válido y tiene los conteos esperados;
  2. el escaneo encontró abiertos los tres puertos que el simulador abre;
  3. la sesión SSH trajo datos de los tres comandos de enumeración.
Uso: python3 validar.py   (después de ejecutar recon.py)
Sale con código 0 si todo pasa y 1 si algo falla.
"""
import glob
import json
import os
import sys

from config import PUERTO_SSH, TARGET_HOST
from ssh_cliente import COMANDOS

fallos = []


def comprobar(nombre: str, obtenido, esperado) -> None:
    ok = obtenido == esperado
    print(f"  {'PASS' if ok else 'FAIL'} | {nombre}: obtenido={obtenido!r} esperado={esperado!r}")
    if not ok:
        fallos.append(nombre)


def ultimo_reporte() -> dict:
    archivos = glob.glob("salida/recon_*.json")
    if not archivos:
        sys.exit("FAIL | No hay reportes en salida/. Ejecute primero: python3 recon.py")
    ultimo = max(archivos, key=os.path.getmtime)
    with open(ultimo, encoding="utf-8") as f:
        reporte = json.load(f)  # si el JSON no es válido, aquí se detiene con el error
    print(f"  JSON válido: {ultimo}")
    return reporte


def validar(reporte: dict) -> None:
    print("\n1. Reporte JSON")
    comprobar("Objetivo", reporte["metadata"]["objetivo"], TARGET_HOST)
    comprobar("Puertos mirados", reporte["resumen"]["puertos_mirados"], 5)

    print("\n2. Puertos abiertos (el simulador abre SSH y dos TCP)")
    comprobar("Cantidad de abiertos", reporte["resumen"]["puertos_abiertos"], 3)
    comprobar("SSH abierto", str(PUERTO_SSH) in reporte["puertos"]
              and reporte["puertos"][str(PUERTO_SSH)], "ABIERTO")

    print("\n3. Enumeración por SSH")
    enumeracion = reporte["enumeracion_ssh"]
    comprobar("Datos de los 3 comandos", set(enumeracion), set(COMANDOS))
    comprobar("El usuario reporta laboratorio", "laboratorio" in enumeracion.get("usuario", ""), True)


if __name__ == "__main__":
    reporte = ultimo_reporte()
    validar(reporte)
    print(f"\nResultado final: {'TODO PASA' if not fallos else f'{len(fallos)} FALLO(S): {fallos}'}")
    sys.exit(1 if fallos else 0)
