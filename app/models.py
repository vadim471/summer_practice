from datetime import datetime
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True) 
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

class Apartment(db.Model):

    __tablename__ = 'flat'

    id = db.Column(db.Integer, primary_key=True, index=True)
    type_of_deal = db.Column(db.String, nullable=False)
    type_of_building = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    rooms_count = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    square = db.Column(db.Float, nullable=False)
    add_date = db.Column(db.DateTime, default=datetime.utcnow)