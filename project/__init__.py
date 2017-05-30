from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
import os


app = Flask(__name__)
modus = Modus(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/podcast'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'shhhh'

db = SQLAlchemy(app)
bcrypt =Bcrypt(app)
login_manager = LoginManager(app)

# import a blueprint that we will create
from project.users.views import users_blueprint
from project.preferences.views import preferences_blueprint
from project.users.models import User

# register our blueprints with the application
app.register_blueprint(users_blueprint, url_prefix='/users')
app.register_blueprint(preferences_blueprint, url_prefix='/users/<int:id>/preferences')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def root():
    return render_template('home.html')
