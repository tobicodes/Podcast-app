### create form for signup, log in and create preference(drop down select)

from flask_wtf import FlaskForm, Form
from wtforms import PasswordField, TextField, StringField,IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, Length, EqualTo
from project.preferences.models import Preference 

class SignupForm(FlaskForm):
  username = StringField('username', validators=[DataRequired()])
  email = StringField('email', validators=[DataRequired(), Email()])
  password = PasswordField('password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
  username = StringField('username', validators=[DataRequired()])
  password = PasswordField('password', validators=[Length(min=6)])

class EditUserForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    current_password=PasswordField('current password', validators=[DataRequired()])
    new_password = PasswordField('new password', validators =[DataRequired(), EqualTo('confirm_new_password', message='Passwords must match')])
    confirm_new_password = PasswordField('confirm password')

class EditUserName(FlaskForm):
  current_username = StringField('current username', validators=[DataRequired()])
  new_username = StringField('new username', validators=[DataRequired(), Length(min=4)])


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class NewPreferenceForm(FlaskForm):
  preference = MultiCheckboxField('Preference',coerce=int)

  def __repr__(self):
    return "This is a multicheckbox field"
## Add validators - at least one box must be selected, if not flash a message

  def set_choices(self):
    self.preference.choices = [(d.id, d.content) for d in Preference.query.all()]


