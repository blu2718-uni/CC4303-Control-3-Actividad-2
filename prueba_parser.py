from parser import parse_packet, create_packet


IP_packet_v1 = {"IP": "127.0.0.1", "Puerto": 8881, "TTL": 10, "Mensaje": "hola".encode()}
parsed_IP_packet = create_packet(IP_packet_v1)
IP_packet_v2 = parse_packet(parsed_IP_packet)
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

IP_packet_v1 = b'\x7f\x00\x00\x01"\xb1\x05adios'
parsed_IP_packet = parse_packet(IP_packet_v1)
print(parsed_IP_packet)
IP_packet_v2 = create_packet(parsed_IP_packet)
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
