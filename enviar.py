import random
import socket
import sys
from parser import *
from router import fragment_IP_packet

TEST = 1
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

def enviar(ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio):
    mensaje_bytes = mensaje.encode()
    paquete_plain = {
        "IP": ip_final,
        "Puerto": int(puerto_final),
        "TTL": int(ttl),
        "ID": random.randint(0, 255),  # ID ocupa 1 byte
        "Offset": 0,
        "Tamaño": len(mensaje_bytes),
        "FLAG": 0,
        "Mensaje": mensaje_bytes,
    }

    paquete_bytes = create_packet(paquete_plain)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sckt:
        sent = sckt.sendto(paquete_bytes, (ip_envio, int(puerto_envio)))
    
if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(
            "Uso: enviar.py IP_router_final puerto_router_final ttl mensaje IP_envio puerto_envio"
        )
        sys.exit()

    ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio = sys.argv[1:]
    # Si se usa test al enviar mensaje se imprimen los mensajes predefinidos en test.py fragmentados para copiar y reemplazar mas abajo, para hacer el test que se desee (enviar por partes, desordenado, etc.)
    # Por defecto se envian los mensajes en orden, primero 2 fragmentos del mensaje 1, luego el mensaje 2 completo y finalmente lo que falta del mensaje 1

    if TEST:
        enviar_test([b'\x7f\x00\x00\x01"\xb5\xff\x07\x00\x00\x00\x00\x00\n\x01hola esto ', b'\x7f\x00\x00\x01"\xb5\xff\x07\x00\n\x00\x00\x00\n\x01es un mens'], ip_envio, puerto_envio)
        enviar_test([b'\x7f\x00\x00\x01"\xb5\xff\t\x00\x00\x00\x00\x00\n\x01que pasa g', b'\x7f\x00\x00\x01"\xb5\xff\t\x00\n\x00\x00\x00\n\x01rupo esto ', b'\x7f\x00\x00\x01"\xb5\xff\t\x00\x14\x00\x00\x00\n\x01es otro me', b'\x7f\x00\x00\x01"\xb5\xff\t\x00\x1e\x00\x00\x00\n\x01nsaje larg', b'\x7f\x00\x00\x01"\xb5\xff\t\x00(\x00\x00\x00\x01\x00o'], ip_envio, puerto_envio)
        enviar_test([b'\x7f\x00\x00\x01"\xb5\xff\x07\x00\x14\x00\x00\x00\n\x01aje de lar', b'\x7f\x00\x00\x01"\xb5\xff\x07\x00\x1e\x00\x00\x00\n\x01go 50, mtu', b'\x7f\x00\x00\x01"\xb5\xff\x07\x00(\x00\x00\x00\n\x00 porte 25.'], ip_envio, puerto_envio)
    else:
        enviar(ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio)
    