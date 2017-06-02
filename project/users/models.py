from project import db, bcrypt
from flask_login import UserMixin
from project.preferences.models import Preference

UserPreference = db.Table('user_preferences',
                          db.Column('id', db.Integer, primary_key=True),
                          db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade')),
                          db.Column('preference_id', db.Integer, db.ForeignKey('preferences.id', ondelete='cascade')))

UserPodcast=db.Table('user_podcasts',
                          db.Column('id', db.Integer,primary_key=True),
                          db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade')),
                          db.Column('podcast_id', db.Integer, db.ForeignKey('podcasts.id', ondelete='cascade')))

LikedPodcasts = db.Table('liked_podcasts',
                          db.Column('id', db.Integer, primary_key= True),
                          db.Column('id_of_user_who_liked_podcast', db.Integer, db.ForeignKey('users.id', ondelete='cascade')),
                          db.Column('id_of_podcast_liked', db.Integer, db.ForeignKey('podcasts.id', ondelete='cascade')))

class User(db.Model, UserMixin):
  __tablename__ ='users'

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.Text, unique=True)
  email = db.Column(db.Text, unique=True)
  password=db.Column(db.Text)
  preferences = db.relationship("Preference", secondary=UserPreference, backref=db.backref('user'))
  podcasts = db.relationship("Podcast",secondary=UserPodcast, backref='user', lazy='dynamic')
  playlist = db.Column(db.Text)
  liked_podcasts=db.relationship('Podcast', secondary=LikedPodcasts, backref=db.backref('users', lazy='dynamic'),lazy='dynamic')


  ## Add a column to hold all podcasts for a user? And/or all liked podcasts? Need a through table and form/button for liking pods

  def __init__(self,username,email,password):
    self.username = username
    self.email = email
    self.password = bcrypt.generate_password_hash(password).decode('UTF-8')

  def setpassword(self):
    self.password = bcrypt.generate_password_hash(password).decode('UTF-8')

  def __repr__(self):
    return "#{}- Username: {}".format(self.id,self.username)

class Podcast(db.Model):
  __tablename__= "podcasts"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Text)
  category=db.Column(db.Text)
  podcast_url =db.Column(db.Text)
  picture_url= db.Column(db.Text)
  summary =db.Column(db.Text)
  display_summary=db.Column(db.Text)
  truncated_summary =db.Column(db.Text)
  itunes_id=db.Column(db.Integer)


  def __init__(self, title, category, podcast_url, picture_url, summary,truncated_summary,display_summary,itunes_id):
    self.title = title
    self.category=category
    self.podcast_url = podcast_url
    self.picture_url = picture_url
    self.summary = summary
    self.truncated_summary=truncated_summary
    self.display_summary=display_summary
    self.itunes_id=itunes_id

  def __repr__(self):
    return "Podcast name - {}".format(self.title)