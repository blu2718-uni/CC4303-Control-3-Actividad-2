from router import check_routes, tabulador, en_red, rutas

# Tabla de R2: un salto hacia R1 y dos saltos (round robin) hacia R3-R5
print(check_routes("rutas/v3/rutas_R2_v3_mtu.txt", ("127.0.0.1", 8881)))  # ('127.0.0.1', 8881, 100)
print(check_routes("rutas/v3/rutas_R2_v3_mtu.txt", ("127.0.0.1", 8885)))  # ('127.0.0.1', 8883, 50)
print(check_routes("rutas/v3/rutas_R2_v3_mtu.txt", ("127.0.0.1", 8884)))  # ('127.0.0.1', 8884, 80)
print(check_routes("rutas/v3/rutas_R2_v3_mtu.txt", ("127.0.0.1", 8883)))  # ('127.0.0.1', 8883, 50)
print(check_routes("rutas/v3/rutas_R2_v3_mtu.txt", ("127.0.0.1", 8882)))  # None
print(check_routes("rutas/v3/rutas_R2_v3_mtu.txt", ("127.0.1.1", 8881)))  # None

rutas.clear()  # olvida la tabla de R2 para cargar la de R1

print(check_routes("rutas/v3/rutas_R1_v3_mtu.txt", ("127.0.0.1", 8885)))  # ('127.0.0.1', 8882, 100)
print(check_routes("rutas/v3/rutas_R1_v3_mtu.txt", ("127.0.0.1", 8882)))  # ('127.0.0.1', 8882, 100)
print(check_routes("rutas/v3/rutas_R1_v3_mtu.txt", ("127.0.0.1", 8881)))  # None

print(en_red("127.0.0.200", "127.0.0.1/24"))  # True
print(en_red("127.0.1.1", "127.0.0.1/24"))  # False
print(en_red("10.10.0.1", "10.1.0.0/16"))  # False
