from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm
from models import User
from config import Config
from extensions import db  # Import db from extensions

# Initialize the app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        print("User is already logged in, redirecting to chat.")
        return redirect(url_for('chat'))
    
    form = RegistrationForm()
    print("Registration form loaded.")

    if form.validate_on_submit():
        print("Form validation successful.")
        
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        
        db.session.add(user)
        try:
            db.session.commit()
            print("User successfully added to the database.")
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during commit: {e}")
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
    else:
        print("Form validation failed or not submitted yet.")

    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("User is already logged in, redirecting to chat.")
        return redirect(url_for('chat'))
    
    form = LoginForm()
    print("Login form loaded.")
    
    if form.validate_on_submit():
        print("Form validation successful.")
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            print("Password check successful.")
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('chat'))
        else:
            print("Invalid credentials.")
            flash('Login unsuccessful. Please check username and password.', 'danger')
    else:
        print("Form validation failed or not submitted yet.")

    return render_template('login.html', form=form)

# Chat route
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=current_user.username)

# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This should create the tables in the database
    app.run(debug=True)
