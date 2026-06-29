from flask import Flask, jsonify, request
import logging
import os
import sqlite3
from datetime import datetime, timezone

app = Flask(__name__)

DB_PATH = "ecovision.db"
VERSION = os.getenv("APP_VERSION", "2.0-fallida")

# Simulación controlada de un pool de conexiones defectuoso.
POOL_LIMITE = 10
conexiones_ocupadas = 0
solicitudes_totales = 0
errores_totales = 0

logging.basicConfig(
    filename="ecovision.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def conectar_db():
    conexion = sqlite3.connect(DB_PATH, timeout=5)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db():
    with conectar_db() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS datos_sensor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                valor REAL NOT NULL,
                fecha TEXT NOT NULL
            )
            """
        )
        conexion.commit()


@app.get("/")
def inicio():
    return jsonify(
        {
            "servicio": "EcoVision IA API",
            "version": VERSION,
            "endpoints": ["/health", "/sensor", "/dashboard", "/metrics"],
        }
    )


@app.get("/health")
def health():
    uso_pool = round((conexiones_ocupadas / POOL_LIMITE) * 100, 2)

    if conexiones_ocupadas >= POOL_LIMITE:
        logging.error(
            "Health check fallido | Connection pool exhausted | uso=%s%%", uso_pool
        )
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "version": VERSION,
                    "database": "pool_exhausted",
                    "pool_usage_percent": uso_pool,
                }
            ),
            503,
        )

    return (
        jsonify(
            {
                "status": "healthy",
                "version": VERSION,
                "database": "connected",
                "pool_usage_percent": uso_pool,
            }
        ),
        200,
    )


@app.post("/sensor")
def registrar_sensor():
    global conexiones_ocupadas, solicitudes_totales, errores_totales

    solicitudes_totales += 1
    datos = request.get_json(silent=True) or {}
    sensor_id = datos.get("sensor_id")
    valor = datos.get("valor")

    if not sensor_id or not isinstance(valor, (int, float)):
        errores_totales += 1
        return jsonify({"error": "sensor_id y valor numérico son obligatorios"}), 400

    # Error intencional: la conexión simulada se ocupa, pero nunca se libera.
    if conexiones_ocupadas >= POOL_LIMITE:
        errores_totales += 1
        logging.error(
            "Connection pool exhausted | Too many connections | "
            "solicitud=%s | pool=%s/%s",
            solicitudes_totales,
            conexiones_ocupadas,
            POOL_LIMITE,
        )
        return (
            jsonify(
                {
                    "error": "Database connection timeout",
                    "detalle": "Connection pool exhausted",
                    "version": VERSION,
                }
            ),
            503,
        )

    conexiones_ocupadas += 1
    fecha = datetime.now(timezone.utc).isoformat()

    try:
        with conectar_db() as conexion:
            conexion.execute(
                "INSERT INTO datos_sensor (sensor_id, valor, fecha) VALUES (?, ?, ?)",
                (sensor_id, valor, fecha),
            )
            conexion.commit()

        logging.info(
            "Dato guardado | sensor=%s | pool=%s/%s",
            sensor_id,
            conexiones_ocupadas,
            POOL_LIMITE,
        )
        return (
            jsonify(
                {
                    "mensaje": "Dato almacenado correctamente",
                    "sensor_id": sensor_id,
                    "valor": valor,
                    "version": VERSION,
                    "pool_en_uso": conexiones_ocupadas,
                }
            ),
            201,
        )
    except sqlite3.Error as error:
        errores_totales += 1
        logging.exception("Database connection timeout: %s", error)
        return jsonify({"error": "No fue posible guardar el dato"}), 503


@app.get("/dashboard")
def dashboard():
    try:
        with conectar_db() as conexion:
            filas = conexion.execute(
                """
                SELECT sensor_id, valor, fecha
                FROM datos_sensor
                ORDER BY id DESC
                LIMIT 20
                """
            ).fetchall()

        return jsonify(
            {
                "version": VERSION,
                "total_mostrado": len(filas),
                "datos": [dict(fila) for fila in filas],
            }
        )
    except sqlite3.Error as error:
        logging.exception("Error leyendo el dashboard: %s", error)
        return jsonify({"error": "Dashboard no disponible"}), 503


@app.get("/metrics")
def metrics():
    uso_pool = round((conexiones_ocupadas / POOL_LIMITE) * 100, 2)
    tasa_error = (
        round((errores_totales / solicitudes_totales) * 100, 2)
        if solicitudes_totales
        else 0
    )
    return jsonify(
        {
            "version": VERSION,
            "solicitudes_totales": solicitudes_totales,
            "errores_totales": errores_totales,
            "error_rate_percent": tasa_error,
            "pool_in_use": conexiones_ocupadas,
            "pool_limit": POOL_LIMITE,
            "pool_usage_percent": uso_pool,
        }
    )


if __name__ == "__main__":
    inicializar_db()
    logging.info("Inicio de EcoVision IA API | version=%s", VERSION)
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
