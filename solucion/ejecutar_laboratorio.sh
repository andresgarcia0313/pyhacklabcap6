#!/usr/bin/env bash
# Ejecuta el laboratorio 6 completo en local y se detiene en el primer fallo:
# entorno -> pruebas -> simulador -> reconocimiento -> validación -> paquete Scapy -> limpieza.
# Todo contra 127.0.0.1. No necesita permisos de administrador.
# Uso: ./ejecutar_laboratorio.sh
set -euo pipefail
cd "$(dirname "$0")"

# El usuario del laboratorio es público; la clave llega por variable de entorno,
# nunca escrita en el código del reconocimiento. Aquí se define solo para la demostración.
export LAB06_USUARIO="laboratorio"
export LAB06_PASSWORD="laboratorio123"

# Archivos que construye el estudiante y el paso de la guía que los crea.
faltan=0
for par in config.py:1 escaneo.py:2 paquetes_scapy.py:3 ssh_cliente.py:4 reporte.py:5 recon.py:6; do
  if [[ ! -f "${par%%:*}" ]]; then
    echo "[!] Falta ${par%%:*}: se crea en el Paso ${par##*:} de la guía"
    faltan=1
  fi
done
[[ $faltan -eq 0 ]] || exit 1

PID_SIM=""
detener_simulador() {
  if [[ -n "$PID_SIM" ]] && kill -0 "$PID_SIM" 2>/dev/null; then
    kill "$PID_SIM" && wait "$PID_SIM" 2>/dev/null || true
  fi
  PID_SIM=""
}
trap detener_simulador EXIT

puerto_ssh_abierto() {
  python3 -c "import socket; socket.create_connection(('127.0.0.1', 10022), 1)" 2>/dev/null
}

iniciar_simulador() {
  for _ in $(seq 1 12); do  # espera hasta 3 s a que un simulador anterior libere el puerto
    puerto_ssh_abierto || break
    sleep 0.25
  done
  if puerto_ssh_abierto; then  # otro simulador u otro programa sigue ocupando el puerto
    echo "[!] El puerto 10022 ya está en uso. Ejecute ./limpiar.sh y vuelva a intentarlo."; exit 1
  fi
  python3 simulador_lab06.py &
  PID_SIM=$!
  for _ in $(seq 1 40); do  # espera hasta 10 s a que abra el puerto SSH simulado
    if puerto_ssh_abierto && kill -0 "$PID_SIM" 2>/dev/null; then return 0; fi
    sleep 0.25
  done
  echo "[!] El simulador no arrancó"; exit 1
}

titulo() { printf '\n========== %s ==========\n' "$1"; }

titulo "Paso 0: entorno virtual y dependencias"
[[ -d .venv ]] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python3 -m pip install -q -r requirements.txt
python3 -c "import paramiko, scapy; print('Dependencias OK: paramiko', paramiko.__version__, 'scapy', scapy.__version__)"

titulo "Pruebas automáticas (cada prueba levanta su propio objetivo simulado)"
python3 -m unittest test_escaneo_local test_ssh test_seguridad

titulo "Paso 6: simulador + reconocimiento completo"
iniciar_simulador
python3 recon.py

titulo "Validación del reporte"
python3 validar.py

titulo "Paso 3: armar un paquete con Scapy, sin enviarlo (no requiere permisos)"
python3 paquetes_scapy.py

titulo "Limpieza"
detener_simulador
pgrep -af '^python[0-9.]* (\./)?simulador_lab06\.py' || echo "Sin procesos del laboratorio activos"
echo "Reportes generados (datos sensibles, no se suben al repositorio):"
ls -1 salida/*.json
echo; echo "LABORATORIO COMPLETADO"
