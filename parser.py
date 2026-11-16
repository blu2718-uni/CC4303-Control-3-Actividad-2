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
        "Mensaje": IP_packet[7:],
    }

    return paquete


def create_packet(parsed_IP_packet):
    l_ip = parsed_IP_packet["IP"].split(".")
    ip = b""

    for i in l_ip:
        ip += int.to_bytes(int(i), 1)

    port = int.to_bytes(parsed_IP_packet["Puerto"], 2)
    ttl = int.to_bytes(parsed_IP_packet["TTL"])
    return ip + port + ttl + parsed_IP_packet["Mensaje"]
