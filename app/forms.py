from flask_wtf import FlaskForm  # type: ignore
from wtforms.fields import (  # type: ignore
    StringField,
    PasswordField,
    SubmitField,
    EmailField,
)
from wtforms.validators import DataRequired, EqualTo, Email  # type: ignore


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()],
        render_kw={"autocomplete": "off", "id": "username_login"},
    )
    password = PasswordField(
        "Password", validators=[DataRequired()], render_kw={"id": "password_login"}
    )
    submit = SubmitField("Send", render_kw={"id": "submit_login"})


class TodoForm(FlaskForm):
    description = StringField(
        "Description",
        validators=[DataRequired()],
        render_kw={"autocomplete": "off", "id": "description_todo"},
    )
    submit = SubmitField("Create", render_kw={"id": "submit_todo"})


class DeleteTodoForm(FlaskForm):
    submit = SubmitField("Delete", render_kw={"id": "submit_delete"})


class UpdateTodoForm(FlaskForm):
    submit = SubmitField("Check", render_kw={"id": "submit_update"})


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current password",
        validators=[DataRequired()],
        render_kw={"id": "current_password"},
    )
    new_password = PasswordField(
        "New password", validators=[DataRequired()], render_kw={"id": "new_password"}
    )
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match"),
        ],
        render_kw={"id": "confirm_password"},
    )
    submit = SubmitField("Change password", render_kw={"id": "submit_change_password"})


class ResetPasswordForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired()], render_kw={"id": "username_reset"}
    )
    submit = SubmitField("Reset password", render_kw={"id": "submit_reset_password"})


class SignupForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()],
        render_kw={"autocomplete": "off", "id": "username_signup"},
    )
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"autocomplete": "off", "id": "email_signup"},
    )
    password = PasswordField(
        "Password", validators=[DataRequired()], render_kw={"id": "password_signup"}
    )
    submit = SubmitField("Send", render_kw={"id": "submit_signup"})
