from router import fragment_IP_packet, reassemble_IP_packet
from parser import *

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
print("Tests de fragment_IP_packet\n")
print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 21))))
print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 20))))
print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 19))))
print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 18))))
print(list(map(parse_packet, fragment_IP_packet(IP_packet_v1, 17))))
print()

print("Tests de reassemble_IP_packet\n")
IP_packet_v2 = reassemble_IP_packet(fragment_IP_packet(IP_packet_v1, 21))
print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
IP_packet_v2 = reassemble_IP_packet(fragment_IP_packet(IP_packet_v1, 20))
print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
IP_packet_v2 = reassemble_IP_packet(fragment_IP_packet(IP_packet_v1, 19))
print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
IP_packet_v2 = reassemble_IP_packet(fragment_IP_packet(IP_packet_v1, 18))
print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
IP_packet_v2 = reassemble_IP_packet(fragment_IP_packet(IP_packet_v1, 17))
print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))