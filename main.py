import os
from flask import Flask, render_template
from flask import request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, EqualTo, Length
import mysql.connector
from create_tables import create_tables

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
# Get MySQL password from environment variable
mysql_password = os.environ.get('MYSQL_PASSWORD')
debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'


# Connect to MySQL database
db = mysql.connector.connect(
    host="blog-db.cqws3asie8ar.us-east-1.rds.amazonaws.com",
    user="svarshith7",
    password=mysql_password,
    # database="blog_db"
)

# Create database tables if not exists
create_tables(db)


# Define WTForms for signup, login, and comment
class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField(
        'Password', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[InputRequired(), EqualTo('password')])


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[InputRequired()])


class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[InputRequired()])


# Routes for signup, login, logout, and post creation
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Extract user data from the form
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data

        # Check if the email already exists in the database
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash('Email address already exists', 'error')
        else:
            # Insert the new user into the database
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO user (first_name, last_name, email, password) "
                "VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, password)
            )

            db.commit()
            cursor.close()

            flash('Account created successfully! You can now login', 'success')
            session['signup_success'] = (
                'Account created successfully! You can now login'
            )
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Check if there's a flash message for successful signup
    signup_success_message = session.pop('signup_success', None)
    if signup_success_message:
        print("Session contents after signup:", session)

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Query the database to check if the email and password match
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM user WHERE email = %s AND password = %s", (
                email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Set user information in the session
            session['user_id'] = user['id']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            # Flash message for successful login
            flash('Login successful! Welcome, {} {}'.format(
                user['first_name'], user['last_name']), 'success')
            return redirect(url_for('welcome'))  # Redirect to welcome page
        else:
            # Flash message for invalid email/password
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))

    return render_template(
        'login.html', form=form, signup_success_message=signup_success_message)


@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        flash('You need to login to access this page', 'error')
        return redirect(url_for('login'))

    # Fetch the current user's information
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()

    return render_template('welcome.html', user=user)


@app.route('/logout')
def logout():
    # Handle logout functionality
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))


@app.route('/all_posts')
def all_posts():
    # Query the database to retrieve all posts
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT p.*, u.first_name, u.last_name "
        "FROM posts p "
        "INNER JOIN user u ON p.user_id = u.id"
    )

    all_posts = cursor.fetchall()

    for post in all_posts:
        cursor.execute(
            "SELECT c.*, u.first_name, u.last_name "
            "FROM comment c "
            "INNER JOIN user u ON c.user_id = u.id "
            "WHERE c.post_id = %s",
            (post['id'],)
        )

        post['comments'] = cursor.fetchall()

    cursor.close()

    # Format the timestamp for each post
    for post in all_posts:
        post['formatted_date_posted'] = post['date_posted'].strftime(
            '%Y-%m-%d %H:%M:%S')

    # Create an instance of the NewPostForm and pass it to the template
    new_post_form = NewPostForm()
    return render_template(
        'all_posts.html', all_posts=all_posts, new_post_form=new_post_form,
        form=new_post_form)


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        user_id = session.get('user_id')  # Retrieve user ID from the session
        if user_id is None:
            flash('User ID not found in session. Please log in.', 'error')
            return redirect(url_for('login'))
        # Save the new post to the database
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO posts (title, content, user_id) "
            "VALUES (%s, %s, %s)",
            (title, content, user_id)
        )

        db.commit()
        cursor.close()
        flash('Post created successfully!', 'success')
        return redirect(url_for('all_posts'))
    return render_template('new_post.html', form=form)


@app.route('/my_posts')
def my_posts():
    if 'user_id' not in session:
        flash('You need to login to view your posts.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts WHERE user_id = %s", (user_id,))
    user_posts = cursor.fetchall()

    for post in user_posts:
        cursor.execute(
            "SELECT c.*, u.first_name, u.last_name "
            "FROM comment c INNER JOIN user u ON c.user_id = u.id "
            "WHERE c.post_id = %s",
            (post['id'],)
        )

        post['comments'] = cursor.fetchall()

    cursor.close()

    return render_template('my_posts.html', user_posts=user_posts)


@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        flash('You need to login to comment.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    content = request.form.get('comment_content')  # Corrected form field name

    # Insert the comment into the database
    cursor = db.cursor()
    cursor.execute(
            "INSERT INTO comment (post_id, user_id, content) "
            "VALUES (%s, %s, %s)",
            (post_id, user_id, content)
        )

    db.commit()
    cursor.close()

    flash('Comment added successfully!', 'success')
    return redirect(url_for('all_posts'))


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        flash('You need to login to edit your posts.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM posts WHERE id = %s AND user_id = %s", (
            post_id, user_id))
    post = cursor.fetchone()

    if post is None:
        flash('Post not found or you do not have permission to edit it.',
              'error')
        return redirect(url_for('my_posts'))

    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        cursor.execute(
            "UPDATE posts SET title = %s, content = %s WHERE id = %s", (
                new_title, new_content, post_id))
        db.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('my_posts'))

    cursor.close()
    return render_template('edit_post.html', post=post)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    print("Attempting to delete post with ID:", post_id)

    if 'user_id' not in session:
        flash('You need to login to delete a post.', 'error')
        return redirect(url_for('login'))

    # Check if the user trying to delete the post is the owner of the post
    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
    post = cursor.fetchone()
    if not post or post['user_id'] != user_id:
        flash('You can only delete your own posts.', 'error')
        return redirect(url_for('my_posts'))

    try:
        # Begin a transaction
        cursor.execute("START TRANSACTION")

        # Delete associated comments
        cursor.execute("DELETE FROM comment WHERE post_id = %s", (post_id,))

        # Delete the post from the database
        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))

        # Commit the transaction
        cursor.execute("COMMIT")

        flash('Post deleted successfully!', 'success')
    except Exception as e:
        # Rollback the transaction in case of any error
        cursor.execute("ROLLBACK")
        flash('An error occurred while deleting the post.', 'error')
        print("Error deleting post:", str(e))
    finally:
        cursor.close()

    return redirect(url_for('my_posts'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
