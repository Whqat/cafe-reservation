from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from decouple import config
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_mail import Mail

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
app.secret_key = config('SECRET_KEY')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping':True}
app.config['SECURITY_PASSWORD_SALT'] = config("SECURITY_PASSWORD_SALT", default="very-important")
app.config['MAIL_DEFAULT_SENDER'] = "digflup@gmail.com"
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = False
app.config['MAIL_USERNAME'] = config("EMAIL_USER")
app.config['MAIL_PASSWORD'] = config("EMAIL_PASSWORD")
app.config["TESTING"] = False
app.config["MAIL_SUPPRESS_SEND"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)


from cafe import routes

