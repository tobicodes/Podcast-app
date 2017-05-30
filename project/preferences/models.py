from project import db, bcrypt
from flask_login import UserMixin


class Preference(db.Model):
  __tablename__="preferences"

  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text)

  def __init__(self, content):
    self.content = content

  def __repr__(self):
    return str(self.content)