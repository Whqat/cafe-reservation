from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, DateTimeField, DateField
from wtforms.validators import InputRequired, Email, Length

class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email(message="This email does not exist", check_deliverability=True)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Email(message="This email does not exist")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    submit = SubmitField("Login")

class ReserveForm(FlaskForm):
    date = DateField("Day for reservation", validators=[InputRequired()])
    time = StringField("Time for reservation", validators=[InputRequired()])
    submit = SubmitField("Reserve")