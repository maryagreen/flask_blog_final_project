from flask_blog import app
from flask import render_template, redirect, flash, url_for, session, abort, request
from blog.form import SetupForm, PostForm, CommentForm
from flask_blog import db, uploaded_images
from author.models import Author
from blog.models import Blog, Category, Post, Comment
from author.decorators import login_required, author_required
import bcrypt
from slugify import slugify
POSTS_PER_PAGE=8
@app.route('/')

@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
#    blog = Blog.query.first()
#    if not blog:
#        return redirect(url_for('setup'))
#    posts=Post.query.filter_by(live=True).order_by(Post.publish_date.desc()).paginate(page, POSTS_PER_PAGE, False)
#    return render_template('blog/index.html', blog=blog, posts=posts)  
#
#@app.route('/mainindex')
#def mainindex():
    blogs = Blog.query.all()
    if blogs:
       return render_template('blog/mainindex.html', blogs=blogs) 
    else:
        return redirect(url_for('setup'))
    
@app.route('/blogindex/<int:id>')
@app.route('/blogindex/<int:id>/<int:page>')
def blogindex(id, page=1):
    blog = Blog.query.filter_by(id=id).first()
    #blog = Blog.query.filter(Blog.id==id).first()
    if not blog:
        return redirect(url_for('setup'))
    posts=Post.query.filter(Post.blog_id==id, Post.live==True).order_by(Post.publish_date.desc()).paginate(page, POSTS_PER_PAGE, False)
    #posts=Post.query.filter(blog_id=id, live=True).order_by(Post.publish_date.desc()).paginate(page, POSTS_PER_PAGE, False)
    
    return render_template('blog/blogindex.html', blog=blog, posts=posts)
 
@app.route('/category/<int:id>')      
def category(id):
    category = Category.query.filter_by(id=id).first()
    if not category:
        return redirect(url_for('index'))
    posts = Post.query.filter(Post.category_id==id, Post.live==True).order_by(Post.author_id.asc(),Post.publish_date.desc()).all()
    if not posts:
       return redirect(url_for('index'))
    if len(posts) > 0:
        return render_template('blog/category.html', category=category, posts=posts)
    else:    
        return redirect(url_for('mainindex'))    
        
@app.route('/admin')
@app.route('/admin<int:page>')
def admin(page=1):
    if session.get('is_author'):
        author = Author.query.filter_by(username=session['username']).first()
        author_id = author.id
        posts = Post.query.filter_by(author_id=author.id).order_by(Post.publish_date.desc()).paginate(page, POSTS_PER_PAGE, False)
        return render_template('blog/admin.html', posts=posts)    
    else:
        abort(403)
    
@app.route('/setup', methods=('GET','POST'))    
def setup():
    form = SetupForm()
    error = ""
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(form.password.data, salt)
        image = request.files.get('image')
        filename = None
        try:
            print("Try filename")
            filename = uploaded_images.save(image)
            print("File Name: ", filename)
        except:
            flash("The image was not uploaded.")
        author = Author(
            form.fullname.data,
            form.email.data,
            form.username.data,
            hashed_password,
            True,
            form.bio.data,
            filename
            )
        db.session.add(author)
        db.session.flush()
        if author.id:
            blog = Blog(
                form.name.data,
                author.id)
            db.session.add(blog)    
            db.session.flush()
        else:
            db.session.rollback()
            error = "Error creating user"
        if author.id and blog.id:
            db.session.commit()
            flash("Blog created")
            return redirect(url_for('index'))
        else:
            db.session.rollback()
            error = "Error creating blog"
    return render_template('blog/setup.html', form=form, error=error, action= "new")
    
@app.route('/post', methods=('GET', 'POST'))
@author_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        image = request.files.get('image')
        filename = None
        print("image: ", image)
        try:
            filename = uploaded_images.save(image)
            print("filename: ", filename)
        except:
            flash("The image was not uploaded.")
        if form.new_category.data:
            new_category = Category(form.new_category.data)
            db.session.add(new_category)
            db.session.flush()
            category = new_category
        #elif form.category.data:
        #    category_id = form.category.get_pk(form.category.data)
        #    category = Category.query.filter_by(id=category_id).first()
        else:
            category = form.category.data    
            #category = None
        #blog = Blog.query.first()
        author = Author.query.filter_by(username=session['username']).first()
        author_id = author.id
        blog = Blog.query.filter_by(admin=author_id).first()
        title = form.title.data
        body = form.body.data
        slug = slugify(title)
        post = Post(blog, author, title, body, category, filename, slug)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('article', slug=slug))
    return render_template('blog/post.html', form=form, action="new")
    
@app.route('/article/<slug>')    
def article(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if session.get('username') is None:
        username = ''
    else:
        username = session['username']
    return render_template('/blog/article.html', post=post, username=username)
    
@app.route('/delete/<int:post_id>')    
@author_required
def delete(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    post.live = False
    db.session.commit()
    flash("Article deleted")
    return redirect('/admin')
    
@app.route('/edit/<int:post_id>', methods=('GET','POST'))
@author_required
def edit(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    form = PostForm(obj=post)
    if form.validate_on_submit():
        original_image = post.image
        form.populate_obj(post)
        if form.image.has_file():
            image = request.files.get('image')
            try:
                filename = uploaded_images.save(image)
            except:
                flash("The image was not uploaded")
            if filename:
                post.image = filename
        else:
            post.image = original_image
        if form.new_category.data:
            new_category = Category(form.new_category.data)
            db.session.add(new_category)
            db.session.flush()
            post.category = new_category
        db.session.commit()
        return redirect(url_for('article', slug=post.slug))
    return render_template('/blog/post.html', form=form, post=post, action="edit")
    
@app.route('/bio/<int:author_id>')    
def bio(author_id):
    author = Author.query.filter_by(id=author_id).first()
    return render_template('/blog/bio.html', author=author)
    
@app.route('/getblogforauthor/<int:author_id>')    
def getblogforauthor(author_id):
    blog=Blog.query.filter_by(admin = author_id).first()
    id=blog.id
    if blog:
       return redirect(url_for('blogindex',id=id) )
    else:
        return redirect(url_for('mainindex'))

@app.route('/comment/<int:post_id>', methods=('POST','GET')) 
@login_required
def comment(post_id):
    if request.method == "POST":
        form = CommentForm(request.form)
        if form.validate_on_submit():
            comment = Comment(
            post_id,
            session['username'],
            form.body.data)
            db.session.add(comment)
            db.session.flush()
            db.session.commit()
            if comment.id:
                return " Success! Comment added"
            else:
                return "Insert failed."
        else:
            print("not valid")
            print(form.body)
            return "failed validation"
    else:        
        post=Post.query.filter_by(id = post_id).first()
        form = CommentForm()
        if post:
            #return render_template('/blog/comment.html', form=form, post=post, username=username, action="new")
            return render_template('/blog/comment.html', form=form, post=post, action="new")
        else:
            return "Post not found"
    
    return "exit comment function"    
            