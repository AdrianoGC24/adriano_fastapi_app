# 1. Imagen base oficial de Python ligera
FROM python:3.12-slim

# 2. Evitar que Python genere archivos .pyc y forzar logs inmediatos en consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Le dice a Python que busque módulos en la raíz /app
ENV PYTHONPATH=/app

# 3. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar solo el requirements primero (aprovecha el caché de Docker)
COPY requirements.txt .

# 5. Instalar dependencias sin guardar caché de pip para reducir peso
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el resto del código del proyecto
COPY . .

# 7. Documentar el puerto que usará la aplicación
EXPOSE 8000

# 8. Comando de arranque de FastAPI
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]