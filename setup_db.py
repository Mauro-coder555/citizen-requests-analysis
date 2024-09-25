import time
from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base

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

# Base para las tablas
Base = declarative_base()

class SolicitudesProcesadas(Base):
    __tablename__ = 'solicitudes_procesadas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(255))
    estado = Column(String(255))
    fecha_solicitud = Column(Date)
    origen = Column(String(255))
    unidad = Column(String(255))
    provincia = Column(String(255))
    referencia = Column(Text)
    mes = Column(Integer)
    año = Column(Integer)
    resolucion_rapida = Column(Integer)

def create_database_and_table():
    wait_for_mysql(engine)  # Espera a que MySQL esté listo

    # Crea las tablas si no existen
    Base.metadata.create_all(engine)
    print("Tabla 'solicitudes_procesadas' creada o verificada.")

if __name__ == '__main__':
    create_database_and_table()
