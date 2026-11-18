HEADER_SIZE = 16  # bytes


def parse_packet(IP_packet):
    ip_codificada = IP_packet[:4]
    ip_decodificada = ""

    for i in range(4):
        octeto = ip_codificada[i]
        ip_decodificada += str(octeto)
        if i < 3:
            ip_decodificada += "."

    paquete = {
        "IP": ip_decodificada,
        "Puerto": int.from_bytes(IP_packet[4:6], "big"),
        "TTL": IP_packet[6],
        "ID": int.from_bytes(IP_packet[7:9], "big"),
        "Offset": int.from_bytes(IP_packet[9:11], "big"),
        "Tamaño": int.from_bytes(IP_packet[11:15], "big"),
        "FLAG": IP_packet[15],
        "Mensaje": IP_packet[HEADER_SIZE:]
    }

    return paquete


def create_packet(parsed_IP_packet):
    l_ip = parsed_IP_packet["IP"].split(".")
    ip = b""

    for i in l_ip:
        ip += int.to_bytes(int(i), 1)

    puerto = int.to_bytes(parsed_IP_packet["Puerto"], 2)
    ttl = int.to_bytes(parsed_IP_packet["TTL"])
    id = int.to_bytes(parsed_IP_packet["ID"], 2)
    offset = int.to_bytes(parsed_IP_packet["Offset"], 2)
    tamaño = int.to_bytes(parsed_IP_packet["Tamaño"], 4)
    flag = int.to_bytes(parsed_IP_packet["FLAG"])

    return ip + puerto + ttl + id + offset + tamaño + flag + parsed_IP_packet["Mensaje"]
