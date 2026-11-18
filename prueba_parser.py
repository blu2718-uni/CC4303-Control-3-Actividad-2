from parser import parse_packet, create_packet


# Prueba 1: dict -> bytes -> dict
IP_packet_v1 = {
    "IP": "127.0.0.1",
    "Puerto": 8881,
    "TTL": 10,
    "ID": 7,
    "Offset": 300,
    "Tamaño": 4,
    "FLAG": 1,
    "Mensaje": "hola".encode(),
}
parsed_IP_packet = create_packet(IP_packet_v1)
IP_packet_v2 = parse_packet(parsed_IP_packet)
print(IP_packet_v2)
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

# Prueba 2: bytes -> dict -> bytes
# IP 127.0.0.1 | Puerto 8881 | TTL 5 | ID 3 | Offset 0 | Tamaño 5 (4 bytes) | FLAG 0 | "adios"
IP_packet_v1 = (
    b"\x7f\x00\x00\x01"   # IP
    b"\x22\xb1"           # Puerto (8881)
    b"\x05"               # TTL
    b"\x00\x03"           # ID
    b"\x00\x00"           # Offset
    b"\x00\x00\x00\x05"   # Tamaño
    b"\x00"               # FLAG
    b"adios"              # Mensaje
)
parsed_IP_packet = parse_packet(IP_packet_v1)
print(parsed_IP_packet)
IP_packet_v2 = create_packet(parsed_IP_packet)
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
