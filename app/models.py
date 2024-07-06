from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
import enum
from .database import Base

class SaleType(enum.Enum):
    RENT = 1
    SALE = 2
    
class HouseType(enum.Enum):
    NEW = 1
    SECONDARY = 2
    
class UserRole(enum.Enum):
    user = "user"
    admin = "admin"
    
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False) 
    password = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    tokents_count = Column(Integer, default=10)

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
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    

        
    def __str__(self):
        return f'Address: {self.address} Price: {self.price} rubs, Area: {self.square} m^2, Rooms: {self.rooms}, Url: {self.url}'
    