import urllib.request
import urllib.error
import time
import json

def diagnosticar_api(url):
    print("=== Herramienta de Diagnóstico y Métricas - EcoVision IA ===")
    print("Analista: David Andrade (Módulo de Diagnóstico y Detección)")
    print(f"[*] Comprobando endpoint: {url}\n")

    inicio = time.time()
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            tiempo_respuesta = time.time() - inicio
            datos = json.loads(response.read().decode())

            print("[+] Estado HTTP: 200 OK")
            print(f"[+] Tiempo de respuesta (Latencia): {tiempo_respuesta:.4f} segundos")

            # Validación basada en los umbrales del informe (Tabla 3)
            if tiempo_respuesta > 1.5:
                print("[-] ALERTA CRÍTICA: Latencia supera 1.5s. Posible saturación del pool.")
            elif tiempo_respuesta > 1.0:
                print("[-] ADVERTENCIA: Latencia elevada (> 1.0s).")
            else:
                print("[+] Latencia dentro de los umbrales normales (< 1.0s).")

            print(f"[+] Estado Base de Datos: {datos.get('database', 'Desconocido')}")
            print(f"[+] Estado de la API: {datos.get('status', 'Desconocido')}")

    except urllib.error.URLError as e:
        print(f"[-] ERROR CRÍTICO: No se pudo conectar a la API. Detalles: {e}")
        print("[-] Hipótesis: Caída del servicio por agotamiento de conexiones.")

if __name__ == '__main__':
    # Simulación de revisión del entorno local
    diagnosticar_api("http://127.0.0.1:5000/health")
