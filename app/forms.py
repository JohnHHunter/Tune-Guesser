from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import player, game_room


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Submit')


class RoomForm(FlaskForm):
    name = StringField('Room Name', validators=[DataRequired()])
    category = SelectField('Artist', coerce=str, validators=[DataRequired()])
    private = BooleanField('Make Room Private ?')
    submit = SubmitField('Submit')

    def validate_name(self, name):
        room = game_room.query.filter_by(name=name.data).first()
        if room is not None:
            raise ValidationError('Please use a different name')


class JoinByCodeForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired()])
    submit = SubmitField('Join Room By Code')

    def validate_code(self, code):
        room = game_room.query.filter_by(code=code.data).first()
        if room is None:
            raise ValidationError('Game is not found')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = player.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = player.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
