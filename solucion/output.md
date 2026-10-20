<!-- Idioma del documento: es-CO (español de Colombia) -->
# Salida real del laboratorio 6: reconocimiento controlado con Scapy y SSH

Capturas hechas en el equipo de práctica con Python 3.14.8. Todo contra `127.0.0.1`,
sin permisos de administrador. Los paquetes de Scapy se arman sin enviarse.

## Versiones instaladas

```
python     3.14.8
paramiko   5.1.0
scapy      2.8.0
```

## Recorrido completo (`./ejecutar_laboratorio.sh`)

```
========== Paso 0: entorno virtual y dependencias ==========
Dependencias OK: paramiko 5.1.0 scapy 2.8.0

========== Pruebas automáticas (cada prueba levanta su propio objetivo simulado) ==========
..............
----------------------------------------------------------------------
Ran 14 tests in 0.396s

OK

========== Paso 6: simulador + reconocimiento completo ==========
[sim] objetivo simulado en 127.0.0.1, puertos [10021, 10022, 10025]

============================================================
  RECONOCIMIENTO CONTROLADO - Objetivo: 127.0.0.1
============================================================

Puerto     Estado
------------------------------
10021      ABIERTO
10022      ABIERTO
10025      ABIERTO
10080      CERRADO
13306      CERRADO

  DATOS OBTENIDOS POR SSH:
    sistema   : Linux objetivo-lab 5.15.0-91-generic #1 SMP x86_64 GNU/Linux
    usuario   : uid=1000(laboratorio) gid=1000(laboratorio) grupos=1000(labo
    version   : NAME="Ubuntu"
============================================================

[+] Reporte guardado en: salida/recon_127_0_0_1_20261020_203527_860289.json

========== Validación del reporte ==========
1. Reporte JSON
  PASS | Objetivo: obtenido='127.0.0.1' esperado='127.0.0.1'
  PASS | Puertos mirados: obtenido=5 esperado=5
2. Puertos abiertos (el simulador abre SSH y dos TCP)
  PASS | Cantidad de abiertos: obtenido=3 esperado=3
  PASS | SSH abierto: obtenido='ABIERTO' esperado='ABIERTO'
3. Enumeración por SSH
  PASS | Datos de los 3 comandos: obtenido={'sistema', 'usuario', 'version'} esperado={'sistema', 'usuario', 'version'}
  PASS | El usuario reporta laboratorio: obtenido=True esperado=True

Resultado final: TODO PASA

========== Paso 3: armar un paquete con Scapy, sin enviarlo (no requiere permisos) ==========
Paquete armado (todavía sin enviar):
    IP / TCP 127.0.0.1:40000 > 127.0.0.1:10022 S
    Bandera TCP: S  destino: puerto 10022

========== Limpieza ==========
[sim] detenido

LABORATORIO COMPLETADO
```

## Reporte JSON generado (`salida/recon_*.json`)

```json
{
  "metadata": {
    "herramienta": "Reconocimiento controlado - Laboratorio 6",
    "objetivo": "127.0.0.1",
    "momento": "2026-10-20T20:35:27Z",
    "autorizacion": "Entorno local controlado - objetivo simulado en 127.0.0.1"
  },
  "resumen": {
    "puertos_mirados": 5,
    "puertos_abiertos": 3,
    "lista_abiertos": [10021, 10022, 10025],
    "ssh_enumerado": true
  },
  "puertos": {
    "10021": "ABIERTO",
    "10022": "ABIERTO",
    "10025": "ABIERTO",
    "10080": "CERRADO",
    "13306": "CERRADO"
  },
  "enumeracion_ssh": {
    "sistema": "Linux objetivo-lab 5.15.0-91-generic #1 SMP x86_64 GNU/Linux",
    "usuario": "uid=1000(laboratorio) gid=1000(laboratorio) grupos=1000(laboratorio)",
    "version": "NAME=\"Ubuntu\"\nVERSION=\"22.04.3 LTS (Jammy Jellyfish)\""
  }
}
```

## Nota sobre el envío con Scapy

Enviar los paquetes de verdad (`syn_scan`) necesita permisos de administrador. Sin ellos,
Scapy responde `PermissionError: [Errno 1] Operation not permitted` al abrir el socket de
bajo nivel, lo cual es esperado. Por eso el recorrido automático solo arma el paquete y la
revisión de puertos se hace por conexión (Paso 2), que no requiere permisos.
```

sudo python3 paquetes_scapy.py   # envía a 127.0.0.1 y clasifica la respuesta (requiere permisos)
```
