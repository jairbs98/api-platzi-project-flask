# Usa la imagen base de Python 3.12 en Alpine Linux
FROM python:3.12-alpine

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /source

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente (ahora en la carpeta 'src') al contenedor
COPY src .

# Crea un usuario no root para ejecutar la aplicación
RUN adduser -D myuser
USER myuser

# Expone el puerto 5000
EXPOSE 5000

# Comando para ejecutar la aplicación (asegúrate de que main.py se ejecute desde /app/src)
CMD ["python", "main.py"]