from flask import Flask
from flask_bootstrap import Bootstrap # Puedes considerar eliminar Flask-Bootstrap si ya no renderizas HTML.
from flask_login import LoginManager # Opcional: Si tu backend será puramente API, Flask-Login puede eliminarse.
from flask_cors import CORS # Nuevo: Importa Flask-CORS
from flask_jwt_extended import JWTManager # Nuevo: Importa Flask-JWT-Extended
# from flask_mail import Mail # Opcional: Si implementas envío de correos

from .config import Config
from .auth import auth
from .models import UserModel #

# login_manager = LoginManager() # Opcional: Comenta o elimina si ya no usas Flask-Login.
# login_manager.login_view = 'auth.login' # Opcional: Comenta o elimina si ya no usas Flask-Login.

# @login_manager.user_loader # Opcional: Comenta o elimina si ya no usas Flask-Login.
# def load_user(username):
#     return UserModel.query(username)

jwt = JWTManager() # Inicializa JWTManager
# mail = Mail() # Opcional: Inicializa Flask-Mail

def create_app():
    app = Flask(__name__)

    # bootstrap = Bootstrap(app) # Comentar o eliminar si no es necesario.

    app.config.from_object(Config)

    # login_manager.init_app(app) # Opcional: Comentar o eliminar si ya no usas Flask-Login.

    CORS(app) # Habilita CORS para todas las rutas. Para producción, especifica origins.
    jwt.init_app(app) # Inicializa JWT en la aplicación Flask
    # mail.init_app(app) # Opcional: Inicializa Flask-Mail

    app.register_blueprint(auth)

    return app