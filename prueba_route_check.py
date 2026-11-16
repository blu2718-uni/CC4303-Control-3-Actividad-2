from router import check_routes, tabulador, en_red, rutas

print(check_routes("rutas/v2/rutas_R3_v2.txt", ("127.0.0.1", 8882)))  # ('127.0.0.1', 8882)
print(check_routes("rutas/v2/rutas_R3_v2.txt", ("127.0.0.1", 8881)))  # ('127.0.0.1', 8882)
print(check_routes("rutas/v2/rutas_R3_v2.txt", ("127.0.0.1", 8883)))  # None

rutas.clear()  # olvida la tabla de R3 para cargar la de R2

print(check_routes("rutas/v2/rutas_R2_v2.txt", ("127.0.0.1", 8881)))  # ('127.0.0.1', 8881)
print(check_routes("rutas/v2/rutas_R2_v2.txt", ("127.0.0.1", 8883)))  # ('127.0.0.1', 8881)
print(check_routes("rutas/v2/rutas_R2_v2.txt", ("127.0.0.1", 8882)))  # None
print(check_routes("rutas/v2/rutas_R2_v2.txt", ("127.0.1.1", 8881)))  # None

print(en_red("127.0.0.200", "127.0.0.1/24"))  # True
print(en_red("127.0.1.1", "127.0.0.1/24"))  # False
print(en_red("10.10.0.1", "10.1.0.0/16"))  # False
