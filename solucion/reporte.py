"""
reporte.py - Reporte del reconocimiento (Paso 5).

Produce dos salidas a partir de los datos recogidos:
  1. Un archivo JSON (JavaScript Object Notation): texto estructurado que otras
     herramientas pueden leer y que sirve de evidencia para un informe.
  2. Un resumen en consola, para leer el resultado de un vistazo.

El reporte se guarda en una carpeta RELATIVA (salida/), dentro de donde se trabaja,
nunca en una ruta fija del sistema. Contiene direcciones y datos del objetivo:
trátelo como información sensible y no lo comparta fuera del curso.
"""
import json  # incluido en Python: leer y escribir JSON
import os     # incluido en Python: carpetas y rutas de archivos
from datetime import datetime, timezone  # incluido en Python: fechas y horas

from config import DIRECTORIO_SALIDA


def generar_json(puertos: dict, enumeracion: dict, host: str,
                 directorio: str = DIRECTORIO_SALIDA) -> str:
    """Guarda el resultado en un archivo JSON y devuelve la ruta creada."""
    os.makedirs(directorio, exist_ok=True)  # crea la carpeta; si ya existe, no pasa nada
    ahora = datetime.now(timezone.utc)
    # Nombre con fecha y hora hasta el microsegundo: dos reconocimientos nunca se pisan.
    nombre = f"recon_{host.replace('.', '_')}_{ahora:%Y%m%d_%H%M%S_%f}.json"
    ruta = os.path.join(directorio, nombre)  # une carpeta y nombre: salida/recon_...
    # abiertos: lista de los puertos cuyo estado es "ABIERTO".
    abiertos = [p for p, estado in puertos.items() if estado == "ABIERTO"]
    reporte = {
        "metadata": {
            "herramienta": "Reconocimiento controlado - Laboratorio 6",
            "objetivo": host,
            "momento": ahora.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "autorizacion": "Entorno local controlado - objetivo simulado en 127.0.0.1",
        },
        "resumen": {
            "puertos_mirados": len(puertos),
            "puertos_abiertos": len(abiertos),
            "lista_abiertos": abiertos,
            "ssh_enumerado": bool(enumeracion),  # True si hubo sesión SSH con datos
        },
        "puertos": puertos,
        "enumeracion_ssh": enumeracion,
    }
    with open(ruta, "w", encoding="utf-8") as f:
        # indent=2 lo deja legible; ensure_ascii=False conserva las tildes.
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    return ruta


def imprimir_resumen(puertos: dict, enumeracion: dict, host: str) -> None:
    """Muestra en consola la tabla de puertos y la enumeración SSH."""
    print("\n" + "=" * 60)
    print(f"  RECONOCIMIENTO CONTROLADO - Objetivo: {host}")
    print("=" * 60)
    print(f"\n{'Puerto':<10} {'Estado'}")
    print("-" * 30)
    for puerto, estado in puertos.items():
        print(f"{puerto:<10} {estado}")
    if enumeracion:
        print("\n  DATOS OBTENIDOS POR SSH:")
        for nombre, valor in enumeracion.items():
            # Una sola línea por dato, recortada para que quepa con holgura.
            print(f"    {nombre:<10}: {valor.splitlines()[0][:60]}")
    else:
        print("\n  Sin sesión SSH: ningún dato enumerado.")
    print("=" * 60 + "\n")
