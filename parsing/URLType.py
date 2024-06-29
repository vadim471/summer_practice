from enum import Enum
from Apartment import HouseType, SaleType


class FeedType(Enum):
    NEW_SALE = 1
    SECONDARY_SALE = 2
    SECONDARY_RENT = 3


class URLType:
    def __init__(
        self,
        type: HouseType,
        url: str,
        count: int,
        sale_type: SaleType,
        url_type: FeedType,
    ):
        self.house_type = type
        self.url = url
        self.count = count
        self.sale_type = sale_type
        self.url_type = url_type

        def __str__(self):
            return f"HouseType: {self.house_type} Url: {self.url} Count: {self.count} SaleType: {self.sale_type} UrlType: {self.url_type}"

        def __repr__(self):
            return f"HouseType: {self.house_type} Url: {self.url} Count: {self.count} SaleType: {self.sale_type} UrlType: {self.url_type}"
