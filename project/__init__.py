from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
import os


###
# General feedback
#
# * Make sure you have a readme that tells me something about your app and how
# get it setup and run locally.
#
# * Do not commit .pyc files.  You should have a .gitignore that ignores .pyc
# and the __pycache__ folder
#
# * I would think over the UI flow a little more.  I find it hard to figure out
# how to get where I want to go.  Maybe have a nav with all the page types that
# I can get to.
#
# * The routes inside of user seem not RESTful.  Since it's a many to many between
# users and preferences you probably don't need a nested route.
#
####

app = Flask(__name__)
modus = Modus(app)

if os.environ.get('ENV') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

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
