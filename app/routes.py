from flask import jsonify, render_template, url_for, redirect, request, Blueprint
from . import models
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.MapService import MapService
from datetime import datetime, timedelta

from .StatisticsService import StatisticsService

from flask import render_template, url_for, redirect, request, Blueprint, jsonify
routes = Blueprint('routes', __name__)

@routes.route('/')
@login_required
def home():
    
    query = db.session.query(models.Apartment)

    deal_type = request.args.get('deal_type')
    clusters_num = request.args.get('cluster_num')
    min_cost = request.args.get('min_cost')
    max_cost = request.args.get('max_cost')
    min_price_per_sqm = request.args.get('min_price_per_sqm')
    max_price_per_sqm = request.args.get('max_price_per_sqm')
    min_floor = request.args.get('min_floor')
    max_floor = request.args.get('max_floor')
    building_type = request.args.get('building_type')
    min_area = request.args.get('min_area')
    max_area = request.args.get('max_area')
    rooms_count = request.args.get('rooms_count')
    address = request.args.get('address')
    location = request.args.get('location')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')


    if deal_type:
        query = query.filter(models.Apartment.type_of_deal == deal_type)
    if min_cost:
        query = query.filter(models.Apartment.cost >= min_cost)
    if max_cost:
        query = query.filter(models.Apartment.cost <= max_cost)
    if min_price_per_sqm:
        query = query.filter(models.Apartment.cost / models.Apartment.square >= min_price_per_sqm)
    if max_price_per_sqm:
        query = query.filter(models.Apartment.cost / models.Apartment.square <= max_price_per_sqm)
    if min_floor:
        query = query.filter(models.Apartment.floor >= min_floor)
    if max_floor:
        query = query.filter(models.Apartment.floor <= max_floor)
    if building_type:
        query = query.filter(models.Apartment.type_of_building == building_type)
    if min_area:
        query = query.filter(models.Apartment.square >= min_area)
    if max_area:
        query = query.filter(models.Apartment.square <= max_area)
    if rooms_count:
        query = query.filter(models.Apartment.rooms_count == rooms_count)
  

    if current_user.is_authenticated:
        if current_user.tokens_count > 0:
            current_user.tokens_count -= 1
            db.session.commit()
        else:
            return redirect(url_for('routes.no_tokens'))

    apartments = query.all()
    if location and latitude and longitude:
        apartments = MapService.get_apartments_in_radius(apartments, float(latitude), float(longitude))

    if not clusters_num:
        clusters_num = 0
    header, body, script = MapService.get_map(apartments, int(clusters_num))
    return render_template('home.html', apartments=apartments, header=header, body_html=body, script=script)
    

@routes.route('/no_tokens')
@login_required
def no_tokens():
    return render_template('no_tokens.html')    
    
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        user = models.User(name=name, password=password)
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
        user = db.session.query(models.User).filter_by(name=name).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('routes.home'))
    return render_template('login.html')

@routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.home'))

@routes.route('/like', methods=['POST'])
def like():
    data = request.get_json()
    apartment_id = data.get('apartmentId')
    # добавление в избранное


@routes.route('/get_apartments_in_radius', methods=['POST'])
def get_radius():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    apartments = db.session.query(models.Apartment).all()
    new_apartments = MapService.get_apartments_in_radius(apartments, latitude, longitude)
    header, body, script = MapService.get_map(apartments)
    return render_template('home.html', apartments=apartments, header=header, body_html=body, script=script)

@routes.route('/user_dashboard')
@login_required
def user_dashboard():
    viewed_apartments = db.session.query(models.UserViewedApartment).filter_by(user_id = current_user.id).all()
    return render_template('user_dashboard.html', user = current_user, viewed_apartments = viewed_apartments)
    
@routes.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != models.UserRole.admin:
        return redirect(url_for('routes.home'))
    return render_template('admin_dashboard.html', admin=current_user)

@routes.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == models.UserRole.admin:
        return redirect(url_for('routes.admin_dashboard'))
    else:
        return redirect(url_for('routes.user_dashboard'))

@routes.route('/add_to_viewed', methods=['GET','POST'])
@login_required
def add_to_viewed():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"})
    data = request.get_json()
    apartment_id = data.get('apartment_id')
    
    user = current_user
    
    apartment = db.session.query(models.Apartment).filter_by(id=apartment_id).first()

    new_viewed_apartment = models.UserViewedApartment(
            user_id=user.id,
            apartment_id=apartment_id
        )
    db.session.add(new_viewed_apartment)
    db.session.commit()
    
    return jsonify({'message': 'Apartment added to viewed list'}) 
