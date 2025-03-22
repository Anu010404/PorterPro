from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, FloatField, BooleanField, IntegerField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError, Regexp
from models import Porter

def validate_name_words(form, field):
    words = field.data.split()
    if len(words) > 3:
        raise ValidationError('Name cannot contain more than 3 words')
    if any(len(word) > 20 for word in words):
        raise ValidationError('Each word in name must be less than 20 characters')

def validate_unique_badge_station(form, field):
    if Porter.query.filter_by(badge_number=field.data, station=form.station.data).first():
        raise ValidationError('This badge number is already registered for this station')

def validate_unique_name_station(form, field):
    if Porter.query.filter_by(name=field.data, station=form.station.data).first():
        raise ValidationError('A porter with this name already exists at this station')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('porter', 'Porter')], validators=[DataRequired()])

class BookingForm(FlaskForm):
    weight = FloatField('Total Weight (kg)', validators=[DataRequired(), NumberRange(min=1, max=100)])
    number_of_bags = IntegerField('Number of Bags', validators=[DataRequired(), NumberRange(min=1, max=10)])
    trolley_required = BooleanField('Trolley Required')
    meeting_point = StringField('Meeting Point at Station', validators=[DataRequired(), Length(max=200)])
    meeting_time = DateTimeField('Meeting Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')

class RatingForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment', validators=[Length(max=500)])

class PorterProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=3, max=100),
        validate_name_words,
        validate_unique_name_station
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message='Phone number must be exactly 10 digits')
    ])
    badge_number = StringField('Badge Number', validators=[
        DataRequired(),
        Length(max=20),
        validate_unique_badge_station
    ])
    station = StringField('Station', validators=[
        DataRequired(),
        Length(max=100)
    ])
    photo = FileField('Porter Photo', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])

class OTPVerificationForm(FlaskForm):
    otp = StringField('OTP', validators=[
        DataRequired(),
        Length(min=6, max=6, message='OTP must be 6 digits'),
        Regexp(r'^\d{6}$', message='OTP must contain only digits')
    ])