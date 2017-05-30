### create form for signup, log in and create preference(drop down select)

from flask_wtf import FlaskForm, Form
from wtforms import  StringField,IntegerField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length


# class NewPreference(FlaskForm):
#   language = SelectMultipleField(u'Categories', choices=[('tech', 'Technology'), ('news', 'World Affairs'), ('sports', 'Sports & Recreation'),('trump', 'Trump')])




