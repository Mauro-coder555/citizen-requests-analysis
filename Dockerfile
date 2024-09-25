FROM python:3.9-slim

WORKDIR /app
COPY . /app

# Instalar dependencias
RUN pip install -r requirements.txt

# Ejecutar el script de setup directamente
CMD ["python", "setup_db.py"]
