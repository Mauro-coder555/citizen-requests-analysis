import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Configuración de la conexión a MySQL usando SQLAlchemy
DB_CONFIG = {
    'host': 'mysql_db',  # El nombre del servicio en Docker Compose
    'user': 'user',  # Este debe ser 'MYSQL_USER' de docker-compose.yml
    'password': 'password',  # Este debe ser 'MYSQL_PASSWORD'
    'database': 'data_db'  # Este debe ser 'MYSQL_DATABASE'
}

# Definir la URL de conexión usando la configuración
DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"

# Crear motor SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)

def wait_for_mysql(engine):
    while True:
        try:
            # Intenta conectar con la base de datos
            connection = engine.connect()
            connection.close()
            print("¡MySQL está listo!")
            break  # Sale del bucle si la conexión es exitosa
        except OperationalError as err:
            print(f"Esperando a que MySQL esté listo... {err}")
            time.sleep(10)  # Espera 10 segundos antes de volver a intentar

def create_database():
    # Espera a que MySQL esté listo
    wait_for_mysql(engine)
    print("Base de datos conectada y lista para usarse.")

if __name__ == '__main__':
    # Crear la base de datos vacía o conectar a ella
    create_database()
