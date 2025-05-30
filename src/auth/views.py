import secrets
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError # type: ignore

from flask import (
    request,
    jsonify,
    current_app,
)
from flask_login import (
    login_user,
    logout_user,
    current_user,
)
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from src.forms import (
    LoginForm,
    ChangePasswordForm,
    ResetPasswordForm,
    SignupForm,
)

from . import auth
from src.crud import create_user
from src.models import (
    UserModel,
    UserData,
    get_user,
    get_user_by_id,
    User
)
from src.database import get_db


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    db = next(get_db())
    user = get_user(username, db=db)

    if user is not None:
        password_from_db = user.password

        if check_password_hash(password_from_db, password):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token, message="Login successful"), 200
        else:
            return jsonify({"message": "Invalid credentials."}), 401
    else:
        return jsonify({"message": "The user does not exist."}), 404


@auth.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"message": "Username, password, and email are required."}), 400

    db = next(get_db())

    existing_user_by_username = get_user(username, db=db)
    if existing_user_by_username:
        return jsonify({"message": "The username already exists!"}), 409

    existing_user_by_email = db.query(User).filter(User.email == email).first()
    if existing_user_by_email:
        return jsonify({"message": "A user with that email already exists."}), 409

    try:
        password_hash = generate_password_hash(password)
        user_data = UserData(None, username, password_hash, email)
        new_user = create_user(user_data)

        access_token = create_access_token(identity=new_user.id)
        return jsonify(access_token=access_token, message="User created successfully!"), 201

    except IntegrityError:
        db.rollback()
        return jsonify({"message": "Error creating user due to data integrity issue (e.g., duplicate email/username)."}), 400
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"An unexpected error occurred: {str(e)}"}), 500


@auth.route("/change_password", methods=["POST"])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not current_password or not new_password or not confirm_password:
        return jsonify({"message": "All password fields are required."}), 400

    if new_password != confirm_password:
        return jsonify({"message": "New passwords do not match."}), 400

    db = next(get_db()) #
    user = get_user_by_id(current_user_id, db=db)

    if user is None:
        return jsonify({"message": "User not found."}), 404

    if check_password_hash(user.password, current_password):
        new_password_hash = generate_password_hash(new_password)
        user.password = new_password_hash
        db.commit()
        return jsonify({"message": "Password changed successfully!"}), 200
    else:
        return jsonify({"message": "Invalid current password."}), 401


@auth.route("/reset_password_request", methods=["POST"])
def reset_password_request():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"message": "Username is required."}), 400

    db = next(get_db())
    user = get_user(username, db=db)

    if user is not None:
        reset_token = secrets.token_urlsafe(32)
        expiration_date = datetime.now() + timedelta(hours=1)

        user.reset_token = reset_token
        user.expiration_date = expiration_date
        db.commit()

        user_email = user.email

        if user_email:
            # Aquí deberías integrar Flask-Mail para enviar el correo.
            # Asegúrate de configurar Flask-Mail en src/__init__.py y src/config.py
            # send_reset_password_email(current_app._get_current_object(), user_email, username, reset_token)
            print(f"DEBUG: Email de restablecimiento simulado enviado a {user_email} con token: {reset_token}")
            print(f"DEBUG: Enlace de restablecimiento para frontend: http://localhost:4200/reset-password/{reset_token}")
            return jsonify({"message": "An email has been sent with instructions to reset your password."}), 200
        else:
            return jsonify({"message": "The user does not have a registered email."}), 400
    else:
        return jsonify({"message": "The user does not exist."}), 404

# Opcional: Función para enviar el correo (requiere Flask-Mail configurado)
# def send_reset_password_email(app, user_email, username, reset_token):
#     try:
#         mail = app.extensions.get("mail")
#         msg = Message(
#             "Reset Password",
#             sender=app.config["MAIL_USERNAME"],
#             recipients=[user_email],
#         )
#         # El enlace debe apuntar a la ruta de Angular para el restablecimiento de contraseña
#         reset_url = f"http://localhost:4200/reset-password/{reset_token}" # URL de tu frontend Angular
#         msg.body = f"Hello {username}, click on the following link to reset your password: {reset_url}"
#         mail.send(msg)
#     except Exception as e:
#         print(f"Error sending the email: {e}")


@auth.route("/reset_password_confirm", methods=["POST"])
def reset_password_confirm():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not token or not new_password or not confirm_password:
        return jsonify({"message": "Token, new password, and confirmation are required."}), 400

    if new_password != confirm_password:
        return jsonify({"message": "New passwords do not match."}), 400

    db = next(get_db())
    user = db.query(User).filter(User.reset_token == token).first()

    if user is not None:
        expiration_date = user.expiration_date
        if expiration_date and expiration_date.replace(tzinfo=None) > datetime.now():
            new_password_hash = generate_password_hash(new_password)
            user.password = new_password_hash
            user.reset_token = None
            user.expiration_date = None
            db.commit()
            return jsonify({"message": "Password changed successfully!"}), 200
        else:
            return jsonify({"message": "The reset token has expired."}), 400
    else:
        return jsonify({"message": "Invalid or expired reset token."}), 404


@auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully."}), 200