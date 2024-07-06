from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class SaleType(str, Enum):
    rent = "RENT"
    sale = "SALE"

class HouseType(str, Enum):
    NEW = "NEW"
    SECONDARY = "SECONDARY"

class ApartmentBase(BaseModel):
    type_of_deal: SaleType
    type_of_building: HouseType
    url: str
    cost: float
    rooms_count: int
    address: str
    floor: int
    square: float
    add_date: datetime
    longitude: float | None = None
    latitude: float | None = None

class ApartmentCreate(ApartmentBase):
    pass

class Apartment(ApartmentBase):
    id: int

    class Config:
        orm_mode = True