# Actividad 2 - Control 3 - Redes

> En esta actividad se usó Claude Opus 5.5 para consultas sobre firmas de funciones, funcionamiento de ciertas funciones de Python, gestión del repositorio y _testeo_ del código.

## Integrantes

- **Oscar Conejeros Bruce**
- **Julio Yáñez Tejada**

## Sobre la actividad

Al internet rudimentario de la actividad 1 se le implementó **fragmentación**. Para ello, se le entregó un nuevo campo a los routers, el **MTU (Maximum Transmission Unit)**. Naturalmente se implementó la lógica de fragmentación de datagramas a los routers, sobre la lógica ya existente del mini-internet.

## Requisitos y ejecución

El proyecto se escribió en Python 3.14.6 y no requiere instalar librerías externas. Se necesita al menos Python 3.12, ya que se usan _f-strings_ con comillas dobles anidadas.

Para levantar un router (uno por terminal):

```bash
python3 router.py <IP> <puerto> <archivo_de_rutas>
# ej: python3 router.py 127.0.0.1 8881 rutas/v3/rutas_R1_v3_mtu.txt
```

La red de prueba tiene 5 routers, R1 a R5, en los puertos 8881 a 8885. Cada uno usa su tabla `rutas/v3/rutas_R<i>_v3_mtu.txt`.

Cada línea de una tabla de rutas tiene el formato:

```
<red> <puerto_inicial> <puerto_final> <IP_salto> <puerto_salto> <MTU>
# ej: 127.0.0.1/24 8883 8885 127.0.0.1 8883 50
```

El MTU es el tamaño máximo en bytes, header incluido, de los paquetes que se envían por ese salto.

Para enviar un paquete:

```bash
python3 enviar.py <IP_router_final> <puerto_router_final> <TTL> <mensaje> <IP_envio> <puerto_envio>
# ej: python3 enviar.py 127.0.0.1 8885 10 "hola" 127.0.0.1 8881
```

El comportamiento de `enviar.py` depende de la constante `TEST`, definida al inicio del archivo:

- **`TEST = 0`:** envía `<mensaje>` como un solo paquete, sin fragmentar. Si el mensaje no cabe en el MTU de algún salto, los routers lo fragmentan en el camino.
- **`TEST = 1`** (valor actual): envía a `(IP_envio, puerto_envio)` dos mensajes predefinidos, con IDs 7 y 9 y destino `127.0.0.1:8885`, ya fragmentados con MTU 25. Los fragmentos van intercalados: primero 2 fragmentos del mensaje 1, luego el mensaje 2 completo y al final el resto del mensaje 1. Sirve para probar el reensamblaje cuando llegan mezclados fragmentos de distintos paquetes. En este modo se ignoran el destino, el TTL y el mensaje, aunque igual hay que pasarlos como argumentos. Además, al importarse, `enviar.py` imprime los fragmentos de ambos mensajes, y eso también ocurre al correr `prueba_router.py`.

Para enviar `quijote.txt` línea por línea:

```bash
python3 prueba_router.py "<IP_final>;<puerto_final>;<TTL>" <IP_router_inicial> <puerto_router_inicial>
# ej: python3 prueba_router.py "127.0.0.1;8885;20" 127.0.0.1 8881
```

Para correr las pruebas, que no necesitan routers levantados:

```bash
python3 prueba_parser.py      # ida y vuelta de parse_packet y create_packet
python3 prueba_fragment.py    # fragmentación con distintos MTU y reensamblaje
```

### Estructura del proyecto

```
.
├── router.py               # router: recibe, reensambla, entrega, reenvía y fragmenta paquetes
├── parser.py               # parseo y armado de paquetes
├── enviar.py               # envío de un paquete a la red (con modo de prueba)
├── prueba_parser.py        # prueba de ida y vuelta de parser.py
├── prueba_fragment.py      # pruebas de fragment_IP_packet y reassemble_IP_packet
├── prueba_route_check.py   # prueba de check_routes y en_red (usa tablas v2 de la actividad 1)
├── prueba_router.py        # envía quijote.txt a través de la red
├── quijote.txt             # texto usado por prueba_router.py
└── rutas/
    └── v3/                 # R1 a R5, con el MTU de cada salto
```

### Archivos y funciones

**`parser.py`**
- `parse_packet(IP_packet) -> dict`: convierte los bytes de un paquete en un diccionario con las llaves `"IP"`, `"Puerto"`, `"TTL"`, `"ID"`, `"Offset"`, `"Tamaño"`, `"FLAG"` y `"Mensaje"`.
- `create_packet(parsed_IP_packet) -> bytes`: operación inversa; arma los bytes del paquete a partir del diccionario.

**`router.py`**
- `tabulador(archivo) -> list`: lee un archivo de rutas y devuelve una lista con un diccionario por línea (`"Red"`, `"Puerto Inicial"`, `"Puerto Final"`, `"IP Salto"`, `"Puerto Salto"`, `"MTU"`).
- `cargar_rutas(archivo)`: carga la tabla en el diccionario global `rutas`, agrupando los saltos que cubren el mismo rango. Cada salto se guarda como `(IP, puerto, MTU)`.
- `en_red(ip, red) -> bool`: indica si `ip` pertenece a `red` (en notación CIDR).
- `check_routes(routes_file_name, destination_address) -> tuple | None`: devuelve el siguiente salto `(IP, puerto, MTU)` para llegar a `destination_address`, o `None` si no hay ruta.
- `fragment_IP_packet(IP_packet, MTU) -> list`: si el paquete cabe en el MTU, devuelve una lista con el paquete tal cual. Si no cabe, divide el mensaje en trozos de a lo más `MTU - 15` bytes y devuelve un fragmento (en bytes) por trozo. Cada fragmento conserva la IP, el puerto, el TTL y el ID del original. Su offset es el del original más la posición del trozo, y su FLAG es 1, salvo en el último, que conserva el FLAG del original.
- `reassemble_IP_packet(fragment_list) -> bytes | None`: une los fragmentos de un mismo paquete siguiendo los offsets desde 0 hasta llegar al fragmento con FLAG 0, sin importar el orden en que vengan en la lista. Devuelve `None` si todavía falta algún fragmento.

**`enviar.py`**
- `enviar(ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio)`: arma un paquete con destino `(ip_final, puerto_final)` y lo envía al router `(ip_envio, puerto_envio)`. El ID se elige al azar entre 0 y 255, el offset y el FLAG van en 0, y el tamaño es el largo del mensaje en bytes.
- `enviar_test(list, ip_envio, puerto_envio)`: envía, en orden, una lista de paquetes ya armados (en bytes) al router `(ip_envio, puerto_envio)`.

## Decisiones de diseño

Se tomaron las siguientes descisiones en cuanto al header de los paquetes: **FLAG** ocupa un byte; El **offset** se guarda en 2 bytes; La **ID** de un paquete toma un solo byte.

En cuanto al MTU, este es leido por `cargar_rutas` y es almacenado directamente dentro de la clave en el diccionario `rutas`.

## Implementación

**Formato del paquete.** Cada paquete tiene un header de 15 bytes, seguido del mensaje:

| Bytes | Campo | Codificación |
|---|---|---|
| 0–3 | IP de destino | un byte por octeto |
| 4–5 | Puerto de destino | entero _big-endian_ |
| 6 | TTL | entero (0 a 255) |
| 7 | ID | entero (0 a 255) |
| 8–9 | Offset | entero _big-endian_ |
| 10–13 | Tamaño | entero _big-endian_ |
| 14 | FLAG | entero (0 o 1) |
| 15 en adelante | Mensaje | texto en UTF-8 |

Los campos nuevos respecto a la actividad 1 son los que permiten fragmentar y reensamblar:

- **ID:** identifica el paquete original. Todos sus fragmentos llevan el mismo ID, y así el destino sabe cuáles debe juntar. `enviar.py` lo elige al azar.
- **Offset:** posición, en bytes, en que comienza el mensaje del fragmento dentro del mensaje original. Un paquete sin fragmentar tiene offset 0.
- **Tamaño:** largo en bytes del mensaje que lleva este paquete o fragmento, sin contar el header.
- **FLAG:** vale 1 si después de este fragmento vienen más, y 0 si es el último o si el paquete no está fragmentado.

Como el header ocupa 15 bytes, por un salto con MTU `m` cada fragmento puede llevar a lo más `m - 15` bytes de mensaje. El texto se corta por bytes, así que un carácter de varios bytes en UTF-8 (por ejemplo, una tilde) puede quedar dividido entre dos fragmentos. Por eso solo el mensaje reensamblado se puede decodificar con seguridad.

**Funcionamiento del router.** El router escucha en su `(IP, puerto)` mediante un socket UDP. Por cada paquete que recibe:

1. Si el TTL es 0, descarta el paquete.
2. Si el destino es el propio router, intenta reensamblar el mensaje. Si se logra reensamblar, imprime el mensaje. Si no lo logra reensamblar, se queda esperando a que llegen las piezas faltantes.
3. Si no, busca el siguiente salto con `check_routes`, le resta 1 al TTL, rearma el paquete, lo fragmenta según el MTU del salto y lo reenvía. Si no hay ruta, lo informa y descarta el paquete.

## Experimentación y observaciones


