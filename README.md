
# Podcasts4u 

### About


This [web app](https://a-pod-a-day.herokuapp.com/) recommends podcasts to users based on their interests. Interest categories include 1) Arts 2) Culture 3) Technology 4) Sports and Recreation 5) Politics and many others. 

Users can choose as many interest categories as they please from a simple checkbox form. For each interest category that the user chooses, 10 of the best podcasts of that category are suggested to the user. 'Best podcasts' are determined by the highest ranked podcasts according to the official Itunes API which has more than 250,000 free podcasts.

Each podcast is displayed with a description, a 'save' button and a link to redirect the user  to that podcast's profile on the official Apple iTunes library which provides more information such as listener reviews and average rating.

Users can also save recommended podcasts to their profile for later review. Users may update their interests at anytime and receive new appropriate suggestions.

Once a user signs in, and before the user fills out the interests form, the user is recommended 3 of the top rated podcasts from the official Apple iTunes library. This was implemented to cater for users who might be new to podcasts and unsure what interest categories suit them. If these podcasts do not interest you, the user can then fill out the 'preferences' checkbox form to receive appropriate suggestions.

### Getting started

Please follow these instructions to get a local copy of this project on your machine.

### Requirements

All required dependencies for this app are listed in the file named 'requirements.txt'

### Installing

1. Make a virtual environment: ```mkvirtualenv <NAME>```.
2. Create a local PostgresSQL database for this project ``` createdb name-of-database```
3. Install the app requirements: ```pip install -r requirements.txt```
4. Upgrade your database ```python manage.py db upgrade```.


### Built with

This project was built with the following tools and technologies: 

1. The Apple iTunes API
2. Python
3. Flask
4. Flask-Login
5. Flask-Modus
6. Flask-Bcrypt
7. Flask-Migrate
8. Flask-SQLAlchemy
9. SQL Alchemy
10. Jinja2
11. JavaScript



