import os
import sys
import secrets
from PIL import Image
from flask import Flask, request, abort, jsonify, render_template, url_for, flash, redirect
from flask_cors import CORS
import traceback
from forms import LoginForm, RegistrationForm, UpdateProfileForm, NewLocationForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models import mongo, AppUser, SampleLocation, SpatialConstants
# import jyserver.Flask as jsf  - This import enables access to the HTML DOM

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    
    # Set up MongoDB connection
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb+srv://720pp:fire@cluster0.ser1dtu.mongodb.net/?retryWrites=true&w=majority')
    mongo.init_app(app)
    
    CORS(app)
    app.config['SECRET_KEY'] = '66cb9ba6becd134af4b68a05fddf19aa'
    
    # Hashing the user's password
    bcrypt = Bcrypt(app)
    
    # Required to enable registered app users to log in
    login_manager = LoginManager(app)
    login_manager.init_app(app)

    # Login required decorator settings
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'warning'

    # Function that reloads the user from the user id stored in the session
    @login_manager.user_loader
    def load_user(user_id):
        user = mongo.db.app_users.find_one({"_id": ObjectId(user_id)})
        return AppUser.from_mongo(user) if user else None

    @app.route("/")
    @app.route("/home")
    def home():
        return render_template('home.html')

    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            # Create the app user instance
            app_user = AppUser(
                firstname=form.firstname.data,
                lastname=form.lastname.data,
                lookup_address=form.lookup_address.data,
                fluent_languages=', '.join(form.fluent_languages.data),
                other_languages=', '.join(form.other_languages.data),
                email=form.email.data,
                password=hashed_password,
                interests=form.interests.data,
                geom=SpatialConstants.point_representation(form.coord_latitude.data, form.coord_longitude.data)
            )
            # Insert user into MongoDB
            mongo.db.app_users.insert_one(app_user.to_dict())
            flash(f'Account created - Welcome to the community {form.firstname.data} {form.lastname.data}!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form, 
                               map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!'))

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('profile'))
        form = LoginForm()
        if form.validate_on_submit():
            app_user = mongo.db.app_users.find_one({"email": form.email.data})
            if app_user and bcrypt.check_password_hash(app_user['password'], form.password.data):
                login_user(AppUser.from_mongo(app_user), remember=form.remember_user.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('profile'))
            else:
                flash('Login unsuccessful, please check your email and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route("/profile", methods=['GET', 'POST'])
    @login_required
    def profile():
        profile = current_user
        if request.args.get('id'):
            user_id = request.args.get('id')
            user = mongo.db.app_users.find_one({"_id": ObjectId(user_id)})
            profile = AppUser.from_mongo(user) if user else None
        profile_pic = url_for('static', filename='profile_pics/' + profile.profile_pic)
        return render_template('profile.html', title='Profile', profile_pic=profile_pic, 
                               profile=profile, map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!'))

    @app.route("/news", methods=['GET'])
    @login_required
    def news():
        return render_template('news.html', title='Top News')

    def save_picture(form_picture):
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_filename = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
        
        output_size = (400, 400)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
        return picture_filename

    @app.route("/edit_profile", methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        form = UpdateProfileForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.profile_pic = picture_file

            current_user.firstname = form.firstname.data
            current_user.lastname = form.lastname.data
            current_user.fluent_languages = ', '.join(form.fluent_languages.data)
            current_user.other_languages = ', '.join(form.other_languages.data)
            current_user.interests = form.interests.data
            current_user.lookup_address = form.lookup_address.data
            current_user.coord_latitude = form.coord_latitude.data
            current_user.coord_longitude = form.coord_longitude.data

            mongo.db.app_users.update_one({'_id': ObjectId(current_user.id)}, {'$set': current_user.to_dict()})
            flash('Your profile has been updated', 'success')
            return redirect(url_for('profile'))

        elif request.method == 'GET':
            form.firstname.data = current_user.firstname
            form.lastname.data = current_user.lastname
            form.interests.data = current_user.interests
            form.lookup_address.data = current_user.lookup_address
            form.fluent_languages.data = current_user.fluent_languages
            form.other_languages.data = current_user.other_languages

        profile_pic = url_for('static', filename='profile_pics/' + current_user.profile_pic)
        return render_template('edit_profile.html', title='Edit Profile', profile_pic=profile_pic, form=form,
                               map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!'))

    @app.route("/new-location", methods=['GET', 'POST'])
    def new_location():
        form = NewLocationForm()
        if form.validate_on_submit():            
            latitude = float(form.coord_latitude.data)
            longitude = float(form.coord_longitude.data)
            description = form.description.data

            location = SampleLocation(description=description, latitude=latitude, longitude=longitude)   
            location.insert()

            flash(f'New location created!', 'success')
            return redirect(url_for('news'))

        return render_template('new_location.html', form=form, 
                               map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!'), title='New Location')

    @app.route("/api/store_item")
    def store_item():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            description = request.args.get('description')

            location = SampleLocation(description=description, latitude=latitude, longitude=longitude)   
            location.insert()

            return jsonify({"success": True, "location": location.to_dict()}), 200
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

            locations = AppUser.get_items_within_radius(latitude, longitude, radius)
            return jsonify({"success": True, "results": locations}), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"success": False, "error": 500, "message": "server error"}), 500

    return app


app = create_app()
if __name__ == '__main__':
 
    app.run(host='0.0.0.0', port=8084, debug=True)
