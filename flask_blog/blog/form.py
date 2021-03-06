from flask_wtf import Form
from wtforms import StringField, validators, PasswordField, TextAreaField, IntegerField, HiddenField
from author.form import RegisterForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from blog.models import Category
from flask_wtf.file import FileField, FileAllowed

class SetupForm(RegisterForm):
    name = StringField('Blog name', [
        validators.Required(),
        validators.Length(max=80)
        ])
    
def categories():    
    return Category.query
    
class PostForm(Form):
    image = FileField('Image', validators=[
        FileAllowed(['jpg','png'], 'Images only!')
        ])
    title = StringField('Title', [
        validators.Required(),
        validators.Length(max=80)
        ])
    body = TextAreaField('Content', validators=[validators.Required()])
    category = QuerySelectField('Category', query_factory=categories, allow_blank=True)
    new_category = StringField('New Category')
    
class CommentForm(Form):
    #post_id = HiddenField() 
    body = TextAreaField('Content', validators=[validators.Required()])
    