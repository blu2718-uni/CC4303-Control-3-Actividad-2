from parser import *
from enviar import *
import sys

if len(sys.argv) != 4:
    print("Uso: python3 prueba_router.py headers IP_router_inicial puerto_router_inicial")
    sys.exit()

headers, IP_router_inicial, puerto_router_inicial = sys.argv[1:]
headers_lista = headers.split(";")

with open("quijote.txt", encoding="utf-8") as quijote:
    for linea in quijote:
        enviar(headers_lista[0], int(headers_lista[1]), int(headers_lista[2]), linea, IP_router_inicial, int(puerto_router_inicial))
