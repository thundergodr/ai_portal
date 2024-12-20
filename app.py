from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_socketio import SocketIO, emit
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm
from models import User
from config import Config
from extensions import db  # Import db from extensions
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize the app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
socketio = SocketIO(app)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    print("OpenAI API key is not set. Check your .env file.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        
        db.session.add(user)
        try:
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')

    return render_template('login.html', form=form)

# Chat route
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=current_user.username)

# Handle chat messages with SocketIO
@socketio.on('message')
def handle_message(data):
    user_message = data['message']
    username = data['username']

    # Generate a timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Broadcast user message to all clients with the timestamp
    emit('message', {'username': username, 'message': user_message, 'timestamp': timestamp}, broadcast=True)

    # Generate AI response using the new API structure with error handling
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        # Extract the AI's response message
        ai_message = response['choices'][0]['message']['content'].strip()
        emit('message', {'username': 'AI', 'message': ai_message, 'timestamp': timestamp}, broadcast=True)
    except Exception as e:
        emit('message', {'username': 'AI', 'message': f"Sorry, I encountered an error: {str(e)}", 'timestamp': timestamp}, broadcast=True)

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
    socketio.run(app, debug=True)  # Use socketio.run instead of app.run
