from flask import redirect, render_template, request, url_for, Blueprint, flash
from project.users.models import User, Preference, UserPreference
from project.users.forms import NewPreferenceForm
from project import db, bcrypt
from functools import wraps
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from sqlalchemy.exc import IntegrityError


### have only the edit and delete preferences routes here..

preferences_blueprint = Blueprint(
  'preferences',
  __name__,
  template_folder = 'templates'
)

def ensure_correct_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if kwargs.get('id') != current_user.id:
            flash({'text': "Not Authorized", 'sus': 'danger'})
            return redirect(url_for('root'))
        return fn(*args, **kwargs)
    return wrapper

# @preferences_blueprint.route('/', methods=["GET", 'PATCH', 'DELETE'])
# @login_required
# @ensure_correct_user
# def show(id):
#   if request.method ==b'PATCH':
#     pass
#   if request.method ==b'DELETE':
#     pass
#   return render_template('preferences/show.html')


