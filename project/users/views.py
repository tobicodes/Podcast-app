import random
import requests
from flask import redirect, render_template, request, url_for, Blueprint, flash, jsonify
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
    return redirect(url_for('users.request_data', id=current_user.id))
  return render_template('users/index.html', form=form)

@users_blueprint.route('/<int:id>/preference/new', methods=['GET'])
@login_required
@ensure_correct_user
def new_preferences(id):
  form = NewPreferenceForm()
  form.set_choices()
  return render_template('preferences/new.html', form=form)

####################### EDIT and DELETE PREFERENCES ##############
@users_blueprint.route('/<int:id>/preferences/edit', methods=['GET'])
@login_required
@ensure_correct_user
def edit_preferences(id):
  form = NewPreferenceForm(request.form)
  form.set_choices()
  return render_template('users/edit_preferences.html', form = form, id=current_user.id)


@users_blueprint.route('/<int:id>/preferences/show', methods=['GET','PATCH', 'DELETE'])
@login_required
@ensure_correct_user
def show_preferences(id):
  form = NewPreferenceForm(request.form)
  form.set_choices()
  if request.method ==b'PATCH':
    current_user.preferences = form.preferences.data
    db.session.add(current_user)
    db.session.commit()
    return redirect(url_for('users.show_preferences',id=current_user.id))
  return render_template('preferences/show.html', id=current_user.id)


################# ROUTE FOR HANDLING REQUESTS TO ITUNES API ################
pref_map = {'Arts':1301, 'Food':1306, 'Literature':1401, 'Design':1402, 'Performing Arts':1405, 'Visual Arts': 1406, 'Fashion & Beauty':1459, 'Comedy':1303, 'Education':1304, 'K-12':1415, 
            'Higher Education':1416, 'Educational Technology': 1468, 'Language Courses': 1469,'Training':1470, 'Kids & Family': 1305, 'Health':1307, 'Fitness & Nutritition': 1417, 'Self-Help':1420,
            'Sexuality':1421, 'Alternative Health': 1481, 'TV % Film': 1309, 'Music': 1310, 'News & Politics': 1311, 'Religion & Spirituality': 1314, 'Buddhism': 1438, 'Christianity':1439, 'Islam': 1440,
            'Judaism': 1441, 'Spirituality': 1444, 'Hinduism': 1463, 'Other': 1464, 'Science & Medicine': 1315, 'Natural Sciences': 1477, 'Medicine': 1478, 'Social Sciences': 1479, 'Sports & Recreation': 1316,
            'Outdoor': 1456, 'Professional': 1465, 'College & High School': 1466, 'Amateur':1467, 'Technology':1318, 'Gadgets':1446, 'Tech News':1448, 'Podcasting': 1450, 'Software How-To':1480, 'Business':1321,
            'Careers':1410, 'Investing': 1412, 'Management & Marketing':1413, 'Business News':1471, 'Shopping':1472, 'Games & Hobbies':1323, 'Video Games': 1404, 'Automotive':1454, 'Aviation':1455, 'Hobbies':1460,
            'Other Games':1461, 'Society & Culture':1324, 'Personal Journals':1302, "Places & Travels":1320, 'Philopsphy':1443, "History":1462, 'Government & Organizations':1325, 'National':1473, 'Regional': 1474,
            "Local": 1475, "Non-Profit": 1476}

## id's should be strings so convert to string when making query string
## other refers to other religions 


@users_blueprint.route('/<int:id>/recommendations/', methods=['GET'])
@login_required
@ensure_correct_user
def request_data(id):
  map_ids = [pref_map[p.content] for p in current_user.preferences]

  playlist = []
  for map_id in map_ids:
    result = requests.get("https://itunes.apple.com/us/rss/toppodcasts/genre={}/json".format(map_id))
    for entry in result.json()['feed']['entry']:
    
      playlist.append(entry)

  ## Now we have N * 10 entries in playlist where N is number of preferences

  # titles = [item['im:name']['label']for item in playlist]
  # summaries = [item['summary']['label']for item in playlist]
  # podcast_URL = [item['link']['attributes']['href']for item in playlist]
  # picture_URL = [item['im:image'][2]['label']for item in playlist]

  podcast_data = []
  for item in playlist:
    obj = {}
    obj['Title'] = item['im:name']['label']
    obj['Summary'] = item['summary']['label']
    obj['Podcast_URL']=item['link']['attributes']['href']
    obj['Picture_URL']=item['im:image'][2]['label']
    obj['Category']=item['category']['attributes']['label']
    podcast_data.append(obj)
  

  podcasts_to_render = random.sample(podcast_data,10)
  
  more_podcasts = [x for x in podcast_data if x not in podcasts_to_render]

  return render_template('users/recommendations.html',podcasts_to_render=podcasts_to_render, more_podcasts=more_podcasts)

  

  
  
  
   
  # result = requests.get("https://itunes.apple.com/us/rss/toppodcasts/genre={}/json".format(pref_id))

  # Get Podcast name ===> result.json()['feed']['entry'][0]

  



## makes a query string and makes request to get all data for podcasts. 26 is the ID for podcasts on Itunes api endpoint

# res = requests.get('https://itunes.apple.com/WebObjects/MZStoreServices.woa/ws/genres', params={'id': 26})

  # res = requests.get('https://itunes.apple.com/WebObjects/MZStoreServices.woa/ws/genres')
  # all_pod_data = res.json()['26']

  # top_pod_url = all_pod_data['rssUrls']['topPodcasts']
  #  ## returns a URL that links to JSON object with data about current top podcasts 
  # all_data = res.json()
  # print(all_data)

  # subgenres = all_pod_data['subgenres'] ##16 elements in this object. Some of these have nested subgenres

  ## url for top_audio_podcasts 'https://itunes.apple.com/us/rss/topaudiopodcasts/genre=1301/json'















