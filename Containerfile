FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crea un usuario no root para ejecutar la aplicación
RUN adduser -D myuser
USER myuser

EXPOSE 5000

CMD ["python", "main.py"]