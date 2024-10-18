# 📊 Proyecto: Análisis de Solicitudes y KPIs con MySQL, ETL y Gráficos AMCharts

Este proyecto tiene como objetivo procesar un conjunto de solicitudes de servicios públicos, almacenarlas en una base de datos MySQL y generar indicadores clave de rendimiento (KPIs) utilizando un flujo de ETL. Los resultados se visualizan con gráficos interactivos usando **AMCharts**.

## 🗂️ Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Tecnologías Utilizadas](#tecnologías-utilizadas)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Ejecución del Proyecto](#ejecución-del-proyecto)
6. [Visualización de Resultados](#visualización-de-resultados)

---

## 📄 Descripción del Proyecto

El proyecto incluye varios componentes:

- **ETL**: Proceso de Extracción, Transformación y Carga (ETL) de datos desde un archivo CSV hacia una base de datos MySQL.
- **Base de Datos**: MySQL se utiliza para almacenar los datos procesados y calcular KPIs.
- **Visualización**: Se emplean gráficos interactivos con **AMCharts** para mostrar los KPIs generados.
- **Docker**: Todos los servicios se ejecutan en contenedores Docker para facilitar la configuración y la portabilidad.

---

## 🛠️ Tecnologías utilizadas

- ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
- ![MySQL](https://img.shields.io/badge/-MySQL-4479A1?logo=mysql&logoColor=white)
- ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)
- ![AMCharts](https://img.shields.io/badge/-AMCharts-FF6F61?logo=amcharts&logoColor=white)

---

## 🗂️ Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

| Archivo                | Descripción                                                                                           |
|------------------------|-------------------------------------------------------------------------------------------------------|
| `docker-compose.yml`    | Define los servicios necesarios: MySQL y el entorno Python para el proceso ETL.                       |
| `Dockerfile`            | Imagen de Docker para el entorno Python que incluye la instalación de dependencias.                   |
| `setup_db.py`           | Script que configura la base de datos MySQL.                            |
| `ETL/load_processed_data.py`        | Realiza el procesamiento de datos desde el CSV, crea tablas en MySQL, inserta los datos y calcula KPIs.|
| `app.py`                | Sirve los datos de la base de datos a la interfaz gráfica para la visualización en AMCharts.          |
| `amcharts/index.html`   | Página principal que contiene los gráficos interactivos generados con AMCharts.                      |
| `data/requests.csv`     | Archivo CSV origen que contiene las solicitudes de ciudanos.                                         |

---

## ⚙️ Instalación y Configuración

Ejecutar los siguientes comandos:

   ```bash
   git clone https://github.com/Mauro-coder555/citizen-requests-analysis
   cd citizen-requests-analysis
   docker-compose build
   ```

## ▶️ Ejecución del Proyecto

El proceso completo de ETL y generación de KPIs se automatiza mediante Docker.

Para iniciar los contenedores corremos el comando:

   ```bash
   docker-compose up
   ```

Una vez que los contenedores estén en ejecución:

- El archivo requests.csv es procesado y cargado en la base de datos MySQL.
- Se calculan diversos KPIs a partir de los datos y se almacenan en tablas de la base de datos.
- Los datos son servidos a la aplicación web con AMCharts para su visualización.

## 📊 Visualización de Resultados

Una vez que todos los servicios están en marcha, accede al archivo *index.html* en la carpeta amcharts para ver los gráficos interactivos que muestran los KPIs calculados.

Los KPIs generados incluyen:

- Tasa de resolución por tipo de solicitud.
- Volumen de solicitudes por origen.
- Distribución de estados de las solicitudes.
- Tiempo promedio de resolución por tipo y origen.
- Tasa de solicitudes inadmitidas o anuladas.

---

¡Gracias por revisar el proyecto! No dudes en contactarme para más información o consultas.

<img src="amcharts/mismatica.jpg" alt="Logo de la empresa" width="500" height="500">
