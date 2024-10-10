from flask import Flask, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Conexión a la base de datos (esto puede ir en una función si prefieres)
config = {
    'user': 'user',          # Cambia por tu usuario de MySQL
    'password': 'password',   # Cambia por tu contraseña de MySQL
    'host': 'localhost',      # Cambia si tu servidor está en otro lugar
    'database': 'data_db'     # Cambia por el nombre de tu base de datos
}

def get_data_from_db(query):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Ruta para exponer el KPI 1: Tiempo de Resolución de Solicitudes
@app.route('/get_kpi_tiempo_resolucion', methods=['GET'])
def get_kpi_tiempo_resolucion():
    query = "SELECT * FROM kpi_tiempo_resolucion"
    results = get_data_from_db(query)
    return jsonify(results)

# Ruta para exponer el KPI 2: Porcentaje de origen 'LIBRO'
@app.route('/get_kpi_origen_libro', methods=['GET'])
def get_kpi_origen_libro():
    query = "SELECT * FROM kpi_origen_libro"
    results = get_data_from_db(query)
    return jsonify(results)

# Ruta para exponer el KPI 3: Estado de las Solicitudes
@app.route('/get_kpi_estado_solicitudes', methods=['GET'])
def get_kpi_estado_solicitudes():
    query = "SELECT * FROM kpi_estado_solicitudes"
    results = get_data_from_db(query)
    return jsonify(results)

# Ruta para exponer las medidas generales de interés
@app.route('/get_medidas_interesantes', methods=['GET'])
def get_medidas_interesantes():
    query = "SELECT * FROM medidas_interesantes"
    results = get_data_from_db(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
