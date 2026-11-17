# Actividad 2 - Control 3 - Redes

> En esta actividad se usó Claude Opus 5.5 para consultas sobre firmas de funciones, funcionamiento de ciertas funciones de Python, gestión del repositorio y _testeo_ del código.

## Integrantes

- **Oscar Conejeros Bruce**
- **Julio Yáñez Tejada**

## Sobre la actividad

Se implementó un internet rudimentario, con direcciones IP, routers y _forwarding_. Luego se le agregó un _Time To Live_ (TTL) a los paquetes. No se implementó ningún mecanismo que garantice el orden de llegada de los paquetes ni que los reordene en el destino.

## Requisitos y ejecución

El proyecto se escribió en Python 3.14.6 y no requiere instalar librerías externas. Se necesita al menos Python 3.12, ya que se usan _f-strings_ con comillas dobles anidadas.

Para levantar un router (uno por terminal):

```bash
python3 router.py <IP> <puerto> <archivo_de_rutas>
# ej: python3 router.py 127.0.0.1 8881 rutas/v3/rutas_R1_v3_mtu.txt
```

Para enviar un paquete:

```bash
python3 enviar.py <IP_router_final> <puerto_router_final> <TTL> <mensaje> <IP_envio> <puerto_envio>
# ej: python3 enviar.py 127.0.0.1 8885 10 "hola" 127.0.0.1 8881
```

Para enviar `quijote.txt` línea por línea:

```bash
python3 prueba_router.py "<IP_final>;<puerto_final>;<TTL>" <IP_router_inicial> <puerto_router_inicial>
# ej: python3 prueba_router.py "127.0.0.1;8885;20" 127.0.0.1 8881
```

### Estructura del proyecto

```
.
├── router.py               # router: recibe, entrega o reenvía paquetes
├── parser.py               # parseo y armado de paquetes
├── enviar.py               # envío de un paquete a la red
├── prueba_parser.py        # prueba de ida y vuelta de parser.py
├── prueba_route_check.py   # prueba de check_routes y en_red
├── prueba_router.py        # envía quijote.txt a través de la red
├── quijote.txt             # texto usado por prueba_router.py
├── indicaciones.txt        # indicaciones de la profesora
└── rutas/                  # tablas de ruta, agrupadas por versión
    ├── v2/                 # R1 a R3, con la configuración errónea del enunciado
    ├── v3/                 # R1 a R5
    ├── v4/                 # R0 a R6
    └── v5/                 # R0 a R6 + router default (Rd)
```

### Archivos y funciones

**`parser.py`**
- `parse_packet(IP_packet) -> dict`: convierte los bytes de un paquete en un diccionario con las llaves `"IP"`, `"Puerto"`, `"TTL"` y `"Mensaje"`.
- `create_packet(parsed_IP_packet) -> bytes`: operación inversa; arma los bytes del paquete a partir del diccionario.

**`router.py`**
- `tabulador(archivo) -> list`: lee un archivo de rutas y devuelve una lista con un diccionario por línea (`"Red"`, `"Puerto Inicial"`, `"Puerto Final"`, `"IP Salto"`, `"Puerto Salto"`).
- `cargar_rutas(archivo)`: carga la tabla en el diccionario global `rutas`, agrupando los saltos que cubren el mismo rango.
- `en_red(ip, red) -> bool`: indica si `ip` pertenece a `red` (en notación CIDR).
- `check_routes(routes_file_name, destination_address) -> tuple | None`: devuelve el siguiente salto `(IP, puerto)` para llegar a `destination_address`, o `None` si no hay ruta.

**`enviar.py`**
- `enviar(ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio)`: arma un paquete con destino `(ip_final, puerto_final)` y lo envía al router `(ip_envio, puerto_envio)`. También se puede ejecutar directamente con argumentos.

## Decisiones de diseño

Se crearon dos archivos además del router: `enviar.py` y `parser.py`. El primero simplifica el envío de mensajes a través de los routers: ofrece una función que hace el envío y también se puede ejecutar directamente con argumentos. El segundo separa del router la lógica de parseo de paquetes, para poder reutilizarla en `enviar.py` y en las pruebas.

La principal diferencia con la guía _Simulando un mini-internet_ es que las distintas rutas se identifican por puertos distintos, no por direcciones distintas. 

## Supuestos e interpretaciones

- **Punto 5 del enunciado:** la tupla `(IP_router_final, puerto_router_final)` es el destino final del paquete, y es la que va en el header. La tupla `(IP_envio, puerto_envio)` es el router por el que el paquete entra a la red.
- Los prefijos de red son siempre múltiplos de 8 (`/8`, `/16`, `/24` o `/32`).
- Una tabla de rutas no contiene líneas en blanco.

## Implementación

**Formato del paquete.** Cada paquete tiene un header de 7 bytes, seguido del mensaje:

| Bytes | Campo | Codificación |
|---|---|---|
| 0–3 | IP de destino | un byte por octeto |
| 4–5 | Puerto de destino | entero _big-endian_ |
| 6 | TTL | entero (0 a 255) |
| 7 en adelante | Mensaje | texto en UTF-8 |

**Funcionamiento del router.** El router escucha en su `(IP, puerto)` mediante un socket UDP. Por cada paquete que recibe:

1. Si el TTL es 0, descarta el paquete.
2. Si el destino es el propio router, imprime el mensaje.
3. Si no, busca el siguiente salto con `check_routes`, le resta 1 al TTL, rearma el paquete y lo reenvía. Si no hay ruta, lo informa y descarta el paquete.

**Búsqueda de ruta.** Una ruta calza si el puerto de destino está dentro de su rango y la IP pertenece a su red. Para lo segundo, `en_red` compara los primeros `prefijo / 8` octetos de ambas IPs. Las rutas se revisan en el orden del archivo y se usa la primera que calce, por lo que el orden de las líneas define la prioridad.

**Round robin.** Siguiendo las indicaciones dadas en clase, el archivo de rutas no se modifica: la tabla se lee una sola vez y se guarda en memoria, en un diccionario cuyas llaves son `(red, puerto_inicial, puerto_final)` y cuyos valores son listas con los posibles saltos. La lista funciona como una cola circular: cada vez que se usa una ruta, se saca el primer salto de la lista (`pop(0)`) y se vuelve a agregar al final (`append`). Así, paquetes sucesivos hacia un mismo rango van alternando entre todos los saltos posibles. Como los diccionarios de Python conservan el orden de inserción, la prioridad sigue siendo el orden del archivo.

## Experimentación y observaciones

### Router default (parte 1, punto 8)

Al agregar un router default, el salto hacia él debe ir al final de cada tabla de ruta (excepto la del propio router default), para que solo se use cuando ninguna otra ruta calza. A su vez, la tabla del router default apunta directamente a cada uno de los demás routers.

La tabla de rutas del router default (`rutas/v5/rutas_Rd_v5.txt`) es:

```
127.0.0.1/24 8880 8880 127.0.0.1 8880
127.0.0.1/24 8881 8881 127.0.0.1 8881
127.0.0.1/24 8882 8882 127.0.0.1 8882
127.0.0.1/24 8883 8883 127.0.0.1 8883
127.0.0.1/24 8884 8884 127.0.0.1 8884
127.0.0.1/24 8885 8885 127.0.0.1 8885
127.0.0.1/24 8886 8886 127.0.0.1 8886
```

Al enviar paquetes a puertos fuera de la red (por ejemplo, el 9999), estos llegan al router default, mientras que el tráfico interno sigue usando sus rutas normales. Como la ruta default usa la red `127.0.0.1/24`, solo atrapa IPs de la forma `127.0.0.x`.

### Pruebas sin TTL

1. **Configuración errónea (tablas v2).** Al enviar un paquete de R1 a R3, R1 y R2 se lo rebotan entre ellos indefinidamente, debido al error de configuración descrito en el enunciado. En aproximadamente un segundo se registraron más de 12.000 reenvíos, sin que el paquete llegara nunca a R3.
2. **Cantidad de saltos (tablas v5).** Cada paquete hace una cantidad distinta de saltos. Enviando 10 paquetes de R1 a R5, intercalados con 10 de R5 a R1, se observaron entre 3 y 11 saltos (en promedio, 7,6 de R1 a R5 y 5,1 de R5 a R1). El mínimo de 3 saltos que permite la topología de la red solo se alcanzó en 2 de los 20 envíos. Esto se explica por la combinación del round robin con la configuración de las tablas: el round robin va cambiando el siguiente salto de cada router a lo largo del viaje del paquete, que a veces lo devuelve hacia atrás.
3. **Tablas creadas.** Se crearon varias versiones de tablas de ruta; las más recientes son las v5, que incluyen el router 0 (R0) y el router default (Rd). Con más routers la cantidad de saltos aumenta, pero el comportamiento es el mismo que con las tablas v3. Las tablas v4 son idénticas a las v5, salvo que no tienen la última línea (el salto al router default) y que en v4 no existe Rd. La tabla de Rd está en la sección anterior; el resto de las tablas v5 son:

   `rutas/v5/rutas_R0_v5.txt`
   ```
   127.0.0.1/24 8881 8881 127.0.0.1 8881
   127.0.0.1/24 8882 8886 127.0.0.1 8882
   127.0.0.1/24 0 65535 127.0.0.1 7000
   ```

   `rutas/v5/rutas_R1_v5.txt`
   ```
   127.0.0.1/24 8880 8880 127.0.0.1 8880
   127.0.0.1/24 8882 8886 127.0.0.1 8882
   127.0.0.1/24 8882 8886 127.0.0.1 8880
   127.0.0.1/24 0 65535 127.0.0.1 7000
   ```

   `rutas/v5/rutas_R2_v5.txt`
   ```
   127.0.0.1/24 8880 8881 127.0.0.1 8881
   127.0.0.1/24 8880 8881 127.0.0.1 8880
   127.0.0.1/24 8883 8886 127.0.0.1 8883
   127.0.0.1/24 8883 8886 127.0.0.1 8884
   127.0.0.1/24 8883 8886 127.0.0.1 8886
   127.0.0.1/24 0 65535 127.0.0.1 7000
   ```

   `rutas/v5/rutas_R3_v5.txt`
   ```
   127.0.0.1/24 8880 8882 127.0.0.1 8882
   127.0.0.1/24 8880 8882 127.0.0.1 8885
   127.0.0.1/24 8880 8882 127.0.0.1 8886
   127.0.0.1/24 8884 8886 127.0.0.1 8882
   127.0.0.1/24 8884 8886 127.0.0.1 8885
   127.0.0.1/24 8884 8886 127.0.0.1 8886
   127.0.0.1/24 0 65535 127.0.0.1 7000
   ```

   `rutas/v5/rutas_R4_v5.txt`
   ```
   127.0.0.1/24 8880 8883 127.0.0.1 8882
   127.0.0.1/24 8880 8883 127.0.0.1 8885
   127.0.0.1/24 8885 8886 127.0.0.1 8882
   127.0.0.1/24 8885 8886 127.0.0.1 8885
   127.0.0.1/24 0 65535 127.0.0.1 7000
   ```

   `rutas/v5/rutas_R5_v5.txt`
   ```
   127.0.0.1/24 8880 8884 127.0.0.1 8884
   127.0.0.1/24 8880 8884 127.0.0.1 8883
   127.0.0.1/24 8886 8886 127.0.0.1 8883
   127.0.0.1/24 0 65535 127.0.0.1 7000
   ```

   `rutas/v5/rutas_R6_v5.txt`
   ```
   127.0.0.1/24 8880 8882 127.0.0.1 8882
   127.0.0.1/24 8883 8885 127.0.0.1 8883
   127.0.0.1/24 0 65535 127.0.0.1 7000
   ```

### Pruebas con TTL

**Configuración errónea con TTL.** Al repetir la prueba de la configuración errónea (tablas v2) con TTL, el rebote entre R1 y R2 persiste, pero ya no es infinito. Con un TTL inicial de 10, el paquete rebotó 10 veces (5 en cada router) hasta que R1 lo recibió con TTL 0 y lo descartó. R3 nunca recibió el paquete.

**Envío de un archivo grande.** Con `prueba_router.py` se envió `quijote.txt` línea por línea (13 líneas: 7 párrafos alternados con 6 líneas vacías) usando las tablas v3, por tres rutas distintas. En todos los casos llegaron las 13 líneas completas, pero en desorden (`·` representa una línea vacía):

| Ruta | Orden de llegada |
|---|---|
| Enviado | 1 · 3 · 5 · 7 · 9 · 11 · 13 |
| R1 → R5 | 1 · 5 9 13 · · 3 · 11 7 · · |
| R5 → R1 | 1 · 5 9 13 · · 3 · · 11 · 7 |
| R4 → R1 | 1 3 5 7 9 · 11 13 · · · · · |

El desorden se debe a que el round robin envía paquetes consecutivos por caminos de distinto largo, y como los paquetes se envían sin esperar entre ellos, los que van por caminos cortos adelantan a los demás. Como el paquete no tiene número de secuencia, el destino no puede reordenarlos. Además, el orden de llegada cambia entre ejecuciones, porque depende de cómo se intercalan los paquetes en tránsito.
