from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
from email.message import EmailMessage
import ssl
import smtplib

from website.model import db, User, Group
from config import GMAIL_EMAIL, GMAIL_APP_PASSWORD, INITIAL_ADMIN_EMAIL

user_bp = Blueprint(
    'user_bp', __name__, template_folder='templates', static_folder='static', static_url_path='/user/static'
)

PASSWORD_LENGTH = 10

def check_tonbridge_email(email):
    return email.endswith('@tonbridge-school.org')

def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(PASSWORD_LENGTH))

def send_email(to_email, subject, body):
    email_message = EmailMessage()
    email_message['From'] = GMAIL_EMAIL
    email_message['To'] = to_email
    email_message['Subject'] = subject
    email_message.set_content(body)
    
    context = ssl.create_default_context()
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls(context=context)
        server.login(
            user=GMAIL_EMAIL,
            password=GMAIL_APP_PASSWORD
        )
        server.sendmail(
            from_addr=GMAIL_EMAIL,
            to_addrs=to_email,
            msg=email_message.as_string()
        )

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        if not check_tonbridge_email(email):
            flash('Please use your school email (@tonbridge-school.org)', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first() is not None:
            flash('Email has already been used', 'error')
            return render_template('register.html')
        
        password = generate_password()
        password_hash = generate_password_hash(password)
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            is_admin=False
        )
        
        if email == INITIAL_ADMIN_EMAIL:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        send_email(
            to_email=email,
            subject='Your ToPyC password',
            body=f'Hi {name},\nYour password is: {password}\nBest regards,\nToPyC'
        )
        
        flash('Registered successfully - your password has been sent to your email', 'success')
        return redirect(url_for('user_bp.login'))
        
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Email incorrect', 'error')
            return render_template('login.html')
        
        if not check_password_hash(user.password_hash, password):
            flash('Password incorrect', 'error')
            return render_template('login.html')
        
        login_user(user)
        return redirect(url_for('home_bp.home'))
        
    return render_template('login.html')

@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user_bp.login'))

@user_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        if 'name' in request.form:
            current_user.name = request.form['name']
            flash('Saved', 'success')
        elif 'group' in request.form:
            current_user.group = Group.query.get(request.form['group_id'])
            flash('Saved', 'success')
        db.session.commit()
    groups = Group.query.all()
    return render_template('settings.html', groups=groups)
