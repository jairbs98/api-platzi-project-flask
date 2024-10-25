## Contenedor Docker (Podman)

Este proyecto utiliza un contenedor Docker (Podman) para facilitar su despliegue y asegurar la consistencia del entorno de ejecución. 

**Containerfile**

El archivo `Containerfile` define las instrucciones para construir la imagen Docker:

```dockerfile
FROM python:3.12-alpine  # Usa la imagen base de Python 3.12 en Alpine Linux

WORKDIR /app  # Establece el directorio de trabajo dentro del contenedor

COPY requirements.txt .  # Copia el archivo de requerimientos
RUN pip install --no-cache-dir -r requirements.txt  # Instala las dependencias

COPY . .  # Copia el código fuente al contenedor

# Crea un usuario no root para ejecutar la aplicación
RUN adduser -D myuser 
USER myuser

EXPOSE 5000  # Expone el puerto 5000

CMD ["python", "main.py"]  # Comando para ejecutar la aplicación
```

```linux
podman build -t mi-imagen-flask .

podman run -d \
  --name platzi-project-flask \
  -v 'api-platzi-project-flask:/app' \
  -v "C:\ruta\a\tu\clave\privada.json:/app/clave_privada.json" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/clave_privada.json" \
  -p 5001:5000 \
  mi-imagen-flask