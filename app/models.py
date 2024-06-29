from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum
from Apartment import HouseType, SaleType
from app import login_manager, db
from flask_login import UserMixin


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(50), nullable=False)

class Apartment(Base):
    __tablename__ = "flat"

    id = Column(Integer, primary_key=True, index=True)
    type_of_deal = Column(Enum(SaleType), nullable=False)
    type_of_building = Column(Enum(HouseType), nullable=False)
    url = Column(String, nullable=False, unique=True)
    cost = Column(Integer, nullable=False)
    rooms_count = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    square = Column(Float, nullable=False)
    add_date = Column(DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))