from project import db, bcrypt
from flask_login import UserMixin
from project.preferences.models import Preference

UserPreference = db.Table('user_preferences',
                          db.Column('id', db.Integer, primary_key=True),
                          db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade')),
                          db.Column('preference_id', db.Integer, db.ForeignKey('preferences.id', ondelete='cascade')))


class User(db.Model, UserMixin):
  __tablename__ ='users'

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.Text, unique=True)
  email = db.Column(db.Text, unique=True)
  password=db.Column(db.Text)
  preferences = db.relationship("Preference", secondary=UserPreference, backref=db.backref('user'))
  playlist = db.Column(db.Text)
  playlist_titles =db.Column(db.Text)

  def __init__(self,username,email,password):
    self.username = username
    self.email = email
    self.password = bcrypt.generate_password_hash(password).decode('UTF-8')

  def setpassword(self):
    self.password = bcrypt.generate_password_hash(password).decode('UTF-8')

  def __repr__(self):
    return "#{}- Username: {}".format(self.id,self.username)

