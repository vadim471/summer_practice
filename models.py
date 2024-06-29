from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum
from Apartment import HouseType, SaleType

Base = declarative_base()

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