import pandas as pd
import mysql.connector
from datetime import datetime

# Configuración de conexión a MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'data_db'
}

# Conexión a la base de datos y creación de tablas
with mysql.connector.connect(**DB_CONFIG) as connection:
    with connection.cursor(buffered=True) as cursor:
        # Crear tablas de KPIs y medidas generales
        table_queries = [
            """
            CREATE TABLE IF NOT EXISTS kpi_tiempo_resolucion (
                id INT AUTO_INCREMENT PRIMARY KEY,
                estado VARCHAR(50),
                tiempo_resolucion_promedio FLOAT,
                solicitudes_resueltas INT,
                rango_tiempo VARCHAR(50),
                año INT,
                trimestre INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS kpi_origen_libro (
                id INT AUTO_INCREMENT PRIMARY KEY,
                total_solicitudes INT,
                total_libro INT,
                porcentaje_libro FLOAT,
                objetivo_reduccion FLOAT,
                año INT,
                trimestre INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS kpi_estado_solicitudes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                estado VARCHAR(50),
                cantidad INT,
                porcentaje_total FLOAT,
                año INT,
                trimestre INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS medidas_interesantes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                total_resueltas INT,
                total_no_resueltas INT,
                porcentaje_resueltas FLOAT,
                solicitudes_origen_libro INT,
                solicitudes_origen_web INT,
                solicitudes_origen_escrito INT,
                solicitudes_origen_otros INT,
                año INT,
                trimestre INT
            )
            """
        ]
        
        # Ejecutar las consultas de creación de tablas
        for query in table_queries:
            cursor.execute(query)
        connection.commit()

    # Leer archivo CSV y preparar el DataFrame
    df_solicitudes = pd.read_csv('data/requests.csv', sep=';')

    # Conversión de columnas a datetime para manipulación de fechas
    df_solicitudes['F.Solicitud'] = pd.to_datetime(df_solicitudes['F.Solicitud'])
    df_solicitudes['F.Resolucion'] = pd.to_datetime(df_solicitudes['F.Resolucion'])
    
    # Crear columnas para Año y Trimestre
    df_solicitudes['Año'] = df_solicitudes['F.Solicitud'].dt.year
    df_solicitudes['Trimestre'] = df_solicitudes['F.Solicitud'].dt.quarter

    # Calcular el tiempo de resolución en días
    df_solicitudes['tiempo_resolucion_dias'] = (df_solicitudes['F.Resolucion'] - df_solicitudes['F.Solicitud']).dt.days

    # Filtrar solo las solicitudes resueltas
    df_resueltas = df_solicitudes[df_solicitudes['Estado'].isin(['Contestado', 'Resuelto'])]

    # Agrupar y calcular KPIs por Año y Trimestre
    agrupado = df_solicitudes.groupby(['Año', 'Trimestre'])

    # Recorrer cada agrupación para calcular e insertar KPIs
    for (año, trimestre), grupo in agrupado:
        # KPI 1: Tiempo de Resolución Promedio
        grupo_resueltas = grupo[grupo['Estado'].isin(['Contestado', 'Resuelto'])]
        tiempo_promedio_resolucion = grupo_resueltas['tiempo_resolucion_dias'].mean()
        solicitudes_resueltas = len(grupo_resueltas)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO kpi_tiempo_resolucion (estado, tiempo_resolucion_promedio, solicitudes_resueltas, rango_tiempo, año, trimestre)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('Resueltas', tiempo_promedio_resolucion, int(solicitudes_resueltas), 'Trimestral', int(año), int(trimestre)))
            connection.commit()

        # KPI 2: Porcentaje de Origen "LIBRO"
        total_solicitudes = len(grupo)
        total_libro = len(grupo[grupo['Origen'] == 'LIBRO'])
        porcentaje_libro = (total_libro / total_solicitudes) * 100
        objetivo_reduccion = porcentaje_libro - 5  # Reducción del 5%

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO kpi_origen_libro (total_solicitudes, total_libro, porcentaje_libro, objetivo_reduccion, año, trimestre)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (int(total_solicitudes), int(total_libro), porcentaje_libro, objetivo_reduccion, int(año), int(trimestre)))
            connection.commit()

        # KPI 3: Cantidad de solicitudes por estado
        estado_counts = grupo['Estado'].value_counts()
        with connection.cursor() as cursor:
            for estado, cantidad in estado_counts.items():
                porcentaje_estado = (cantidad / total_solicitudes) * 100
                cursor.execute("""
                    INSERT INTO kpi_estado_solicitudes (estado, cantidad, porcentaje_total, año, trimestre)
                    VALUES (%s, %s, %s, %s, %s)
                """, (estado, int(cantidad), porcentaje_estado, int(año), int(trimestre)))
            connection.commit()

        # Tabla de medidas generales
        total_resueltas = len(grupo[grupo['Estado'].isin(['Contestado', 'Resuelto'])])
        total_no_resueltas = total_solicitudes - total_resueltas
        porcentaje_resueltas = (total_resueltas / total_solicitudes) * 100

        solicitudes_origen_libro = len(grupo[grupo['Origen'] == 'LIBRO'])
        solicitudes_origen_web = len(grupo[grupo['Origen'] == 'WEB'])
        solicitudes_origen_escrito = len(grupo[grupo['Origen'] == 'ESCRITO'])
        solicitudes_origen_otros = total_solicitudes - (solicitudes_origen_libro + solicitudes_origen_web + solicitudes_origen_escrito)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO medidas_interesantes (
                    total_resueltas, total_no_resueltas, porcentaje_resueltas,
                    solicitudes_origen_libro, solicitudes_origen_web,
                    solicitudes_origen_escrito, solicitudes_origen_otros,
                    año, trimestre
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (int(total_resueltas), int(total_no_resueltas), porcentaje_resueltas,
                  int(solicitudes_origen_libro), int(solicitudes_origen_web),
                  int(solicitudes_origen_escrito), int(solicitudes_origen_otros),
                  int(año), int(trimestre)))
            connection.commit()
