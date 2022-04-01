import os
import secrets
from turtle import title
from PIL import Image
import sys
import tkinter as tk
from flask import Flask, request, abort, jsonify, render_template, url_for, flash, redirect
from flask_cors import CORS
# import jyserver.Flask as jsf  - This import enables HTML DOM
import traceback
from forms import LoginForm, RegistrationForm, UpdateProfileForm
from models import setup_db, SampleLocation, db_drop_and_create_all,db, AppUser
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_login import login_user, current_user, logout_user, login_required


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    """ comment out at the first time running the app """
    #db_drop_and_create_all()
    app.config['SECRET_KEY']= '66cb9ba6becd134af4b68a05fddf19aa'
    
    # hashing the user's password
    bcrypt = Bcrypt(app)
    
    # Required to enable registered app users to log in
    login_manager = LoginManager(app)
    login_manager.init_app(app)

    # Further to the login_required decorator, this sets/sends the user to the route required
    # before accessing the desired page which in this case is the 'profile page' for a user that
    # hasn't logged in yet
    login_manager.login_view = 'login'

    # Flash alert for the login required message as - 'Please log in to access this page'
    login_manager.login_message_category = 'warning'

    # Function that reloads the user from the user id stored in the session
    @login_manager.user_loader
    def load_user(user_id):
        return AppUser.query.get(int(user_id))


    @app.route("/")
    @app.route("/home")
    def home():
        #print('Home route running')
        return render_template('home.html')
    
    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            # create the app user instance
            app_user = AppUser(firstname=form.firstname.data, lastname=form.lastname.data, street=form.street.data, 
            house=form.house.data, fluent_languages=form.fluent_languages.data, other_languages=form.other_languages.data, 
            email=form.email.data, password=hashed_password, interests=form.interests.data)
            # add the app user to the database
            #print(app_user)
            db.session.add(app_user)
            # commit the change - now the user can log in
            db.session.commit() 
            flash(f'Account created - Welcome to the community {form.firstname.data} {form.lastname.data}!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        #print("Login info", flush=True)
        if current_user.is_authenticated:
            return redirect(url_for('news'))
        form = LoginForm()
        if form.validate_on_submit():
            #print('form validated')
            app_user = AppUser.query.filter_by(email=form.email.data).first()
            # checking if credentials used exist in the db
            #print(app_user)
            if app_user and bcrypt.check_password_hash(app_user.password, form.password.data):
                print("There's a password match")
                login_user(app_user, remember=form.remember_user.data)
                '''The aim here is to access the query paramater(next?%profile) after login if it exists
                Initially when trying to access the profile page without logging in the user was redirected
                to the log in page and the flash message appeared as - 'Please log in to access this page'
                however after logging in the user is still redirected to the home page and not the 
                profile page(which the user wanted to access beforehand) so to avoid this we include the below 
                next_page code which will redirect the user to the page they were trying to access after logging 
                in instead of the home page'''
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                #print('Failed flash message - auth failed')
                flash('Login unsuccessful, please check your email and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route("/profile", methods=['GET', 'POST'])
    # The app user has to be logged in to access this profile page
    @login_required
    def profile():
        profile_pic = url_for('static', filename='profile_pics/' + current_user.profile_pic)
        return render_template('profile.html', title='Profile', profile_pic = profile_pic)

    @app.route("/news", methods=['GET', 'POST'])
    @login_required
    def news():
        return render_template('news.html', title='Top News')

        # Saving user's picture as a random HEX by importing secrets module
    def save_picture(form_picture):
        random_hex = secrets.token_hex(8)

        # Making sure the file is saved under the same extension it was uploaded in by importing os module
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_filename = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
        
        '''Resizing Images before saving the on the file py installing the Pillow package 
        and importing the image class from PIL. By doing this we save space and reduce the
        website/App loading time'''
        output_size = (400, 400)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
        return picture_filename

    @app.route("/edit_profile", methods=['GET', 'POST'])
    # The app user has to be logged in to access this edit_profile page
    @login_required
    def edit_profile():
        form = UpdateProfileForm()
        if form.validate_on_submit():
            # Saving user's picture
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.profile_pic = picture_file

            # Updates current user first and last names
            #print('Update form validated')
            current_user.firstname = form.firstname.data
            current_user.lastname = form.lastname.data
            current_user.fluent_languages = form.fluent_languages.data
            current_user.other_languages = form.other_languages.data
            current_user.interests = form.interests.data
            db.session.commit()
            flash('Your profile has been updated', 'success')
            return redirect(url_for('profile'))

        # Populating the UpdateProfileForm with the current user's details(names) when it validates on submit
        elif request.method =='GET':
            form.firstname.data = current_user.firstname
            form.lastname.data = current_user.lastname
        profile_pic = url_for('static', filename='profile_pics/' + current_user.profile_pic)
        return render_template('edit_profile.html', title='Edit Profile', profile_pic=profile_pic, form=form)


    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for('home'))
    
    @app.route('/map', methods=['GET'])
    def location():
        return render_template(
            'map.html', 
            map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!'), title='Map'
        )

    @app.route("/api/store_item")
    def store_item():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            description = request.args.get('description')

            location = SampleLocation(
                description=description,
                geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude)
            )   
            location.insert()

            return jsonify(
                {
                    "success": True,
                    "location": location.to_dict()
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.route("/api/get_items_in_radius")
    def get_items_in_radius():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            radius = int(request.args.get('radius'))
            
            locations = SampleLocation.get_items_within_radius(latitude, longitude, radius)
            return jsonify(
                {
                    "success": True,
                    "results": locations
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500

    return app

app = create_app()
if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host='127.0.0.1',port=port,debug=True)

    