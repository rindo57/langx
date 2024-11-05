from random import choices
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, PasswordField, SubmitField, \
    BooleanField, TextAreaField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import AppUser  # Assuming you have the AppUser model connected to MongoDB

""" Form to Log In """
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # This field allows users to remain logged in after a period under a secure cookie
    remember_user = BooleanField('Remember Me')
    submit = SubmitField('Login')

""" Form to Register"""
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=10)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=5, max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    options = ['12 available options:', 'French', 'Spanish', 'English', 'Portuguese', 'Chinese', 'German',
               'Khoisan', 'Korean', 'Swahili', 'Japanese', 'Russian', 'Arabic']
    options.sort()

    fluent_languages = SelectMultipleField('Select your native and fluent language(s)', validators=[DataRequired()], choices=options)
    other_languages = SelectMultipleField('Select the language(s) you want to learn', validators=[DataRequired()], choices=options)
    interests = TextAreaField('Describe your Interests and ideal language exchange partner', validators=[DataRequired(), Length(max=300)])
    lookup_address = StringField('Search for your Street name and House number')
    coord_latitude = HiddenField('Latitude', validators=[DataRequired()])
    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])
    submit = SubmitField('Confirm Registration')

    def validate_email(self, email):
        # Since we're now using MongoDB, we need to use MongoDB's query method
        app_user = AppUser.query.filter_by(email=email.data).first()
        if app_user:
            raise ValidationError('This email is taken, please select a different one.')

""" Form to Update user profile Info """   
class UpdateProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=10)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=10)])
    
    options = ['12 available options:', 'French', 'Spanish', 'English', 'Portuguese', 'Chinese', 'German',
               'Khoisan', 'Korean', 'Swahili', 'Japanese', 'Russian', 'Arabic']
    options.sort()

    fluent_languages = SelectMultipleField('Your native and fluent language(s)', validators=[DataRequired()], choices=options)
    other_languages = SelectMultipleField('Language(s) you want to learn', validators=[DataRequired()], choices=options)
    interests = TextAreaField('Describe your Interests and ideal language exchange partner', validators=[DataRequired(), Length(max=300)])
    picture = FileField('Upload profile picture',  validators=[FileAllowed(['jpg', 'jpeg', 'png', 'AVIF'])])
    lookup_address = StringField('Update your Street name and House number')
    coord_latitude = HiddenField('Latitude', validators=[DataRequired()])
    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])
    submit = SubmitField('Update')

class NewLocationForm(FlaskForm):
    description = StringField('Location description', validators=[DataRequired(), Length(min=1, max=80)])
    lookup_address = StringField('Search address')
    coord_latitude = HiddenField('Latitude', validators=[DataRequired()])
    coord_longitude = HiddenField('Longitude', validators=[DataRequired()])
    submit = SubmitField('Create Location')
