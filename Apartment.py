from enum import Enum


class SaleType(Enum):
    RENT = 1
    SALE = 2
    
class HouseType(Enum):
    NEW = 1
    SECONDARY = 2

class Apartment:
    def __init__(self, address: str, price: int, square: float, rooms: int, floor: int, sale_type: SaleType, house_type: HouseType):
        self.address = address
        self.price = price
        self.square = square
        self.rooms = rooms
        self.floor = floor
        self.sale_type = sale_type
        self.house_type = house_type
        
        

    def __str__(self):
        return f'Address: {self.address} Price: {self.price} rubs, Area: {self.square} m^2, Rooms: {self.rooms}'
    