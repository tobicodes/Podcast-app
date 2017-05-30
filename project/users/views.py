from flask import redirect, render_template, request, url_for, Blueprint, flash
from project.users.models import User, Preference, UserPreference
from project.users.forms import SignupForm, LoginForm, EditUserForm, NewPreferenceForm
from project import db, bcrypt
from functools import wraps
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from sqlalchemy.exc import IntegrityError



users_blueprint = Blueprint(
  'users',
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

@users_blueprint.route('/', methods=['GET'])  
def index():
  user = current_user
  return render_template('users/index.html', user=user)

########################### SIGN UP ############################

@users_blueprint.route('/signup', methods=["GET", "POST"])
def signup():
  form = SignupForm()
  if request.method == "POST":
    if form.validate():
      try:
        new_user = User(
          username=form.username.data,
          email=form.email.data,
          password=form.password.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
      except IntegrityError as e:
        flash({'text': "Username already taken", 'status': 'danger'})
        return render_template('users/signup.html', form=form)
      return redirect(url_for('users.preferences', id=new_user.id))
  return render_template('users/signup.html', form=form)

########################### LOG IN and LOG OUT ############################
@users_blueprint.route('/login', methods=["GET", "POST"])
def login():
  form=LoginForm()
  if request.method =='POST':
    if form.validate():
      found_user = User.query.filter_by(username = form.username.data).first()
      if found_user:
        is_authenticated = bcrypt.check_password_hash(found_user.password, form.password.data)
        if is_authenticated:
          login_user(found_user)
          flash({'text': "Hello, {}!".format(found_user.username), 'status': 'success'})
          return redirect(url_for('users.index'))
        else:
          flash("Invalid password")
      else:
        flash({'text': "Invalid credentials.", 'status': 'danger'})
      return render_template('users/login.html', form=form)
  return render_template('users/login.html', form=form)

@users_blueprint.route('/logout')
def logout():
  logout_user()
  flash({ 'text': "You have successfully logged out.", 'status': 'success' })
  return redirect(url_for('root'))


######################### EDITING USER PASSWORD #####################
@users_blueprint.route('/<int:id>/edit')
@login_required
@ensure_correct_user
def edit(id):
  return render_template('users/edit.html', form=EditUserForm(), user=User.query.get(id))



####################### SHOW, PATCH, DELETE USERS ###################
@users_blueprint.route('/<int:id>/show', methods=['GET','PATCH', 'DELETE'])
@login_required
@ensure_correct_user
def show(id):
############ EDITING PASSWORDS #####
  if request.method == b'PATCH':
    form =EditUserForm()
    if bcrypt.check_password_hash(current_user.password, request.form['current_password']):  ##check whether the hashed password is the same as the generated hash for the supplied password in form
      if form.validate_on_submit():
        current_user.setpassword(request.form['new_password'])
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('users.show', id=current_user.id))
    else:
      flash("That password is incorrect. Please try again")
      return redirect(url_for('users.edit',form=form))
####### DELETING USERS #####
  if request.method == b'DELETE':
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    return redirect('home.html')
  return render_template('users/show.html', user=current_user)


################## FORM FOR USERS TO ADD PREFERENCES


@users_blueprint.route('/<int:id>/preferences', methods=['GET','POST'])
@login_required
@ensure_correct_user
def preferences(id):
  form = NewPreferenceForm(request.form)
  form.set_choices()
  if request.method=='POST':
    for preference in form.preference.data:
      current_user.preferences.append(Preference.query.get(preference))
    db.session.add(current_user)
    db.session.commit()
    return redirect(url_for('preferences.show', id=current_user.id))
  return render_template('users/index.html', form=form)

@users_blueprint.route('/<int:id>/preference/new', methods=['GET'])
@login_required
@ensure_correct_user
def new_preferences(id):
  form = NewPreferenceForm()
  form.set_choices()
  return render_template('preferences/new.html', form=form)



