from flask import Flask, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Conexión a la base de datos
config = {
    'user': 'user',
    'password': 'password',
    'host': 'mysql_db',
    'database': 'data_db'
}

def get_data_from_db(query):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# Ruta para exponer el KPI 1: Tasa de Resolución de Solicitudes
@app.route('/get_tasa_resolucion_por_tipo', methods=['GET'])
def get_tasa_resolucion_por_tipo():
    query = "SELECT * FROM tasa_resolucion_por_tipo"
    results = get_data_from_db(query)
    return jsonify(results)

# Ruta para exponer el KPI 2: Volumen de solicitudes por origen
@app.route('/get_volumen_solicitudes_por_origen', methods=['GET'])
def get_volumen_solicitudes_por_origen():
    query = "SELECT * FROM volumen_solicitudes_por_origen"
    results = get_data_from_db(query)
    return jsonify(results)

# Ruta para exponer el KPI 3: Estado de las Solicitudes
@app.route('/get_distribucion_estados', methods=['GET'])
def get_distribucion_estados():
    query = "SELECT * FROM distribucion_estados"
    results = get_data_from_db(query)
    return jsonify(results)

# Ruta para exponer el KPI 4: Tiempo promedio de resolucion
@app.route('/get_tiempo_promedio_resolucion', methods=['GET'])
def get_tiempo_promedio_resolucion():
    query = "SELECT * FROM tiempo_promedio_resolucion"
    results = get_data_from_db(query)
    return jsonify(results)

# Ruta para exponer el KPI 5: Tasa inadmitidas anuladas
@app.route('/get_tasa_inadmitidas_anuladas', methods=['GET'])
def get_tasa_rechazadas_anuladas():
    query = "SELECT * FROM tasa_inadmitidas_anuladas"
    results = get_data_from_db(query)
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000) 
