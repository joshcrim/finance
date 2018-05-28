from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from finance.auth.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])

    payday = DateField('Date of Next Payday', format='%m/%d/%Y', validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user is not None:
            raise ValidationError('Please use a different username.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
