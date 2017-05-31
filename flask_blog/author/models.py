from flask_blog import db, uploaded_images

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80))
    email = db.Column(db.String(35), unique=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(60))
    is_author = db.Column(db.Boolean)
    bio = db.Column(db.String(256))
    image = db.Column(db.String(255))
    
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    blogs = db.relationship('Blog', backref='author', lazy='dynamic')

    @property
    def imgsrc(self):
        return uploaded_images.url(self.image)
        
    def __init__(self, fullname, email, username, password, is_author=False, bio=None, image=None):
        self.fullname = fullname
        self.email = email
        self.username = username
        self.password = password
        self.is_author = is_author
        self.bio = bio
        self.image = image
        
    def __repr__(self):
        return '<Author %r>' % self.username