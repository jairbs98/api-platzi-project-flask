class Config:
    SECRET_KEY = "SUPER SECRET" # Usada por Flask para sesiones (si aún usas Flask-Login o flash messages)
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:admin@bd-todo-flask-container:5432/todo"
    )
    JWT_SECRET_KEY = "tu-clave-secreta-jwt-muy-segura" # <-- ¡CAMBIA ESTO POR UNA CLAVE SEGURA!
    # Opcional: Configuración para Flask-Mail (si implementas envío de correos)
    # MAIL_SERVER = 'smtp.example.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'your-email@example.com'
    # MAIL_PASSWORD = 'your-email-password'
    # MAIL_DEFAULT_SENDER = 'your-email@example.com'