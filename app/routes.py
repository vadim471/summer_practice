from flask import render_template, url_for, redirect, request, Blueprint
from app.models import User, Apartment
from flask_login import login_user, current_user, logout_user, login_required
from app import db

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    apartments = Apartment.query.all()
    return render_template('home.html', apartments=apartments)


@routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        user = User(name=name, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('routes.home'))
    return render_template('register.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(name=name).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('routes.home'))
    return render_template('login.html')

@routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.home'))