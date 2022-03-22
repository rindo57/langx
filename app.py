import email
import os
import sys
from turtle import title
from flask import Flask, request, abort, jsonify, render_template, url_for, flash, redirect
from flask_cors import CORS
import traceback
from forms import LoginForm, RegistrationForm
from models import AppUser, setup_db, SampleLocation, db_drop_and_create_all, db
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    """ comment out at the first time running the app """
    # db_drop_and_create_all()
    
    app.config['SECRET_KEY']= 'b7c43167f2d15b477ae15d333596ceb4'
    
    # hashing the user's password
    bcrypt = Bcrypt(app)
    
    # class required to enable registered app users to log in
    login_manager = LoginManager(app)
    login_manager.init_app(app)

    # Function that reloads the user from the user id stored in the session
    @login_manager.user_loader
    def load_user(user_id):
        return AppUser.query.get(int(user_id))


    @app.route("/")
    @app.route("/home")
    def home():
        return render_template('home.html', title='Home')

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = AppUser.query.filter_by(email==form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful - Please check your email and password', 'danger')
        return render_template('login.html', title='Login', form=form)
    
    @app.route("/register", methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            # create the app user instance
            user = AppUser(firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)
            # add the app user to the database
            db.session.add(user)
            # commit the change - now the user can log in
            db.session.commit() 
            flash(f'Account created - Welcome to the community {form.firstname.data} {form.lastname.data}!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

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

    