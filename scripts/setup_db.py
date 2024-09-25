import mysql.connector

# Configuración de la conexión a MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'data_db'
}

def create_database_and_table():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return  # O maneja el error según necesites

    cursor = connection.cursor()

    # Verificar si la base de datos existe
    cursor.execute("SHOW DATABASES LIKE 'data_db'")
    db_exists = cursor.fetchone()
    
    if db_exists:
        print("La base de datos 'data_db' ya existe.")
    else:
        cursor.execute("CREATE DATABASE data_db")
        print("Base de datos 'data_db' creada por primera vez.")

    # Usar la base de datos
    cursor.execute("USE data_db")

    # Verificar si la tabla existe
    cursor.execute("SHOW TABLES LIKE 'solicitudes_procesadas'")
    table_exists = cursor.fetchone()

    if table_exists:
        print("La tabla 'solicitudes_procesadas' ya existe.")
    else:
        cursor.execute("""
            CREATE TABLE solicitudes_procesadas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tipo VARCHAR(255),
                estado VARCHAR(255),
                fecha_solicitud DATE,
                origen VARCHAR(255),
                unidad VARCHAR(255),
                provincia VARCHAR(255),
                referencia TEXT,
                mes INT,
                año INT,
                resolucion_rapida INT
            )
        """)
        print("Tabla 'solicitudes_procesadas' creada por primera vez.")

    cursor.close()
    connection.close()

if __name__ == '__main__':
    create_database_and_table()
