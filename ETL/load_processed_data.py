import pandas as pd
import mysql.connector
from mysql.connector import Error
import time

# Configuración de conexión a MySQL
DB_CONFIG = {
    'host': 'mysql_db',
    'user': 'user',
    'password': 'password',
    'database': 'data_db'
}

def create_tables(cursor):
    # Crear tabla de solicitudes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo VARCHAR(50),
            estado VARCHAR(50),
            fecha_solicitud DATE,
            origen VARCHAR(50),
            unidad VARCHAR(100),
            provincia VARCHAR(50),
            referencia TEXT,
            fecha_resolucion DATE,
            tiempo_resolucion INT -- Tiempo de resolución en días
        )
    ''')

    # KPI 1: Tasa de resolución por tipo de solicitud (agrupada por año)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasa_resolucion_por_tipo (
            año INT,  -- Año de las solicitudes
            tipo VARCHAR(50),
            total_solicitudes INT,
            solicitudes_resueltas INT,
            tasa_resolucion DECIMAL(5, 2)
        )
    ''')

    # KPI 2: Volumen de solicitudes por origen (agrupada por año)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS volumen_solicitudes_por_origen (
            año INT,  -- Año de las solicitudes
            origen VARCHAR(50),
            total_solicitudes INT
        )
    ''')

    # KPI 3: Distribución de estados (agrupada por año)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS distribucion_estados (
            año INT,  -- Año de las solicitudes
            estado VARCHAR(50),
            total_solicitudes INT
        )
    ''')

    # KPI 4: Tiempo promedio de resolución (Por tipo y por origen)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiempo_promedio_resolucion (
            año INT,  -- Año de las solicitudes
            tipo VARCHAR(50),
            origen VARCHAR(50),
            tiempo_promedio_resolucion DECIMAL(10, 2) -- Tiempo promedio en días
        )
    ''')

    # KPI 5: Tasa de solicitudes inadmitidas o anuladas (agrupada por año)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasa_inadmitidas_anuladas (
            año INT,  -- Año de las solicitudes
            total_solicitudes INT,
            total_inadmitidas INT,
            total_anuladas INT,
            tasa_inadmitidas_anuladas DECIMAL(5, 2)
        )
    ''')

def insert_requests(cursor, df):
    for index, row in df.iterrows():
        cursor.execute('''
            INSERT INTO solicitudes (tipo, estado, fecha_solicitud, origen, unidad, provincia, referencia, fecha_resolucion, tiempo_resolucion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            row['Tipo'],
            row['Estado'],
            row['F.Solicitud'],
            row['Origen'],
            row['Unidad'],
            row['Provincia'],
            row['Referencia'],
            row['F.Resolucion'],
            row['tiempo_resolucion']  # Días de diferencia entre F.Resolucion y F.Solicitud
        ))

def calculate_kpis(cursor):
    # KPI 1: Tasa de resolución por tipo de solicitud (por año)
    cursor.execute('''
        INSERT INTO tasa_resolucion_por_tipo (año, tipo, total_solicitudes, solicitudes_resueltas, tasa_resolucion)
        SELECT YEAR(fecha_solicitud) AS año,
               tipo,
               COUNT(*) AS total_solicitudes,
               SUM(CASE WHEN estado = 'Contestado' THEN 1 ELSE 0 END) AS solicitudes_resueltas,
               (SUM(CASE WHEN estado = 'Contestado' THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS tasa_resolucion
        FROM solicitudes
        GROUP BY año, tipo;
    ''')

    # KPI 2: Volumen de solicitudes por origen (por año)
    cursor.execute('''
        INSERT INTO volumen_solicitudes_por_origen (año, origen, total_solicitudes)
        SELECT YEAR(fecha_solicitud) AS año, origen, COUNT(*)
        FROM solicitudes
        GROUP BY año, origen;
    ''')

    # KPI 3: Distribución de estados de las solicitudes (por año)
    cursor.execute('''
        INSERT INTO distribucion_estados (año, estado, total_solicitudes)
        SELECT YEAR(fecha_solicitud) AS año, estado, COUNT(*)
        FROM solicitudes
        GROUP BY año, estado;
    ''')

    # KPI 4: Tiempo promedio de resolución por tipo y origen (por año)
    cursor.execute('''
        INSERT INTO tiempo_promedio_resolucion (año, tipo, origen, tiempo_promedio_resolucion)
        SELECT YEAR(fecha_solicitud) AS año,
               tipo,
               origen,
               AVG(tiempo_resolucion) AS tiempo_promedio_resolucion  -- Promedio de días de resolución
        FROM solicitudes
        WHERE tiempo_resolucion >= 0
        GROUP BY año, tipo, origen;
    ''')

    # KPI 5: Tasa de solicitudes Inadmitidas o anuladas (por año)
    cursor.execute('''
        INSERT INTO tasa_inadmitidas_anuladas (año, total_solicitudes, total_inadmitidas, total_anuladas, tasa_inadmitidas_anuladas)
        SELECT YEAR(fecha_solicitud) AS año,
               COUNT(*) AS total_solicitudes,
               SUM(CASE WHEN estado = 'Inadmitida' THEN 1 ELSE 0 END) AS total_inadmitidas,
               SUM(CASE WHEN estado = 'Anulada' THEN 1 ELSE 0 END) AS total_anuladas,
               ((SUM(CASE WHEN estado = 'Inadmitida' THEN 1 ELSE 0 END) + SUM(CASE WHEN estado = 'Anulada' THEN 1 ELSE 0 END)) / COUNT(*)) * 100 AS tasa_inadmitidas_anuladas
        FROM solicitudes
        GROUP BY año;
    ''')

def main():
    # Leer el archivo CSV con los datos de solicitudes
    df = pd.read_csv('data/requests.csv', sep=';')

    # Convertir las fechas a datetime
    df['F.Solicitud'] = pd.to_datetime(df['F.Solicitud'], format='%Y-%m-%d')
    df['F.Resolucion'] = pd.to_datetime(df['F.Resolucion'], format='%Y-%m-%d', errors='coerce')

    # Calcular tiempo de resolución en días
    df['tiempo_resolucion'] = (df['F.Resolucion'] - df['F.Solicitud']).dt.days

    # Reemplazar NaN con valores adecuados
    df.fillna({
        'Estado': 'Desconocido',
        'F.Resolucion': pd.Timestamp('2099-12-31'),  # Asumimos una fecha futura si no se ha resuelto
        'tiempo_resolucion': -1,  # -1 si no se ha resuelto
        'Origen': 'No especificado',
        'Unidad': 'No asignada'
    }, inplace=True)
    df.dropna(inplace=True)

    connection = None
    max_retries = 5  # Máximo número de reintentos
    retries = 0

    while retries < max_retries:
        try:
            # Intentar conectar a la base de datos
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                cursor = connection.cursor()
                create_tables(cursor)
                insert_requests(cursor, df)
                calculate_kpis(cursor)

                # Confirmar los cambios
                connection.commit()
                print("Conexión exitosa y datos insertados")
                break  # Salir del bucle si la conexión es exitosa
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            retries += 1
            print(f"Reintentando en 20 segundos... ({retries}/{max_retries})")
            time.sleep(20)  # Esperar 20 segundos antes de intentar nuevamente
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == "__main__":
    main()
