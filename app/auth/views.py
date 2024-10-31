from mailbox import Message
import secrets
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError  # type: ignore # Importa IntegrityError

from flask import (  # type: ignore
    render_template,
    redirect,
    flash,
    url_for,
    current_app,
)
from flask_login import (  # type: ignore
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import (  # type: ignore
    generate_password_hash,
    check_password_hash,
)

from app.forms import (
    LoginForm,
    ChangePasswordForm,
    ResetPasswordForm,
    SignupForm,
)

from . import auth
from app.crud import create_user
from app.models import (
    UserModel,
    UserData,
    User,
    get_user,
)
from app.database import get_db


@auth.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    context = {"login_form": LoginForm()}
    db = next(get_db())

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data

        user = get_user(username, db=db)

        if user is not None:
            password_from_db = user.password

            # Verifica la contraseña usando check_password_hash
            if check_password_hash(password_from_db, password):
                # Crea una instancia de UserData con los datos del usuario
                user_data = UserData(username, password, user.email)
                user_model = UserModel(user_data)

                login_user(user_model)

                flash("Welcome back.")

                return redirect(url_for("hello"))
            else:
                flash("The information does not match.")
        else:
            flash("The user does not exist.")

        return redirect(url_for("index"))

    return render_template("login.html", **context)


@auth.route("/signup", methods=["GET", "POST"])  # Corrected: /signup
def signup():
    signup_form = SignupForm()
    context = {"signup_form": signup_form}
    db = next(get_db())  # Obtén la sesión de la base de datos aquí

    if signup_form.validate_on_submit():
        username = signup_form.username.data
        password = signup_form.password.data
        email = signup_form.email.data

        existing_user = get_user(username, db=db)  # Verifica si el usuario ya existe

        if existing_user is None:
            try:
                password_hash = generate_password_hash(password)
                user_data = UserData(username, password_hash, email)
                create_user(user_data)  # Usa create_user

                user = UserModel(user_data)

                login_user(user)

                flash("Welcome!")

                return redirect(url_for("hello"))
            except IntegrityError:
                db.rollback()  # Revierte la transacción en caso de error
                flash("A user with that email already exists.")
        else:
            flash("The user exists!")

    return render_template("signup.html", **context)


@auth.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    change_password_form = ChangePasswordForm()
    context = {"change_password_form": change_password_form}
    db = next(get_db())

    if change_password_form.validate_on_submit():
        current_password = change_password_form.current_password.data
        new_password = change_password_form.new_password.data

        user = get_user(current_user.id, db=db)

        if user is not None and check_password_hash(user.password, current_password):
            new_password_hash = generate_password_hash(new_password)

            print(f"Contraseña actual (hash): {user.password}")
            print(f"Nueva contraseña (hash): {new_password_hash}")

            user.password = new_password_hash
            print(f"Contraseña actualizada (hash): {user.password}")

            db.commit()
            db.refresh(user)

            flash("Password changed successfully!")
            return redirect(url_for("hello"))
        else:
            flash("Invalid current password.")

    return render_template("change_password.html", **context)


@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    reset_password_form = ResetPasswordForm()
    db = next(get_db())  # Obtén la sesión de la base de datos

    if reset_password_form.validate_on_submit():
        username = reset_password_form.username.data

        user = get_user(username, db=db)  # Obtiene el objeto User y pasa la sesión

        if user is not None:
            # Genera un token de restablecimiento
            reset_token = secrets.token_urlsafe(32)
            # Establece la fecha de expiración del token (por ejemplo, 1 hora)
            expiration_date = datetime.now() + timedelta(hours=1)

            # Actualiza el token y la fecha de expiración en la base de datos
            user.reset_token = reset_token
            user.expiration_date = expiration_date
            db.commit()

            # Obtiene el correo electrónico del usuario
            user_email = user.email

            if user_email:
                # Envía un correo electrónico al usuario con el enlace de restablecimiento
                send_reset_password_email(
                    current_app._get_current_object(),
                    user_email,
                    username,
                    reset_token,  # Pasa la aplicación como argumento
                )
                flash(
                    "An email has been sent with instructions to reset your password."
                )
                return redirect(url_for("auth.login"))
            else:
                flash("The user does not have a registered email.")
        else:
            flash("The user does not exist.")

    return render_template(
        "reset_password.html", reset_password_form=reset_password_form
    )


def send_reset_password_email(
    app, user_email, username, reset_token
):  # Add app as an argument
    """Sends an email with the link to reset the password."""
    try:
        # Get the Flask-Mail instance
        mail = app.extensions.get("mail")  # Use app.extensions.get('mail')

        # Create the message
        msg = Message(
            "Reset Password",
            sender=app.config["MAIL_USERNAME"],  # Use the email configured in the app
            recipients=[user_email],
        )
        # Build the URL with the token
        reset_url = url_for(
            "auth.reset_password_with_token", token=reset_token, _external=True
        )
        msg.body = f"Hello {username}, click on the following link to reset your password: {reset_url}"

        # Send the email
        mail.send(msg)

    except Exception as e:
        print(f"Error sending the email: {e}")
        flash("Error sending the email. Please try again later.")


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_with_token(token):
    reset_password_form = ChangePasswordForm()  # Reusa ChangePasswordForm
    context = {"reset_password_form": reset_password_form}

    if reset_password_form.validate_on_submit():
        new_password = reset_password_form.new_password.data

        # Busca al usuario con el token de restablecimiento
        db = next(get_db())
        user = db.query(User).filter(User.reset_token == token).first()

        if user is not None:
            # Verifica si el token ha expirado
            expiration_date = user.expiration_date
            if (
                expiration_date
                and expiration_date.replace(tzinfo=None) > datetime.now()
            ):
                # Encripta la nueva contraseña
                new_password_hash = generate_password_hash(new_password)

                # Actualiza la contraseña en la base de datos
                user.password = new_password_hash
                user.reset_token = None
                user.expiration_date = None
                db.commit()

                flash("Password changed successfully!")
                return redirect(url_for("auth.login"))
            else:
                flash("The reset token has expired.")
                return redirect(url_for("auth.login"))
        else:
            flash("Invalid reset token.")

    return render_template("reset_password_with_token.html", **context)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Come back soon.")

    return redirect(url_for("auth.login"))  # Corrected: auth.login
