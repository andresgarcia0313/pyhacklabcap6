<!-- Idioma del documento: es-CO (español de Colombia) -->
# Solución del laboratorio 6

Los seis archivos terminados de la herramienta de reconocimiento, más el material de apoyo (idéntico al de `paso-a-paso/`).

## Ejecutar todo

```bash
./ejecutar_laboratorio.sh
```

Hace el recorrido completo contra `127.0.0.1`, sin permisos de administrador: prepara el entorno, corre las 14 pruebas, enciende el objetivo simulado, reconoce, valida el reporte, arma un paquete con Scapy y limpia. Debe terminar en `LABORATORIO COMPLETADO`. Las salidas reales están en [`output.md`](output.md).

## Los seis archivos

| Archivo | Qué hace |
|---|---|
| `config.py` | Objetivo, red permitida, puertos y credenciales desde el entorno. |
| `escaneo.py` | Mira qué puertos están abiertos por conexión TCP (sin permisos de administrador). |
| `paquetes_scapy.py` | Arma y clasifica paquetes con Scapy; el envío real requiere `sudo`. |
| `ssh_cliente.py` | Abre la sesión SSH con Paramiko, enumera y descarga por SFTP. |
| `reporte.py` | Resume en consola y guarda un reporte JSON en `salida/`. |
| `recon.py` | Orquesta todo: red permitida, puertos, sesión SSH y reporte. |

## Correr una parte suelta

```bash
# en una terminal: encender el objetivo
python3 simulador_lab06.py

# en otra: mirar puertos, o el reconocimiento completo
python3 escaneo.py
LAB06_PASSWORD='laboratorio123' python3 recon.py
python3 validar.py
```
