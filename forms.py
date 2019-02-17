from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Regexp, ValidationError, Email, Length, EqualTo
from models import User

def name_exists(form, field):       # Funkcija za provjeru istog usernamea
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists!')

def email_exists(form, field):       # Funkcija za provjeru istog emaila
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists!')

class RegisterFrom(Form):
    username = StringField(
        'Username', validators=[DataRequired(),     # Prvi argument je Label, drugi je lista validatora
                                Regexp(r'^[a-zA-Z0-9_]+$', message="Username should be one word"),
                                name_exists]
    )

    email = StringField(
        'Email', validators=[DataRequired(),
                             Email(),
                             email_exists]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(),
                                Length(min=2),
                                EqualTo('password2', message='Passwords must match!')]
    )
    password2 = PasswordField(
        'Confirm Password', validators=[DataRequired()]
    )

class LoginForm(Form):          # Validacija ce se odvijati u viewu
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class PostForm(Form):
    content = TextAreaField("Nesto novo?", validators=[DataRequired()])
