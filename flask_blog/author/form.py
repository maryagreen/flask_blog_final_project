from flask_wtf import Form
from wtforms import validators, StringField, PasswordField
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileField, FileAllowed

class RegisterForm(Form):
    fullname = StringField('Full Name',[validators.Required()])
    email = EmailField('Email', [validators.Required()])
    username = StringField('Username', [
        validators.Required(),
        validators.Length(min=4, max=25)
        ])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.length(min=4, max=80)
        ])    
    confirm = PasswordField('Repeat Password')
    bio = StringField('Bio')
    image = FileField('Image', validators=[
        FileAllowed(['jpg','png'], 'Images only!')
        ])
        
class LoginForm(Form):
    username = StringField('Username', [
        validators.Required(),
        validators.Length(min=4, max=25)
        ])
    password = PasswordField('Password', [
        validators.Required(),
        validators.length(min=4, max=80)
        ])    