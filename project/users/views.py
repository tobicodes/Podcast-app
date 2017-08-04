import random
import requests
from flask import redirect, render_template, request, url_for, Blueprint, flash, jsonify
from project.users.models import User, Preference, UserPreference, Podcast
from project.users.forms import SignupForm, LoginForm, EditUserForm, NewPreferenceForm, EditUserName
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

# @users_blueprint.route('/', methods=['GET'])  
# def index():
#   return render_template('users/index.html', user=current_user, podcasts_to_render=podcasts_to_render)

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
      return redirect(url_for('users.show', id=new_user.id))
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
          return redirect(url_for('users.show',id=current_user.id))
        else:
          flash({ 'text': "Wrong password, please try again.", 'status': 'danger'})
      else:
        flash({'text': "Invalid username. Please try again", 'status': 'danger'})
      return render_template('users/login.html', form=form)
  return render_template('users/login.html', form=form)

@users_blueprint.route('/logout')
def logout():
  logout_user()
  flash({ 'text': "You have successfully logged out.", 'status': 'success' })
  return redirect(url_for('root'))


######################### EDITING USERNAMES and USER PASSWORD #####################

################## FOR PASSWORDS ################
@users_blueprint.route('/<int:id>/edit')
@login_required
@ensure_correct_user
def edit(id):
  return render_template('users/edit.html', form=EditUserForm(), user=User.query.get(id))

@users_blueprint.route('/<int:id>', methods=['GET','PATCH', 'DELETE'])
@login_required
@ensure_correct_user
def show(id):
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

######### GET Request to show route ###############
  result = requests.get('https://itunes.apple.com/us/rss/toppodcasts/genre=26/json')
  pod_results = result.json()['feed']['entry']
  pod_objects = []
  number_of_pods_to_display = 3
  
  for result in pod_results:
    pod_objects.append(result)

  podcast_list=[]
  for podcast in pod_objects:
    pod = {}
    pod['Title'] = podcast['im:name']['label']
    pod['Summary'] = podcast['summary']['label']
    pod['Podcast_URL']=podcast['link']['attributes']['href']
    pod['Picture_URL']=podcast['im:image'][2]['label']
    pod['Category']=podcast['category']['attributes']['label']
    pod['itunes_id'] = int(podcast['id']['attributes']['im:id'])
    podcast_list.append(pod)
  
  truncate_length = 45

  for podcast in podcast_list:
    podcast['split_up'] = podcast['Summary'].split()
    podcast['shortened_arr'] = []
    podcast['truncated_summary'] = ""
    if len(podcast['split_up']) < truncate_length:
      podcast['truncated_summary'] = podcast['Summary']
    else: 
      for x in range(0,truncate_length):
        podcast['shortened_arr'].append(podcast['split_up'][x])
        podcast['truncated_summary'] = " ".join(podcast['shortened_arr'])+ "..."

  max_char_length = 200
  for podcast in podcast_list:
    podcast['summary_split_chars']=list(podcast['Summary'])
    podcast['chars_split'] = []
    podcast['display_summary'] =""
    if len(podcast['summary_split_chars']) < max_char_length:
      podcast['display_summary']=podcast['Summary']
    else:
      for x in range(0, max_char_length-1):
       podcast['chars_split'].append(podcast['summary_split_chars'][x])
       podcast['display_summary'] = "".join(podcast['chars_split'])+ "..."

  for pod in podcast_list:
    podcast_already_in_table = Podcast.query.filter_by(itunes_id = pod['itunes_id']).first()
    if podcast_already_in_table == None:
      new_pod = Podcast(
      title=pod['Title'],
      podcast_url=pod['Podcast_URL'],
      picture_url=pod['Picture_URL'],
      summary=pod['Summary'],
      category=pod['Category'],
      truncated_summary=pod['truncated_summary'],
      itunes_id=pod['itunes_id'],
      display_summary=pod['display_summary'])
      current_user.podcasts.append(new_pod)
    else:
      current_user.podcasts.append(podcast_already_in_table)
  db.session.add(current_user)
  db.session.commit()

  podcasts_to_render=random.sample(current_user.podcasts.all(),number_of_pods_to_display)

  return render_template('users/show.html', user=current_user, podcasts_to_render=podcasts_to_render)
  

################# FOR USERNAMES ###############

@users_blueprint.route('/<int:id>/edit-username')
@login_required
@ensure_correct_user
def edit_username(id):
  form = EditUserName()
  form.current_username = current_user.username
  return render_template('users/edit-username.html', form=form)

@users_blueprint.route('/<int:id>/show-username', methods=['GET', 'PATCH'])
@login_required
@ensure_correct_user
def show_username(id):
  if request.method == b'PATCH':
    form = EditUserName(request.form)
    if form.validate_on_submit():
      current_user.username = request.form['new_username']
      db.session.add(current_user)
      db.session.commit()
      flash("Successfully updated your username!")
      return redirect(url_for('users.show'))
    else:
      flash("Oops something went wrong. Please try again with at least 6 characters")
      return render_template('users/edit-username.html', form=form)


################## FUNCTIONALITY FOR USERS TO ADD PREFERENCES ###############


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
  return render_template('users/show.html', form=form)

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
  user =User.query.get(id)
  form = NewPreferenceForm(obj=user)
  form.set_choices()
  return render_template('users/edit_preferences.html', form = form, id=current_user.id)


@users_blueprint.route('/<int:id>/preferences/show', methods=['GET','PATCH', 'DELETE'])
@login_required
@ensure_correct_user
def show_preferences(id):
  form = NewPreferenceForm()
  form.set_choices()
  if request.method ==b'PATCH':

    for preference in form.preference.data:
      current_user.preferences.append(Preference.query.get(preference))

    db.session.add(current_user)
    db.session.commit()

    # current_user.preferences = request.form['preferences']
    # db.session.add(current_user)
    # db.session.commit()
    return redirect(url_for('users.request_data',id=current_user.id))
  return render_template('preferences/show.html', id=current_user.id)


# if request.method=='POST':
#     for preference in form.preference.data:
#       current_user.preferences.append(Preference.query.get(preference))
    

################# ROUTE FOR HANDLING REQUESTS TO ITUNES API ################
pref_map = {'Arts':1301, 'Food':1306, 'Literature':1401, 'Design':1402, 'Performing Arts':1405, 'Visual Arts': 1406, 'Fashion & Beauty':1459, 'Comedy':1303, 'Education':1304, 'K-12':1415, 
            'Higher Education':1416, 'Educational Technology': 1468, 'Language Courses': 1469,'Training':1470, 'Kids & Family': 1305, 'Health':1307, 'Fitness & Nutritition': 1417, 'Self-Help':1420,
            'Sexuality':1421, 'Alternative Health': 1481, 'TV % Film': 1309, 'Music': 1310, 'News & Politics': 1311, 'Religion & Spirituality': 1314, 'Buddhism': 1438, 'Christianity':1439, 'Islam': 1440,
            'Judaism': 1441, 'Spirituality': 1444, 'Hinduism': 1463, 'Other': 1464, 'Science & Medicine': 1315, 'Natural Sciences': 1477, 'Medicine': 1478, 'Social Sciences': 1479, 'Sports & Recreation': 1316,
            'Outdoor': 1456, 'Professional': 1465, 'College & High School': 1466, 'Amateur':1467, 'Technology':1318, 'Gadgets':1446, 'Tech News':1448, 'Podcasting': 1450, 'Software How-To':1480, 'Business':1321,
            'Careers':1410, 'Investing': 1412, 'Management & Marketing':1413, 'Business News':1471, 'Shopping':1472, 'Games & Hobbies':1323, 'Video Games': 1404, 'Automotive':1454, 'Aviation':1455, 'Hobbies':1460,
            'Other Games':1461, 'Society & Culture':1324, 'Personal Journals':1302, "Places & Travels":1320, 'Philopsphy':1443, "History":1462, 'Government & Organizations':1325, 'National':1473, 'Regional': 1474,
            "Local": 1475, "Non-Profit": 1476}

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

  podcast_data = []
  for item in playlist:
    pod = {}
    pod['Title'] = item['im:name']['label']
    pod['Summary'] = item['summary']['label']
    pod['Podcast_URL']=item['link']['attributes']['href']
    pod['Picture_URL']=item['im:image'][2]['label']
    pod['Category']=item['category']['attributes']['label']
    pod['itunes_id'] = int(item['id']['attributes']['im:id'])
    podcast_data.append(pod)


############ TRUNCATING SUMMARY TEXT ############################
  truncate_length = 45

  for podcast in podcast_data:
    podcast['split_up'] = podcast['Summary'].split()
    podcast['shortened_arr'] = []
    podcast['truncated_summary'] = ""
    if len(podcast['split_up']) < truncate_length:
      podcast['truncated_summary'] = podcast['Summary']
    else: 
      for x in range(0,truncate_length):
        podcast['shortened_arr'].append(podcast['split_up'][x])
        podcast['truncated_summary'] = " ".join(podcast['shortened_arr'])+ "..."

  ############### Truncating to display based on length of characters ##########
  max_char_length = 200
  for podcast in podcast_data:
    podcast['summary_split_chars']=list(podcast['Summary'])
    podcast['chars_split'] = []
    podcast['display_summary'] =""

    if len(podcast['summary_split_chars']) < max_char_length:
      podcast['display_summary']=podcast['Summary']
    else:
      for x in range(0, max_char_length-1):
       podcast['chars_split'].append(podcast['summary_split_chars'][x])
       podcast['display_summary'] = "".join(podcast['chars_split'])+ "..."
  
################# CREATING INSTANCES of PODCAST class to be placed as property on each current user ############# 
  
  for pod in podcast_data:
    podcast_already_in_table = Podcast.query.filter_by(itunes_id = pod['itunes_id']).first()
    if podcast_already_in_table == None:
      new_pod = Podcast(
      title=pod['Title'],
      podcast_url=pod['Podcast_URL'],
      picture_url=pod['Picture_URL'],
      summary=pod['Summary'],
      category=pod['Category'],
      truncated_summary=pod['truncated_summary'],
      itunes_id=pod['itunes_id'],
      display_summary=pod['display_summary'])
      current_user.podcasts.append(new_pod)
    else:
      current_user.podcasts.append(podcast_already_in_table)
  db.session.add(current_user)
  db.session.commit()

  number_of_pods_to_render = 12
  if len(current_user.podcasts.all()) < number_of_pods_to_render:
    podcasts_to_render= current_user.podcasts.all()
  else:
    podcasts_to_render = random.sample(current_user.podcasts.all(),number_of_pods_to_render)

  
  more_podcasts = [podcast for podcast in podcast_data if x not in podcasts_to_render]
  from IPython import embed; embed()
  
  return render_template('users/recommendations.html',podcasts_to_render=podcasts_to_render, more_podcasts=more_podcasts)

############## ADDING FUNCTIONALITY FOR LIKING PODCASTS ########
@users_blueprint.route('/liked/<int:podcast_id>', methods=['POST'])
@login_required
def like_pod(podcast_id):
  podcast=Podcast.query.get(podcast_id)
  current_user.liked_podcasts.append(podcast)
  db.session.add(current_user)
  db.session.commit()
  return "done"
  # redirect(url_for('users.request_data',id=current_user.id))

@users_blueprint.route('/liked-podcasts', methods=['GET'])
@login_required
def liked_podcasts():
  all_liked_podcasts = current_user.liked_podcasts
  return render_template('users/liked_podcasts.html',all_liked_podcasts=all_liked_podcasts)






  # titles = [item['im:name']['label']for item in playlist]
  # summaries = [item['summary']['label']for item in playlist]
  # podcast_URL = [item['link']['attributes']['href']for item in playlist]
  # picture_URL = [item['im:image'][2]['label']for item in playlist]
  
  
   
  