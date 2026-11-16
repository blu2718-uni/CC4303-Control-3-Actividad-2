import random
import socket
import sys
from parser import *

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
    
    enviar(ip_final, puerto_final, ttl, mensaje, ip_envio, puerto_envio)
