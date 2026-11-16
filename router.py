import socket
import sys

from parser import *

BUFFER_SIZE = 4092
TEXT_LEN = 32
sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rutas = {}

def cargar_rutas(archivo):
    for linea in tabulador(archivo):
        clave = (linea["Red"], linea["Puerto Inicial"], linea["Puerto Final"])
        if clave in rutas:
            rutas[clave].append((linea["IP Salto"], linea["Puerto Salto"]))
        else:
            rutas[clave] = [(linea["IP Salto"], linea["Puerto Salto"])]


def en_red(ip, red):
    red_ip, prefijo = red.split("/")
    offset = int(prefijo) // 8
    return ip.split(".")[:offset] == red_ip.split(".")[:offset]


def check_routes(routes_file_name, destination_address):
    if not rutas:
        cargar_rutas(routes_file_name)
    
    ip_dest, puerto_dest = destination_address

    for red in rutas:
        if red[1] <= puerto_dest <= red[2] and en_red(ip_dest, red[0]):
            salto = rutas[red].pop(0)
            rutas[red].append(salto)
            return salto
    
    return None


def tabulador(archivo):
    tabla = []

    with open(archivo, encoding="utf-8") as a:
        for linea in a:
            elementos = linea.split()
            tabla.append(
                {
                    "Red": elementos[0],
                    "Puerto Inicial": int(elementos[1]),
                    "Puerto Final": int(elementos[2]),
                    "IP Salto": elementos[3],
                    "Puerto Salto": int(elementos[4]),
                }
            )

    return tabla


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: IP, puerto y tabla de rutas")
        sys.exit()
    else:
        ip = str(sys.argv[1])
        puerto = int(sys.argv[2])
        dir = (ip, puerto)
        tabla = sys.argv[3]

    print("ip: ", ip)
    print("puerto: ", puerto)
    print("tabla: ", tabla)

    sckt.bind(dir)

    while True:
        mensaje, direccion = sckt.recvfrom(BUFFER_SIZE)
        mensaje_parseado = parse_packet(mensaje)

        print("="*TEXT_LEN)
        if mensaje_parseado["TTL"] <= 0:
            print(f"Se recibió paquete {mensaje_parseado["Mensaje"]} con TTL {mensaje_parseado["TTL"]}")
        elif mensaje_parseado["IP"] == ip and mensaje_parseado["Puerto"] == puerto:
            print(f"Se recibió un mensaje de: {direccion}")
            print(mensaje_parseado["Mensaje"].decode())
        else:
            print(f"Se recibió un mensaje de: {direccion}")
            siguiente_salto = check_routes(
                tabla, (mensaje_parseado["IP"], mensaje_parseado["Puerto"])
            )

            if siguiente_salto != None:
                print(
                    f"Redirigiendo paquete '{mensaje_parseado['Mensaje'].decode()}' con destino final ('{mensaje_parseado['IP']}', {mensaje_parseado['Puerto']}) desde ('{ip}', {puerto}) hacia {siguiente_salto}"
                )
                mensaje_parseado["TTL"] -= 1
                mensaje_reenviar = create_packet(mensaje_parseado)
                sckt.sendto(mensaje_reenviar, siguiente_salto)
            else:
                print(
                    f"No hay rutas hacia ('{mensaje_parseado['IP']}', {mensaje_parseado['Puerto']}) para el paquete '{mensaje_parseado['Mensaje'].decode()}'"
                )

        print("="*TEXT_LEN)
