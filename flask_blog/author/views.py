from flask_blog import app
from flask_blog import db, uploaded_images
from flask import render_template, redirect, url_for, session, request, flash
from author.form import RegisterForm, LoginForm
from author.models import Author
from author.decorators import login_required
import bcrypt

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
    
@app.route('/success')    
def success():
    return "Author registered!"
    
@app.route('/resetpassword', methods=('GET', 'POST'))    
def resetpassword():
    #This doesn't work. It tries to insert instead of update.
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
        #db.session.query(author).filter_by( author.username==form.username.data).update({'password':hashed_password])
            #conn = engine.connect()
            stmt = Author.update().\
            values(password = hashed_password).\
            where(Author.username == form.username.data)
            db.session.execute(stmt)

            db.session.commit()
            return redirect(url_for('success'))
    return render_template('author/register.html', form=form,  action="edit") 
    
@app.route('/logout')    
def logout():
    session.pop('username')
    session.pop('is_author')
    flash("User logged out")
    return redirect(url_for('index'))