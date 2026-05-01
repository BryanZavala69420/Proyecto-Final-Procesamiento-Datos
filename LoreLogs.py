import random
from datetime import datetime, timedelta

# Configuración
num_registros = 1892
archivo_salida = "logs_servidor.txt"

niveles = ["INFO", "WARNING", "ERROR"]
endpoints = ["/api/login", "/api/productos", "/api/carrito", "/api/pago", "/home"]

codigos_http = {
    "INFO": [200, 201],
    "WARNING": [400, 404],
    "ERROR": [500, 502, 503]
}

# Generar registros
fecha_inicio = datetime.now()

with open(archivo_salida, "w", encoding="utf-8") as f:
    for i in range(num_registros):
        fecha = fecha_inicio + timedelta(seconds=i * random.randint(1, 5))
        
        nivel = random.choice(niveles)
        endpoint = random.choice(endpoints)
        codigo = random.choice(codigos_http[nivel])
        tiempo = random.randint(50, 1000)  # ms

        linea = f"{fecha.strftime('%Y-%m-%d %H:%M:%S')} | {nivel} | {endpoint} | {codigo} | {tiempo}ms\n"
        f.write(linea)

print(f"Archivo '{archivo_salida}' generado con {num_registros} registros.")