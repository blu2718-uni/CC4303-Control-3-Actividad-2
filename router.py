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
            rutas[clave].append((linea["IP Salto"], linea["Puerto Salto"], int(linea["MTU"])))
        else:
            rutas[clave] = [(linea["IP Salto"], linea["Puerto Salto"], int(linea["MTU"]))]


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
                    "MTU": int(elementos[5])
                }
            )

    return tabla

def fragment_IP_packet(IP_packet, MTU):
    fragmentos = []
    
    if len(IP_packet) <= MTU:
        fragmentos = [IP_packet]
        return fragmentos
        
    parseado = parse_packet(IP_packet)
    trozos = parseado["Tamaño"] // (MTU - HEADER_SIZE)
    
    if parseado["Tamaño"] % (MTU - HEADER_SIZE) != 0:
        trozos += 1
    
    ultimo = False
    for i in range(trozos):
        inicio = i * (MTU - HEADER_SIZE)
        ultimo = True if i == trozos - 1 else False
        
        fragmento = {
                "IP": parseado["IP"],
                "Puerto": parseado["Puerto"],
                "TTL": parseado["TTL"],
                "ID": parseado["ID"],
                "Offset": parseado["Offset"] + inicio,
                "Tamaño": len(parseado["Mensaje"][inicio:inicio + (MTU - HEADER_SIZE)]),
                "FLAG": 1 if not ultimo else parseado["FLAG"],
                "Mensaje": parseado["Mensaje"][inicio:inicio + (MTU - HEADER_SIZE)]
        }
        
        fragmentos.append(create_packet(fragmento))
    
    return fragmentos

def reassemble_IP_packet(fragment_list):
    if len(fragment_list) == 1:
        parsed_fragment = parse_packet(fragment_list[0])
        fragment_flag = parsed_fragment["FLAG"]
        fragment_offset = parsed_fragment["Offset"]
        if fragment_offset == fragment_flag == 0:
            return fragment_list[0]
        else:
            return None

    final_message = b''
    found = True
    cont = True
    i = 0
    while found and cont:
        found = False
        for frag in fragment_list:
            parsed_fragment = parse_packet(frag)
            if parsed_fragment["Offset"] == i:
                found = True
                i += parsed_fragment["Tamaño"]
                final_message += parsed_fragment["Mensaje"]
                if not parsed_fragment["FLAG"]:
                    cont = False
                break
        if not found:
            return None

    first_parsed = parse_packet(fragment_list[0])
    packet = {
        "IP": first_parsed["IP"],
        "Puerto": first_parsed["Puerto"],
        "TTL": first_parsed["TTL"],
        "ID": first_parsed["ID"],
        "Offset": 0,
        "Tamaño": len(final_message),
        "FLAG": 0,
        "Mensaje": final_message,
    }
    return create_packet(packet)

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

    d = {}

    while True:
        mensaje, direccion = sckt.recvfrom(BUFFER_SIZE)
        mensaje_parseado = parse_packet(mensaje)

        print("="*TEXT_LEN)
        if mensaje_parseado["TTL"] <= 0:
            print(f"Se recibió paquete {mensaje_parseado["Mensaje"]} con TTL {mensaje_parseado["TTL"]}")
        elif mensaje_parseado["IP"] == ip and mensaje_parseado["Puerto"] == puerto:
            print(f"Se recibió un mensaje de: {direccion}")
            print(mensaje_parseado["Mensaje"].decode())
            if f"{mensaje_parseado["ID"]}" in d:
                d[f"{mensaje_parseado["ID"]}"].append(mensaje)
            else:
                d[f"{mensaje_parseado["ID"]}"] = [mensaje]
            full_packet = reassemble_IP_packet(d[f"{mensaje_parseado["ID"]}"])
            if full_packet is not None:
                print(f"Se recibió el mensaje completo: {parse_packet(full_packet)["Mensaje"].decode()}")
                del d[f"{mensaje_parseado["ID"]}"]
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
                mensaje_reenviar = fragment_IP_packet(create_packet(mensaje_parseado), siguiente_salto[2])
                for frag in mensaje_reenviar:
                    sckt.sendto(frag, siguiente_salto[:2])
            else:
                print(
                    f"No hay rutas hacia ('{mensaje_parseado['IP']}', {mensaje_parseado['Puerto']}) para el paquete '{mensaje_parseado['Mensaje'].decode()}'"
                )

        print("="*TEXT_LEN)
