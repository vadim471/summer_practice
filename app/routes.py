from flask import render_template, url_for, redirect, request, Blueprint
from app.models import User, Apartment
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.MapService import MapService

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    query = Apartment.query

    deal_type = request.args.get('deal_type')
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
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')

    if deal_type:
        query = query.filter(Apartment.type_of_deal == deal_type)
    if min_cost:
        query = query.filter(Apartment.cost >= min_cost)
    if max_cost:
        query = query.filter(Apartment.cost <= max_cost)
    if min_price_per_sqm:
        query = query.filter(Apartment.cost / Apartment.square >= min_price_per_sqm)
    if max_price_per_sqm:
        query = query.filter(Apartment.cost / Apartment.square <= max_price_per_sqm)
    if min_floor:
        query = query.filter(Apartment.floor >= min_floor)
    if max_floor:
        query = query.filter(Apartment.floor <= max_floor)
    if building_type:
        query = query.filter(Apartment.type_of_building == building_type)
    if min_area:
        query = query.filter(Apartment.square >= min_area)
    if max_area:
        query = query.filter(Apartment.square <= max_area)
    if rooms_count:
        query = query.filter(Apartment.rooms_count == rooms_count)
    if address:
        query = query.filter(Apartment.address.ilike(f"%{address}%"))
    if latitude:
        query = query.filter(Apartment.latitude == latitude)
    if longitude:
        query = query.filter(Apartment.longitude == longitude)

    apartments = query.all()
    header, body, script = MapService.get_map(apartments)
    return render_template('home.html', apartments=apartments, header=header, body_html=body, script=script)



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
    apartments = Apartment.query.all()
    new_apartments = MapService.get_apartments_in_radius(apartments, latitude, longitude)
    header, body, script = MapService.get_map(apartments)
    return render_template('home.html', apartments=apartments, header=header, body_html=body, script=script)