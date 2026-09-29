# 1. Usar la imagen oficial ligera de Python
FROM python:3.12-slim

# 2. Copiar el binario oficial de uv desde su imagen optimizada
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Variables de entorno esenciales
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Evita problemas de enlaces entre sistemas de archivos en Docker
ENV UV_LINK_MODE=copy
# Hace que uv instale directamente en el entorno de Python del sistema (sin necesidad de crear un .venv dentro del contenedor)
ENV UV_SYSTEM_PYTHON=1
ENV PYTHONPATH=/app

# 4. Carpeta de trabajo
WORKDIR /app

# 5. Copiar únicamente los archivos de dependencias de uv primero (para aprovechar la caché de Docker)
COPY pyproject.toml uv.lock ./

# 6. Instalar las dependencias exactas bloqueadas en uv.lock
RUN uv pip install --no-cache -r pyproject.toml

# 7. Copiar el resto del código del proyecto
COPY . .

# 8. Exponer el puerto
EXPOSE 8000

# 9. Comando de arranque
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]