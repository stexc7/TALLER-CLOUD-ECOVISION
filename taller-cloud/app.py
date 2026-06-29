from flask import Flask, jsonify, request
import logging
import os
import sqlite3
from datetime import datetime, timezone

app = Flask(__name__)

DB_PATH = "ecovision.db"
VERSION = os.getenv("APP_VERSION", "1.0-estable")

logging.basicConfig(
    filename="ecovision.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def conectar_db():
    """Abre una conexión nueva y segura para cada operación."""
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
            "endpoints": ["/health", "/sensor", "/dashboard"],
        }
    )


@app.get("/health")
def health():
    try:
        with conectar_db() as conexion:
            conexion.execute("SELECT 1").fetchone()

        return (
            jsonify(
                {
                    "status": "healthy",
                    "version": VERSION,
                    "database": "connected",
                }
            ),
            200,
        )
    except sqlite3.Error as error:
        logging.exception("Fallo del health check: %s", error)
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "version": VERSION,
                    "database": "disconnected",
                }
            ),
            503,
        )


@app.post("/sensor")
def registrar_sensor():
    datos = request.get_json(silent=True) or {}
    sensor_id = datos.get("sensor_id")
    valor = datos.get("valor")

    if not sensor_id or not isinstance(valor, (int, float)):
        return jsonify({"error": "sensor_id y valor numérico son obligatorios"}), 400

    fecha = datetime.now(timezone.utc).isoformat()

    try:
        with conectar_db() as conexion:
            conexion.execute(
                "INSERT INTO datos_sensor (sensor_id, valor, fecha) VALUES (?, ?, ?)",
                (sensor_id, valor, fecha),
            )
            conexion.commit()

        logging.info("Dato guardado | sensor=%s | valor=%s", sensor_id, valor)
        return (
            jsonify(
                {
                    "mensaje": "Dato almacenado correctamente",
                    "sensor_id": sensor_id,
                    "valor": valor,
                    "version": VERSION,
                }
            ),
            201,
        )
    except sqlite3.Error as error:
        logging.exception("Error guardando el dato: %s", error)
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


if __name__ == "__main__":
    inicializar_db()
    logging.info("Inicio de EcoVision IA API | version=%s", VERSION)
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
