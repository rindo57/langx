from random import choices
from flask_wtf import FlaskForm
#from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import AppUser

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
    street = StringField('Street Name', validators=[DataRequired()])
    house = IntegerField('House Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    options=['12 available options:', 'French', 'Spanish', 'English', 'Portuguese', 'Chinese', 'German','Khoisan', 'Korean', 'Swahili', 'Japanese', 'Russian', 'Arabic']
    options.sort()
    fluent_languages = SelectMultipleField('Select your native and fluent language(s)', validators=[DataRequired()], choices=options)
    other_languages = SelectMultipleField('Select the language(s) you want to learn', validators=[DataRequired()], choices=options)
    interests = TextAreaField('Describe your Interests and ideal language exchange partner', validators=[DataRequired(), Length(max=300)])
    submit = SubmitField('Confirm Registration')

    def validate_email(self, email):
        app_user = AppUser.query.filter_by(email=email.data).first()
        if app_user:
            raise ValidationError('This email is taken, please select a different one.')

""" Form to Update user profile Info(names, pic, languages and Interests) """   
class UpdateProfileForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=10)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=10)]) 
    options=['12 available options:', 'French', 'Spanish', 'English', 'Portuguese', 'Chinese', 'German','Khoisan', 'Korean', 'Swahili', 'Japanese', 'Russian', 'Arabic']
    options.sort()
    fluent_languages = SelectMultipleField('Your native and fluent language(s)', validators=[DataRequired()], choices=options)
    other_languages = SelectMultipleField('Language(s) you want to learn', validators=[DataRequired()], choices=options)
    interests = TextAreaField('Describe your Interests and ideal language exchange partner', validators=[DataRequired(), Length(max=300)])
    picture = FileField('Select a different profile picture',  validators=[FileAllowed(['jpg', 'AVIF'])])
    submit = SubmitField('Update')






