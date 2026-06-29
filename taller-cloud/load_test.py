import csv
import time
from datetime import datetime
import requests

URL = "http://127.0.0.1:5000/sensor"
TOTAL_SOLICITUDES = 30
RESULTADOS = []

exitos = 0
fallos = 0

print("Prueba de carga controlada sobre EcoVision IA")
print("-" * 60)

for numero in range(1, TOTAL_SOLICITUDES + 1):
    inicio = time.perf_counter()
    estado = "ERROR"
    codigo = 0
    detalle = ""

    try:
        respuesta = requests.post(
            URL,
            json={
                "sensor_id": f"IOT-{numero:03d}",
                "valor": round(20 + (numero * 0.37), 2),
            },
            timeout=3,
        )
        codigo = respuesta.status_code
        detalle = respuesta.text[:120]

        if 200 <= codigo < 300:
            estado = "OK"
            exitos += 1
        else:
            fallos += 1
    except requests.RequestException as error:
        fallos += 1
        detalle = str(error)

    latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)

    RESULTADOS.append(
        {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "solicitud": numero,
            "estado": estado,
            "codigo_http": codigo,
            "latencia_ms": latencia_ms,
            "detalle": detalle,
        }
    )

    print(
        f"Solicitud {numero:02d} | {estado:5s} | "
        f"HTTP {codigo:3d} | {latencia_ms:8.2f} ms"
    )
    time.sleep(0.15)

with open("metricas.csv", "w", newline="", encoding="utf-8-sig") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=RESULTADOS[0].keys())
    escritor.writeheader()
    escritor.writerows(RESULTADOS)

tasa_error = round((fallos / TOTAL_SOLICITUDES) * 100, 2)

print("-" * 60)
print(f"Solicitudes totales: {TOTAL_SOLICITUDES}")
print(f"Exitosas: {exitos}")
print(f"Fallidas: {fallos}")
print(f"Tasa de error: {tasa_error}%")
print("Archivo generado: metricas.csv")
