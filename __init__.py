from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_recaptcha import ReCaptcha
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["MAIL_SERVER"] = os.getenv('MAIL_SERVER')
app.config["MAIL_PORT"] = os.getenv('MAIL_PORT')
app.config["MAIL_USE_SSL"] = os.getenv('MAIL_USE_SSL')
app.config["MAIL_USERNAME"] = os.getenv('MAIL_USER')
app.config["MAIL_PASSWORD"] = os.getenv('MAIL_PASS')

db = SQLAlchemy(app)
mail = Mail(app)
bcrypt = Bcrypt(app)

recaptcha = ReCaptcha()
recaptcha.is_enabled = True
recaptcha.site_key = os.getenv('ALAMBI_RECAPTCHA_PUBLIC')
recaptcha.secret_key = os.getenv('ALAMBI_RECAPTCHA_SECRET')
recaptcha.theme = 'light'
recaptcha.type = 'image'
recaptcha.size = 'normal'
recaptcha.tabindex = 0
recaptcha.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

from alambi.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.template_filter('autoversion')
def autoversion_filter(filename):
    path = 'alambi/' + filename[1:]

    try:
        timestamp = str(os.path.getmtime(path))
    except OSError:
        return filename

    newfile = "{0}?v={1}".format(filename, timestamp)
    print(newfile)
    return newfile


from alambi.main.routes import main
from alambi.users.routes import users
from alambi.admin.routes import admin
from alambi.errors.routes import errors

app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(admin)
app.register_blueprint(errors)

