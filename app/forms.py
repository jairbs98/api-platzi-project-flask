from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'class': 'custom-input'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'class': 'custom-input'})
    submit = SubmitField('Send', render_kw={'class': 'custom-button'})



class TodoForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()], render_kw={"autocomplete": "off"})
    submit = SubmitField('Create')


class DeleteTodoForm(FlaskForm):
    submit = SubmitField('Delete')


class UpdateTodoForm(FlaskForm):
    submit = SubmitField('Check')
