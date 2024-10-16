# Proyecto: Análisis de Solicitudes y KPIs con MySQL, ETL y Gráficos AMCharts

Este proyecto tiene como objetivo procesar un conjunto de solicitudes de servicios públicos, almacenarlas en una base de datos MySQL y generar indicadores clave de rendimiento (KPIs) utilizando un flujo de ETL. Los resultados se visualizan utilizando gráficos interactivos con **AMCharts**.

## Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Ejecución del Proyecto](#ejecución-del-proyecto)
5. [Visualización de Resultados](#visualización-de-resultados)

## Descripción del Proyecto

El proyecto está compuesto por varios componentes:
- **ETL**: Proceso de Extracción, Transformación y Carga de datos desde un archivo CSV hacia una base de datos MySQL.
- **Base de Datos**: MySQL se utiliza para almacenar los datos procesados y calcular KPIs.
- **Visualización**: Se usan gráficos interactivos de AMCharts para mostrar los KPIs generados.
- **Docker**: El entorno se ejecuta en contenedores Docker, lo que facilita la reproducción y configuración del proyecto.

## Estructura del Proyecto

El proyecto se organiza de la siguiente manera:

| Archivo                | Descripción                                                                                           |
|------------------------|-------------------------------------------------------------------------------------------------------|
| `docker-compose.yml`    | Define los servicios necesarios: MySQL y el entorno Python para el proceso ETL.                       |
| `Dockerfile`            | Imagen de Docker para el entorno Python que incluye la instalación de dependencias.                   |
| `setup_db.py`           | Script que espera la disponibilidad de MySQL, configura la base de datos.     |
| `etl_process.py`        | Realiza el procesamiento de datos desde el CSV, crea tablas en la base mysql, inserta los datos y calcula KPIs.        |
| `app.py`                | Sirve los datos de la base de datos a la interfaz gráfica para la visualización en AMCharts.          |
| `amcharts/index.html`            | Página principal que contiene los gráficos interactivos generados con AMCharts.                      |
| `data/requests.csv`     | Archivo CSV origen que contiene las solicitudes de servicio público.     |



## Instalación y Configuración

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Mauro-coder555/citizen-requests-analysis
   cd https://github.com/Mauro-coder555/citizen-requests-analysis
Asegúrate de tener Docker y Docker Compose instalados en tu sistema.

Levanta los servicios:
docker-compose up

## Ejecución del Proyecto

El proceso completo de ETL y generación de KPIs se automatiza mediante Docker. Una vez que los contenedores estén en ejecución:

    El archivo requests.csv es procesado y cargado en la base de datos MySQL.
    Se calculan diversos KPIs a partir de los datos y se almacenan en tablas de la base de datos.
    Los datos son servidos a la aplicación web con AMCharts para su visualización.

## Visualización de Resultados

Una vez que todos los servicios están en marcha, accede al archivo index.html en la carpeta amcharts para ver los gráficos interactivos que muestran los KPIs calculados.

Los KPIs generados incluyen:

    Tasa de resolución por tipo de solicitud.
    Volumen de solicitudes por origen.
    Distribución de estados de las solicitudes.
    Tiempo promedio de resolución por tipo y origen.
    Tasa de solicitudes inadmitidas o anuladas.

¡Gracias por revisar el proyecto! No dudes en contactarme para más información o consultas.