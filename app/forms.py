from flask_wtf import FlaskForm  # type: ignore
from wtforms.fields import StringField, PasswordField, SubmitField, EmailField  # type: ignore  # Agregar EmailField
from wtforms.validators import DataRequired, EqualTo, Email  # type: ignore  # Agregar Email


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()],
        render_kw={"class": "custom-input", "autocomplete": "off"},
    )
    password = PasswordField(
        "Password", validators=[DataRequired()], render_kw={"class": "custom-input"}
    )
    submit = SubmitField("Send", render_kw={"class": "custom-button"})


class TodoForm(FlaskForm):
    description = StringField(
        "Description", validators=[DataRequired()], render_kw={"autocomplete": "off"}
    )
    submit = SubmitField("Create")


class DeleteTodoForm(FlaskForm):
    submit = SubmitField("Delete")


class UpdateTodoForm(FlaskForm):
    submit = SubmitField("Check")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current password", validators=[DataRequired()])
    new_password = PasswordField("New password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Change password")


class ResetPasswordForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Reset password")


class SignupForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()],
        render_kw={"class": "custom-input", "autocomplete": "off"},
    )
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"class": "custom-input", "autocomplete": "off"},
    )
    password = PasswordField(
        "Password", validators=[DataRequired()], render_kw={"class": "custom-input"}
    )
    submit = SubmitField("Send", render_kw={"class": "custom-button"})
