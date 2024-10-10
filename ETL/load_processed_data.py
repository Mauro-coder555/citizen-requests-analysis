import pandas as pd
import mysql.connector
import numpy as np

# Leer el archivo CSV con la columna F.Resolucion ya agregada
df = pd.read_csv('data/requests.csv', sep=';')

# Asegurarnos de que las columnas 'F.Solicitud' y 'F.Resolucion' estén en formato de fecha
df['F.Solicitud'] = pd.to_datetime(df['F.Solicitud'], errors='coerce')
df['F.Resolucion'] = pd.to_datetime(df['F.Resolucion'], errors='coerce')

# Conexión a MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'data_db'
}

connection = mysql.connector.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    database=DB_CONFIG['database']
)
cursor = connection.cursor()

# Crear las tablas si no existen
create_tables_sql = [
    """
    CREATE TABLE IF NOT EXISTS kpi_tiempo_resolucion (
        trimestre INT,
        año INT,
        objetivo DECIMAL(5, 2),
        tiempo_promedio_resolucion DECIMAL(5, 2),
        total_resueltas INT,
        año_trimestre VARCHAR(20),
        PRIMARY KEY (trimestre, año)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS kpi_porcentaje_resueltas (
        trimestre INT,
        año INT,
        porcentaje_resueltas DECIMAL(5, 2),
        objetivo DECIMAL(5, 2),
        año_trimestre VARCHAR(20),
        PRIMARY KEY (trimestre, año)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS kpi_distribucion_origen (
        trimestre INT,
        año INT,
        origen VARCHAR(50),
        cantidad INT,
        total_solicitudes INT,
        porcentaje DECIMAL(5, 2),
        objetivo DECIMAL(5, 2),
        año_trimestre VARCHAR(20),
        PRIMARY KEY (trimestre, año, origen)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS kpi_medidas (
        año INT,
        trimestre INT,
        resueltas INT,
        no_resueltas INT,
        total_solicitudes INT,
        porcentaje_resueltas DECIMAL(5, 2),
        porcentaje_no_resueltas DECIMAL(5, 2),
        año_trimestre VARCHAR(20),
        PRIMARY KEY (año, trimestre)
    )
    """
]

# Ejecutar cada consulta para crear las tablas
for query in create_tables_sql:
    cursor.execute(query)

# Procesar los datos y calcular KPIs
df['trimestre'] = df['F.Solicitud'].dt.to_period('Q').dt.quarter
df['año'] = df['F.Solicitud'].dt.year

# Crear un dataframe con la combinación completa de trimestres y años
trimestres_completos = pd.DataFrame({
    'trimestre': [1, 2, 3, 4] * len(df['año'].unique()),
    'año': sorted(df['año'].unique().tolist() * 4)
})

# --- KPI 1: Tiempo Promedio de Resolución ---
kpi_tiempo_resolucion = df[df['Estado'] == 'Contestado'].copy()
kpi_tiempo_resolucion['tiempo_resolucion'] = (kpi_tiempo_resolucion['F.Resolucion'] - kpi_tiempo_resolucion['F.Solicitud']).dt.days

# Crear columna año_trimestre
kpi_tiempo_resolucion['año_trimestre'] = kpi_tiempo_resolucion['año'].astype(str) + '-Q' + kpi_tiempo_resolucion['trimestre'].astype(str)

# Agrupar por trimestre y año, calculando el tiempo promedio de resolución
kpi_tiempo_resolucion_agg = kpi_tiempo_resolucion.groupby(['trimestre', 'año', 'año_trimestre']).agg(
    tiempo_promedio_resolucion=pd.NamedAgg(column='tiempo_resolucion', aggfunc='mean'),
    total_resueltas=pd.NamedAgg(column='Estado', aggfunc='count')
).reset_index()

# Definir el objetivo
objetivo_tiempo_resolucion = 270  # Por ejemplo, el objetivo es que el tiempo promedio no exceda 27 días

# Insertar en la tabla MySQL
for index, row in kpi_tiempo_resolucion_agg.iterrows():
    cursor.execute("""
    INSERT INTO kpi_tiempo_resolucion (trimestre, año, tiempo_promedio_resolucion, total_resueltas, objetivo, año_trimestre)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (row['trimestre'], row['año'], row['tiempo_promedio_resolucion'], row['total_resueltas'], objetivo_tiempo_resolucion, row['año_trimestre']))



# --- KPI 2: Porcentaje de Solicitudes Resueltas ---
kpi_resueltas = df.groupby(['trimestre', 'año']).agg(
    porcentaje_resueltas=pd.NamedAgg(column='Estado', aggfunc=lambda x: (x == 'Contestado').sum() / x.count() * 100)
).reset_index()

# Asegurar que todos los trimestres estén presentes en kpi_resueltas
kpi_resueltas = pd.merge(trimestres_completos, kpi_resueltas, on=['trimestre', 'año'], how='left')
kpi_resueltas['porcentaje_resueltas'] = kpi_resueltas['porcentaje_resueltas'].fillna(0)

# Calcular el objetivo: 10% más que el trimestre anterior o 50% inicial
kpi_resueltas['objetivo'] = kpi_resueltas['porcentaje_resueltas'].shift(1) * 1.10
kpi_resueltas['objetivo'] = kpi_resueltas['objetivo'].fillna(50)

# Crear columna de identificación de trimestre-año
kpi_resueltas['año_trimestre'] = kpi_resueltas['año'].astype(str) + "-Q" + kpi_resueltas['trimestre'].astype(str)

# Insertar en MySQL
for index, row in kpi_resueltas.iterrows():
    cursor.execute("""
    INSERT INTO kpi_porcentaje_resueltas (trimestre, año, porcentaje_resueltas, objetivo, año_trimestre)
    VALUES (%s, %s, %s, %s, %s)
    """, (row['trimestre'], row['año'], row['porcentaje_resueltas'], row['objetivo'], row['año_trimestre']))

# --- KPI 3: Distribución de Solicitudes por Origen ---
kpi_libro = df[df['Origen'] == 'LIBRO'].groupby(['trimestre', 'año']).agg(
    cantidad_libro=pd.NamedAgg(column='Estado', aggfunc='count')
).reset_index()

total_solicitudes_trimestre = df.groupby(['trimestre', 'año']).agg(
    total_solicitudes=pd.NamedAgg(column='Estado', aggfunc='count')
).reset_index()

kpi_libro = kpi_libro.merge(total_solicitudes_trimestre, on=['trimestre', 'año'], how='left')
kpi_libro['porcentaje'] = kpi_libro['cantidad_libro'] / kpi_libro['total_solicitudes'] * 100
kpi_libro['objetivo'] = kpi_libro['porcentaje'].shift(1) * 0.90  # Objetivo de reducir en un 10%
kpi_libro['objetivo'] = kpi_libro['objetivo'].fillna(0)  # El objetivo del primer trimestre es 0

# Crear columna de identificación de trimestre-año
kpi_libro['año_trimestre'] = kpi_libro['año'].astype(str) + "-Q" + kpi_libro['trimestre'].astype(str)

# Insertar en MySQL
for index, row in kpi_libro.iterrows():
    cursor.execute("""
    INSERT INTO kpi_distribucion_origen (trimestre, año, origen, cantidad, total_solicitudes, porcentaje, objetivo, año_trimestre)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (row['trimestre'], row['año'], 'LIBRO', row['cantidad_libro'], row['total_solicitudes'], row['porcentaje'], row['objetivo'], row['año_trimestre']))

# --- KPI 4: Medidas Comparativas ---
df['solicitudes_resueltas'] = df['Estado'] == 'Contestado'
kpi_medidas = df.groupby(['año', 'trimestre']).agg(
    resueltas=pd.NamedAgg(column='solicitudes_resueltas', aggfunc='sum'),
    no_resueltas=pd.NamedAgg(column='solicitudes_resueltas', aggfunc=lambda x: (~x).sum()),
    total_solicitudes=pd.NamedAgg(column='Estado', aggfunc='count')
).reset_index()

kpi_medidas['porcentaje_resueltas'] = (kpi_medidas['resueltas'] / kpi_medidas['total_solicitudes']) * 100
kpi_medidas['porcentaje_no_resueltas'] = (kpi_medidas['no_resueltas'] / kpi_medidas['total_solicitudes']) * 100
kpi_medidas['año_trimestre'] = kpi_medidas['año'].astype(str) + "-Q" + kpi_medidas['trimestre'].astype(str)

# Insertar en MySQL
for index, row in kpi_medidas.iterrows():
    cursor.execute("""
    INSERT INTO kpi_medidas (año, trimestre, resueltas, no_resueltas, total_solicitudes, porcentaje_resueltas, porcentaje_no_resueltas, año_trimestre)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (row['año'], row['trimestre'], row['resueltas'], row['no_resueltas'], row['total_solicitudes'], row['porcentaje_resueltas'], row['porcentaje_no_resueltas'], row['año_trimestre']))

# Confirmar los cambios
connection.commit()

# Cerrar la conexión
cursor.close()
connection.close()
