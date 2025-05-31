## Base de alpine con python para construir el distribuible
FROM python:3.13-alpine as builder 

RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev && \
    pip install pyinstaller

WORKDIR /source

ENV LC_ALL es_ES.UTF-8
ENV LANG es_ES.UTF-8
ENV LANGUAGE es_ES.UTF-8
ENV PYTHONIOENCODING=UTF-8

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt
COPY . .

RUN pyinstaller app.py --name=app --clean --log-level=WARN --onefile \
    --add-data "auth:auth" \
    --add-data "models:models" \
    --add-data "static:static" \
    --add-data "templates:templates"

# Base con Alpine para la imagen final (solo el distribuible)
FROM alpine:latest AS python-3.13

WORKDIR /sysx/progs/
COPY --from=builder /source/dist/*app ./

CMD ["./app"]

FROM python-3.13 AS image