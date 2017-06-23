from flask_blog import app
from flask_blog import db, uploaded_images
from flask import render_template, redirect, url_for, session, request, flash
from author.form import RegisterForm, LoginForm
from author.models import Author
from author.decorators import login_required
import bcrypt
#import pdb

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    error = None
    
    if request.method == 'GET' and request.args.get('next'):
        session['next'] = request.args.get('next', None)
        
    if form.validate_on_submit():
        author = Author.query.filter_by(
            username=form.username.data
            ).first()
        if author:
            if bcrypt.hashpw(form.password.data, author.password) == author.password:
                session['username'] = form.username.data
                session['is_author'] = author.is_author
                flash("User %s logged in" % form.username.data)
                if 'next' in session:
                    next = session.get('next')
                    session.pop('next')
                    return redirect(next)
                else:    
                    return redirect(url_for('index'))
            else:
                error = "Incorrect username or password"                    
        else:
            error = "Incorrect username or password"
    return render_template('author/login.html', form=form, error=error)
    
@app.route('/register', methods=('GET', 'POST'))    
def register():
    form = RegisterForm()
    error = ""
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(form.password.data, salt)
        author = Author(
            form.fullname.data,
            form.email.data,
            form.username.data,
            hashed_password,
            False
            )
            
        db.session.add(author)
        db.session.flush()
        db.session.commit()
        return redirect(url_for('success'))
    return render_template('author/register.html', form=form, action="new")

@app.route('/success/<string:msg>')      
@app.route('/success')    
def success(msg):
    if msg > '':
        return msg
    else:
        return "Success!"
    
@app.route('/resetpassword', methods=('GET', 'POST'))  
#@login_required
def resetpassword():
    form = RegisterForm()
    error = ""
    if form.validate_on_submit():
        author = Author.query.filter_by(
            username=form.username.data
            ).first()
        if author:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(form.password.data, salt)
            author.password = hashed_password
            setattr(author, 'password', hashed_password)
            db.session.commit()
            return redirect(url_for('success', msg="Password Reset"))
    return render_template('author/register.html', form=form,  action="reset") 
            
    
    
@app.route('/editbio', methods=('GET', 'POST'))  
@login_required
def editbio():
    form = RegisterForm()
    error = ""
    message = ""
    datachanged = 0
    #pdb.set_trace()
    if form.validate_on_submit():
        if session['username'] == form.username:
            author = Author.query.filter_by(
                username=form.username.data
                ).first()
            if author:
                newbio = form.bio.data
                image = request.files.get('image')
                filename = None
                try:
                    filename = uploaded_images.save(image)
                    setattr(author, 'image', filename)
                    datachanged = 1
                except:
                    flash("The image was not uploaded.")
                    print("The image was not uploaded.")
                if newbio > ' ':
                    setattr(author, 'bio', newbio)
                    datachanged = 1
                if datachanged == 1:
                    db.session.commit()
                    return redirect(url_for('success', msg="Author updated"))
            else:
                #This will never execute, because you must be logged in to use this function,
                # and if you have a login, you are in the author table, even if is_author is false.
                return "You must be an author to edit your bio."
        else:  
            return "You may only edit your own information."
           # return url_for('index')
    else:            
        #username=session['username']
        #author = Author.query.filter_by(username=session['username']).first()
        #form.fullname = author.fullname
        #form.email = author.email
        #form.username = author.username
        #form.password = author.password
        #form.confirm = author.password
        #form.bio = author.bio
        #form.image = author.image
        return render_template('author/register.html', form=form,  action="edit")    
    
@app.route('/logout')    
def logout():
    session.pop('username')
    session.pop('is_author')
    flash("User logged out")
    return redirect(url_for('index'))