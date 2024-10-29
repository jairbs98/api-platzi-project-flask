import secrets
from datetime import datetime, timedelta

from flask import render_template, redirect, flash, url_for, current_app  # type: ignore
from flask_login import (  # type: ignore
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore

from app.forms import (
    LoginForm,
    ChangePasswordForm,
    ResetPasswordForm,
    SignupForm,  # Import SignupForm
)  # Import ChangePasswordForm


from . import auth
from app.firestore_service import get_user, user_put
from app.models import UserModel, UserData


@auth.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    context = {"login_form": LoginForm()}

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data

        user_doc = get_user(username)

        if user_doc.to_dict() is not None:
            password_from_db = user_doc.to_dict()["password"]

            # Verify the password using check_password_hash
            if check_password_hash(password_from_db, password):
                user_data = UserData(username, password, None)
                user = UserModel(user_data)

                login_user(user)

                flash("Welcome back.")

                return redirect(url_for("hello"))  # Corrected: return redirect(...)
            else:
                flash("The information does not match.")
        else:
            flash("The user does not exist.")

        return redirect(url_for("index"))

    return render_template("login.html", **context)


@auth.route("/signup", methods=["GET", "POST"])  # Corrected: /signup
def signup():
    signup_form = SignupForm()  # Use SignupForm
    context = {"signup_form": signup_form}

    if signup_form.validate_on_submit():
        username = signup_form.username.data
        password = signup_form.password.data
        email = signup_form.email.data  # Get the email

        user_doc = get_user(username)

        if user_doc.to_dict() is None:
            password_hash = generate_password_hash(password)
            user_data = UserData(username, password_hash, email)  # Pass the email
            user_put(user_data)

            user = UserModel(user_data)

            login_user(user)

            flash("Welcome!")

            return redirect(url_for("hello"))
        else:
            flash("The user exists!")

    return render_template("signup.html", **context)


@auth.route("/change_password", methods=["GET", "POST"])  # New route
@login_required
def change_password():
    change_password_form = ChangePasswordForm()
    context = {"change_password_form": change_password_form}

    if change_password_form.validate_on_submit():
        current_password = change_password_form.current_password.data
        new_password = change_password_form.new_password.data

        user_doc = get_user(current_user.id)
        password_from_db = user_doc.to_dict()["password"]

        if check_password_hash(password_from_db, current_password):
            new_password_hash = generate_password_hash(new_password)
            user_doc.reference.update({"password": new_password_hash})
            flash("Password changed successfully!")
            return redirect(url_for("hello"))
        else:
            flash("Invalid current password.")

    return render_template("change_password.html", **context)


@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    reset_password_form = ResetPasswordForm()
    if reset_password_form.validate_on_submit():
        username = reset_password_form.username.data

        user_doc = get_user(username)

        if user_doc.to_dict() is not None:
            # Generate a reset token
            reset_token = secrets.token_urlsafe(32)
            # Set the token expiration date (e.g., 1 hour)
            expiration_date = datetime.now() + timedelta(hours=1)
            user_doc.reference.update(
                {"reset_token": reset_token, "expiration_date": expiration_date}
            )

            # Get the user's email
            user_email = user_doc.to_dict().get("email")

            if user_email:
                # Send an email to the user with the reset link
                send_reset_password_email(
                    current_app._get_current_object(),
                    user_email,
                    username,
                    reset_token,  # Pass the application as an argument
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
    reset_password_form = ChangePasswordForm()  # Reuse ChangePasswordForm
    context = {"reset_password_form": reset_password_form}

    if reset_password_form.validate_on_submit():
        new_password = reset_password_form.new_password.data

        # Search for the user with the reset token
        users_ref = db.collection("users")
        query = users_ref.where("reset_token", "==", token)
        for user_doc in query.stream():  # Corrected: iterate over the query results
            # Check if the token has expired
            expiration_date = user_doc.to_dict().get("expiration_date")
            if (
                expiration_date
                and expiration_date.replace(tzinfo=None) > datetime.now()
            ):
                # Encrypt the new password
                new_password_hash = generate_password_hash(new_password)
                # Update the password in Firestore
                user_doc.reference.update(
                    {
                        "password": new_password_hash,
                        "reset_token": None,
                        "expiration_date": None,
                    }
                )
                flash("Password changed successfully!")
                return redirect(url_for("auth.login"))
            else:
                flash("The reset token has expired.")
                return redirect(
                    url_for("auth.login")
                )  # Redirect to login if the token has expired
            break  # Exit the loop after processing the first document
        else:
            flash("Invalid reset token.")

    return render_template("reset_password_with_token.html", **context)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Come back soon.")

    return redirect(url_for("auth.login"))  # Corrected: auth.login
