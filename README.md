<!-- Idioma del documento: es-CO (español de Colombia) -->
# Laboratorio 6: reconocimiento controlado con Scapy y SSH

Curso Seguridad informática con Python, capítulo 6: reconocimiento activo y automatización de sesiones.

En este laboratorio usted construye en Python una herramienta de reconocimiento que mira qué puertos TCP (Transmission Control Protocol, protocolo de control de transmisión) tiene abiertos un equipo, arma paquetes de red a mano con Scapy para entender cómo funciona por dentro, y entra por SSH (Secure Shell, consola remota cifrada) con Paramiko para pedirle datos del sistema y descargar un archivo por SFTP (SSH File Transfer Protocol). Al final genera un reporte JSON (JavaScript Object Notation, formato de texto para datos estructurados).

Todo ocurre **en su propio equipo, sin máquinas virtuales**. Un objetivo simulado incluido levanta un servidor SSH y unos puertos abiertos en `127.0.0.1`, y ningún paquete sale de su computador.

## Dos lados: la práctica y la respuesta

| Carpeta | Qué contiene | Quién la usa |
|---|---|---|
| [`paso-a-paso/`](paso-a-paso/) | **La práctica.** La guía [`paso-a-paso/README.md`](paso-a-paso/README.md) y el material de apoyo (objetivo simulado, comprobaciones por paso, validación y pruebas). Usted crea los seis archivos de la herramienta pegando el código de la guía, comentado línea a línea para quien ve Python por primera vez. | Estudiante |
| [`solucion/`](solucion/) | **La respuesta.** Los seis archivos terminados y el laboratorio completo funcionando, con sus salidas reales en [`solucion/output.md`](solucion/output.md). | Estudiante que quiera comparar, e instructor |

Recomendación: haga primero la práctica y abra la solución solo para comparar cuando algo no le funcione (`diff config.py ../solucion/config.py`).

## Empezar

```bash
git clone https://github.com/andresgarcia0313/pyhacklabcap6.git
cd pyhacklabcap6/paso-a-paso
```

Luego abra [`paso-a-paso/README.md`](paso-a-paso/README.md) y siga el Paso 0.

¿Solo quiere ver la herramienta funcionando? Desde la carpeta `pyhacklabcap6`, ejecute la solución:

```bash
cd solucion
./ejecutar_laboratorio.sh
```

## Qué va a aprender

1. Mirar qué puertos TCP están abiertos en un equipo con el módulo `socket`, sin permisos de administrador.
2. Construir paquetes de red capa por capa con `scapy` y entender qué lleva cada uno.
3. Abrir sesiones SSH con `paramiko`, ejecutar comandos de enumeración y descargar archivos por SFTP.
4. Leer las credenciales desde el entorno, nunca escritas en el código.
5. Generar un reporte JSON con los puertos abiertos y los datos obtenidos.
6. Aplicar controles de uso responsable: red permitida acotada al equipo local y manejo de datos sensibles.

No necesita saber Python: la guía y los comentarios del código lo explican desde cero. Requisitos: Python 3.10 o superior en Linux, macOS o Windows con WSL (Windows Subsystem for Linux, subsistema de Linux para Windows). El detalle está en la guía.

## Para el instructor

- `./comprobar_repositorio.sh`: verifica que el material de apoyo sea igual en ambas carpetas y que el código de la guía sea idéntico al de la solución. Además ejecuta el laboratorio completo dos veces, con la solución y con el código copiado de la guía, como lo haría un estudiante. Debe terminar en `REPOSITORIO CORRECTO`.
- `herramientas/comprobar_guia.py`: la parte de esa verificación que compara la guía con la solución y cuenta las líneas de código de cada archivo.

## Uso responsable

Use esta herramienta solo sobre sistemas con autorización escrita. No mire ni intente entrar a redes ajenas, ni a la red de su casa u oficina. La red permitida del laboratorio es únicamente la familia loopback `127.0.0.0/8`: su propio equipo. Enviar paquetes con Scapy requiere permisos de administrador (`sudo`); el laboratorio funciona completo sin ellos usando la revisión por conexión.

## Control de cambios

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-20 | Andrés García | Laboratorio 6 de reconocimiento con Scapy y SSH en ejecución local, con objetivo simulado (servidor SSH y puertos abiertos), pruebas automáticas y guía paso a paso. |
