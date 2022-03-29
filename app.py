import os
import sys
import tkinter as tk
from flask import Flask, request, abort, jsonify, render_template, url_for, flash, redirect
from flask_cors import CORS
import traceback
from forms import LoginForm, RegistrationForm
from models import setup_db, SampleLocation, db_drop_and_create_all,db, AppUser
from flask_bcrypt import Bcrypt, bcrypt
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

    # Flash alert for the login required message
    login_manager.login_message_category = 'warning'

    # Function that reloads the user from the user id stored in the session
    @login_manager.user_loader
    def load_user(user_id):
        return AppUser.query.get(int(user_id))


    @app.route("/")
    @app.route("/home")
    def home():
        print('Home route running')
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
            print(app_user)
            db.session.add(app_user)
            # commit the change - now the user can log in
            db.session.commit() 
            flash(f'Account created - Welcome to the community {form.firstname.data} {form.lastname.data}!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        print("Login info", flush=True)
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            print('form validated')
            app_user = AppUser.query.filter_by(email=form.email.data).first()
            # checking if credentials used exist in the db
            print(app_user)
            if app_user and bcrypt.check_password_hash(app_user.password, form.password.data):
                print("There's a password match")
                login_user(app_user, remember=form.remember_user.data)
                # access the query paramater after login if it exists
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                print('Failed flash message - auth failed')
                flash('Login unsuccessful, please check your email and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route("/profile")
    # The app user has to be logged in to access this profile page
    @login_required
    def profile():
        profile_pic = url_for('static', filename='profile_pics/' + current_user.profile_pic)
        return render_template('profile.html', title='Profile', profile_pic = profile_pic)

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

    