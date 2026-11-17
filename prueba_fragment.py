from router import fragment_IP_packet
from parser import *

IP_packet_v1 = (
    b"\x7f\x00\x00\x01"   # IP
    b"\x22\xb1"           # Puerto (8881)
    b"\x05"               # TTL
    b"\x03"               # ID
    b"\x00\x00"           # Offset
    b"\x00\x00\x00\x05"   # Tamaño
    b"\x00"               # FLAG
    b"adios"              # Mensaje
)

print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 20))))

print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 19))))

print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 18))))

print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 17))))

print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 16))))
