import time
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

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
Session = sessionmaker(bind=engine)

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

# Definición de la tabla "solicitudes_procesadas" con columnas ajustadas
class SolicitudesProcesadas(Base):
    __tablename__ = 'solicitudes_procesadas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Identificador único
    n_registro = Column(String(50))  # Nº Registro
    tipo = Column(String(255))  # Tipo de solicitud
    estado = Column(String(255))  # Estado de la solicitud
    fecha_solicitud = Column(Date)  # Fecha de solicitud
    fecha_resolucion = Column(Date)
    origen = Column(String(255))  # Origen de la solicitud
    unidad = Column(String(255))  # Unidad responsable
    provincia = Column(String(255))  # Provincia
    referencia = Column(Text)  # Texto de referencia
    mes = Column(Integer)  # Mes de la solicitud
    año = Column(Integer)  # Año de la solicitud

def create_database_and_table():
    # Espera a que MySQL esté listo antes de crear la tabla
    wait_for_mysql(engine)

    # Crea las tablas si no existen
    Base.metadata.create_all(engine)
    print("Tabla 'solicitudes_procesadas' creada o verificada.")

def load_data_to_table():
    # Leer el archivo CSV (Asegúrate de que la ruta del archivo sea correcta)
    csv_file = 'data/requests.csv'
    df = pd.read_csv(csv_file, sep=';', parse_dates=['F.Solicitud'])

    # Cambiar el nombre de las columnas en el DataFrame para que coincidan con la tabla
    df.columns = [
        'n_registro',
        'tipo',
        'estado',
        'fecha_solicitud',
        'fecha_resolucion',
        'origen',
        'unidad',
        'provincia',
        'referencia'
    ]

    # Agregar columnas adicionales 'mes' y 'año' basadas en la fecha de solicitud
    df['mes'] = df['fecha_solicitud'].dt.month
    df['año'] = df['fecha_solicitud'].dt.year

    # Crear una nueva sesión de base de datos
    session = Session()

    try:
        # Convertir el DataFrame a una lista de diccionarios para la carga en la base de datos
        data_to_insert = df.to_dict(orient='records')
        
        # Insertar los datos en la base de datos
        session.bulk_insert_mappings(SolicitudesProcesadas, data_to_insert)
        session.commit()
        print(f"Se han insertado {len(data_to_insert)} registros en la tabla 'solicitudes_procesadas'.")
    except Exception as e:
        session.rollback()  # Deshacer la transacción en caso de error
        print(f"Error al insertar datos: {e}")
    finally:
        session.close()  # Cerrar la sesión

if __name__ == '__main__':
    # Crear la tabla si no existe
    create_database_and_table()
    
    # Cargar los datos en la tabla
    load_data_to_table()
