import random
import socket
import sys
from parser import *
from router import fragment_IP_packet

TEST = 0
def enviar_test(list, ip_envio, puerto_envio):

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sckt:
        for i in list:
            sent = sckt.sendto(i, (ip_envio, int(puerto_envio)))

message_1 = {
    "IP": "127.0.0.1",
    "Puerto": 8885,
    "TTL": 255,
    "ID": 7,
    "Offset": 0,
    "Tamaño": 50,
    "FLAG": 0,
    "Mensaje": b'hola esto es un mensaje de largo 50, mtu porte 25.'
}
message_1 = create_packet(message_1)

if TEST:
    print(fragment_IP_packet(message_1, 25))

message_2 = {
    "IP": "127.0.0.1",
    "Puerto": 8885,
    "TTL": 255,
    "ID": 9,
    "Offset": 0,
    "Tamaño": 41,
    "FLAG": 0,
    "Mensaje": b'que pasa grupo esto es otro mensaje largo'
}

message_2 = create_packet(message_2)

if TEST:
    print(fragment_IP_packet(message_2, 25))

def enviar(ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio, id_paquete=None):
    mensaje_bytes = mensaje.encode()
    if id_paquete is None:
        id_paquete = random.randint(0, 65535)  # ID ocupa 2 bytes
    paquete_plain = {
        "IP": ip_final,
        "Puerto": int(puerto_final),
        "TTL": int(ttl),
        "ID": int(id_paquete),
        "Offset": 0,
        "Tamaño": len(mensaje_bytes),
        "FLAG": 0,
        "Mensaje": mensaje_bytes,
    }

    paquete_bytes = create_packet(paquete_plain)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sckt:
        sent = sckt.sendto(paquete_bytes, (ip_envio, int(puerto_envio)))
    
if __name__ == "__main__":
    if len(sys.argv) not in (7, 8):
        print(
            "Uso: enviar.py IP_router_final puerto_router_final ttl mensaje IP_envio puerto_envio [ID]"
        )
        sys.exit()

    ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio = sys.argv[1:7]
    id_paquete = sys.argv[7] if len(sys.argv) == 8 else None  # si no se entrega, se elige al azar
    # Si se usa test se envian los mensajes predefinidos (message_1 y message_2) fragmentados con MTU 25. Para hacer otro test (enviar por partes, desordenado, etc.) basta con cambiar las listas de fragmentos que se pasan a enviar_test
    # Por defecto se envian primero 2 fragmentos del mensaje 1, luego el mensaje 2 completo y finalmente lo que falta del mensaje 1

    if TEST:
        fragmentos_1 = fragment_IP_packet(message_1, 25)
        fragmentos_2 = fragment_IP_packet(message_2, 25)
        enviar_test(fragmentos_1[:2], ip_envio, puerto_envio)
        enviar_test(fragmentos_2, ip_envio, puerto_envio)
        enviar_test(fragmentos_1[2:], ip_envio, puerto_envio)
    else:
        enviar(ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio, id_paquete)
    