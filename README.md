# [Actividad 2 - Control 3 - Redes](https://github.com/blu2718-uni/CC4303-Control-3-Actividad-2)

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
python3 enviar.py <IP_router_final> <puerto_router_final> <TTL> <mensaje> <IP_envio> <puerto_envio> [ID]
# ej: python3 enviar.py 127.0.0.1 8885 10 "hola!" 127.0.0.1 8881 347
```

El `ID` es opcional: si no se entrega, se elige al azar entre 0 y 65535.

El comportamiento de `enviar.py` depende de la constante `TEST`, definida al inicio del archivo:

- **`TEST = 0`** (valor actual): envía `<mensaje>` como un solo paquete, sin fragmentar. Si el mensaje no cabe en el MTU de algún salto, los routers lo fragmentan en el camino.
- **`TEST = 1`:** envía a `(IP_envio, puerto_envio)` dos mensajes predefinidos, con IDs 7 y 9 y destino `127.0.0.1:8885`, ya fragmentados con MTU 25. Los fragmentos van intercalados: primero 2 fragmentos del mensaje 1, luego el mensaje 2 completo y al final el resto del mensaje 1. Sirve para probar el reensamblaje cuando llegan mezclados fragmentos de distintos paquetes. En este modo se ignoran el destino, el TTL, el mensaje y el ID, aunque igual hay que pasar los 6 primeros argumentos. Además, al importarse, `enviar.py` imprime los fragmentos de ambos mensajes, y eso también ocurre al correr `prueba_router.py`.

Para enviar `quijote.txt` línea por línea:

```bash
python3 prueba_router.py "<IP_final>;<puerto_final>;<TTL>" <IP_router_inicial> <puerto_router_inicial>
# ej: python3 prueba_router.py "127.0.0.1;8885;20" 127.0.0.1 8881
```

Para correr las pruebas, que no necesitan routers levantados:

```bash
python3 prueba_parser.py      # ida y vuelta de parse_packet y create_packet
python3 prueba_fragment.py    # fragmentación con distintos MTU y reensamblaje
python3 prueba_route_check.py # búsqueda de rutas, round robin y en_red
```

### Estructura del proyecto

```
.
├── router.py               # router: recibe, reensambla, entrega, reenvía y fragmenta paquetes
├── parser.py               # parseo y armado de paquetes
├── enviar.py               # envío de un paquete a la red (con modo de prueba)
├── prueba_parser.py        # prueba de ida y vuelta de parser.py
├── prueba_fragment.py      # pruebas de fragment_IP_packet y reassemble_IP_packet
├── prueba_route_check.py   # prueba de check_routes y en_red
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
- `fragment_IP_packet(IP_packet, MTU) -> list`: si el paquete cabe en el MTU, devuelve una lista con el paquete tal cual. Si no cabe, divide el mensaje en trozos de a lo más `MTU - 16` bytes y devuelve un fragmento (en bytes) por trozo. Cada fragmento conserva la IP, el puerto, el TTL y el ID del original. Su offset es el del original más la posición del trozo, y su FLAG es 1, salvo en el último, que conserva el FLAG del original.
- `reassemble_IP_packet(fragment_list) -> bytes | None`: une los fragmentos de un mismo paquete siguiendo los offsets desde 0 hasta llegar al fragmento con FLAG 0, sin importar el orden en que vengan en la lista. Devuelve `None` si todavía falta algún fragmento.

**`enviar.py`**
- `enviar(ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio, id_paquete=None)`: arma un paquete con destino `(ip_final, puerto_final)` y lo envía al router `(ip_envio, puerto_envio)`. Si no se entrega `id_paquete`, el ID se elige al azar entre 0 y 65535; el offset y el FLAG van en 0, y el tamaño es el largo del mensaje en bytes.
- `enviar_test(list, ip_envio, puerto_envio)`: envía, en orden, una lista de paquetes ya armados (en bytes) al router `(ip_envio, puerto_envio)`.

## Decisiones de diseño

Se tomaron las siguientes descisiones en cuanto al header de los paquetes: **FLAG** ocupa un byte; El **offset** se guarda en 2 bytes; La **ID** de un paquete se guarda en 2 bytes, ya que el enunciado usa IDs mayores a 255 en las pruebas (por ejemplo, 347).

En cuanto al MTU, este es leido por `cargar_rutas` y es almacenado directamente dentro de la clave en el diccionario `rutas`.

## Implementación

**Formato del paquete.** Cada paquete tiene un header de 16 bytes, seguido del mensaje:

| Bytes | Campo | Codificación |
|---|---|---|
| 0–3 | IP de destino | un byte por octeto |
| 4–5 | Puerto de destino | entero _big-endian_ |
| 6 | TTL | entero (0 a 255) |
| 7–8 | ID | entero _big-endian_ (0 a 65535) |
| 9–10 | Offset | entero _big-endian_ |
| 11–14 | Tamaño | entero _big-endian_ |
| 15 | FLAG | entero (0 o 1) |
| 16 en adelante | Mensaje | texto en UTF-8 |

Los campos nuevos respecto a la actividad 1 son los que permiten fragmentar y reensamblar:

- **ID:** identifica el paquete original. Todos sus fragmentos llevan el mismo ID, y así el destino sabe cuáles debe juntar. `enviar.py` lo elige al azar.
- **Offset:** posición, en bytes, en que comienza el mensaje del fragmento dentro del mensaje original. Un paquete sin fragmentar tiene offset 0.
- **Tamaño:** largo en bytes del mensaje que lleva este paquete o fragmento, sin contar el header.
- **FLAG:** vale 1 si después de este fragmento vienen más, y 0 si es el último o si el paquete no está fragmentado.

Como el header ocupa 16 bytes (constante `HEADER_SIZE` de `parser.py`), por un salto con MTU `m` cada fragmento puede llevar a lo más `m - 16` bytes de mensaje. El texto se corta por bytes, así que un carácter de varios bytes en UTF-8 (por ejemplo, una tilde) puede quedar dividido entre dos fragmentos. Por eso solo el mensaje reensamblado se puede decodificar con seguridad.

**Funcionamiento del router.** El router escucha en su `(IP, puerto)` mediante un socket UDP. Por cada paquete que recibe:

1. Si el TTL es 0, descarta el paquete.
2. Si el destino es el propio router, intenta reensamblar el mensaje. Si se logra reensamblar, imprime el mensaje. Si no lo logra reensamblar, se queda esperando a que llegen las piezas faltantes.
3. Si no, busca el siguiente salto con `check_routes`, le resta 1 al TTL, rearma el paquete, lo fragmenta según el MTU del salto y lo reenvía. Si no hay ruta, lo informa y descarta el paquete.

## Experimentación y observaciones

Todas las pruebas usan la red de 5 routers con las tablas `rutas/v3/` (R1 a R5 en los puertos 8881 a 8885). Los MTU de cada enlace son los mismos en ambos sentidos:

| Enlace | MTU | Bytes de mensaje por fragmento |
|---|---|---|
| R1 – R2 | 100 | 84 |
| R2 – R3 | 50 | 34 |
| R2 – R4 | 80 | 64 |
| R3 – R5 | 55 | 39 |
| R4 – R5 | 140 | 124 |

Los paquetes se armaron con `create_packet`, se guardaron en un archivo y se enviaron con netcat al router de entrada. Por ejemplo, para el paquete `hola!` desde R1 a R5:

```bash
python3 -c 'from parser import create_packet; import sys; sys.stdout.buffer.write(create_packet({"IP": "127.0.0.1", "Puerto": 8885, "TTL": 10, "ID": 347, "Offset": 0, "Tamaño": 5, "FLAG": 0, "Mensaje": b"hola!"}))' > hola.bin
nc -u -q1 127.0.0.1 8881 < hola.bin
```

Para seguir cada paquete salto a salto, los routers se ejecutaron registrando cada `recvfrom` y `sendto` de su socket, con el TTL, ID, offset, tamaño y FLAG de cada paquete y fragmento. `router.py` no se modificó para esto. Cada envío se hizo después de que terminara el anterior.

### Prueba 1: TTL y round robin, sin fragmentación

Se envió 8 veces, desde R1 a R5, el paquete del enunciado: IP `127.0.0.1`, puerto 8885, TTL 10, ID 347, offset 0, tamaño 5, FLAG 0 y mensaje `hola!`. El paquete mide 21 bytes, menos que el MTU más chico de la red (50), así que nunca se fragmenta.

Los 8 paquetes llegaron a R5, alternando entre dos caminos:

| Envíos | Camino | Saltos | Llega con TTL |
|---|---|---|---|
| 1, 3, 5, 7 | R1 → R2 → R3 → R2 → R4 → R2 → R3 → R5 | 7 | 3 |
| 2, 4, 6, 8 | R1 → R2 → R4 → R5 | 3 | 7 |

Con esto, queda claro que round robin funciona.

### Prueba 2: paquete de 150 bytes desde R1 a R5

El paquete tiene 16 bytes de header y 134 de mensaje (texto ASCII). Se envió 6 veces desde R1 a R5, siempre el mismo archivo y por lo tanto con el mismo ID (500), con TTL 10.

Como el enlace R1 – R2 tiene MTU 100, R1 siempre lo divide en 2 fragmentos: bytes 0–83 (100 bytes en total) y 84–133 (66 bytes). Desde ahí, R2 los vuelve a fragmentar según el salto que le toque a cada uno:

- **Hacia R3 (MTU 50):** el fragmento 0–83 se divide en 0–33, 34–67 y 68–83, y el 84–133 en 84–117 y 118–133.
- **Hacia R4 (MTU 80):** el fragmento 0–83 se divide en 0–63 y 64–83, y el 84–133 (66 bytes) pasa sin cambios.

Los enlaces R4 – R5 y R3 – R5 tienen MTU más grande que estos fragmentos, así que no los vuelven a dividir. Los fragmentos tampoco se juntan en el camino: solo el destino reensambla.

Este es el recorrido de cada fragmento en el envío 4:

| Bytes del mensaje | Camino | Llega con TTL | Orden de llegada |
|---|---|---|---|
| 0–63 | R1 → R2 → R4 → R5 | 7 | 1.º |
| 64–83 | R1 → R2 → R4 → R2 → R4 → R5 | 5 | 3.º |
| 84–117 | R1 → R2 → R3 → R2 → R3 → R2 → R4 → R2 → R3 → R5 | 1 | 4.º |
| 118–133 | R1 → R2 → R3 → R5 | 7 | 2.º |

Cada fragmento se enruta por separado con round robin, así que los fragmentos de un mismo paquete toman caminos distintos y llegan desordenados. R5 igual reconstruye el mensaje, porque `reassemble_IP_packet` los junta según su offset y no según su orden de llegada.

R5 reensambló el mensaje completo en 5 de los 6 envíos. En el envío 1, el fragmento 84–117 rebotó entre R2, R3 y R4 hasta llegar a R4 con TTL 0, y se perdió. Basta con que se pierda un fragmento para que el paquete completo no se pueda reensamblar.

Esa pérdida además tuvo un efecto lateral, porque los 6 envíos usan el mismo ID. Los fragmentos del envío 1 que sí llegaron quedaron guardados en R5, a la espera del que faltaba. En el envío 2, R5 completó el mensaje usando el fragmento 34–67 que había quedado del envío 1, antes de que llegara el del envío 2. Ese fragmento sobrante pasó a su vez al envío siguiente, y así sucesivamente. Aquí no se nota, porque los 6 envíos llevan el mismo mensaje, pero dos paquetes distintos con el mismo ID mezclarían sus fragmentos. Por eso cada paquete necesita un ID propio, y `enviar.py` lo elige al azar cuando no se le entrega uno.

Al repetir los 6 envíos con TTL 20 y un ID distinto en cada uno, los 6 llegaron completos. El fragmento que más tardó llegó con TTL 7.

### Prueba 3: envío desde otros routers

Se envió el mismo paquete de 150 bytes entre otros pares de routers, 2 veces con TTL 10 y luego con TTL 20, con un ID distinto en cada envío:

| Origen → destino | Completos con TTL 10 | Completos con TTL 20 | Fragmentos que llegan al destino |
|---|---|---|---|
| R1 → R5 | 5 de 6 | 6 de 6 | 4 a 5 |
| R5 → R1 | 2 de 2 | 1 de 1 | 3 |
| R4 → R1 | 0 de 2 | 2 de 2 | 3 a 8 |
| R3 → R1 | 1 de 2 | 2 de 2 | 4 a 6 |
| R2 → R5 | 1 de 2 | 2 de 2 | 4 |
| R1 → R3 | 2 de 2 | 2 de 2 | 5 |

Lo que cambia según el origen es cómo se fragmenta el paquete: El primer enlace define la primera fragmentación; Los fragmentos pueden volver a fragmentarse o fragmentarse menos, justamente por los distintos enlaces que puede recorrer el paquete; A mas fragmentación, más probable es que alguno se pierda al acabarse tu TTL.
