from abc import ABC, abstractmethod

from bs4.element import Tag
from Apartment import Apartment, HouseType, SaleType


class Parser(ABC):
    @abstractmethod
    def parse_card(self, html: Tag, type: HouseType) -> Apartment:
        pass

    @abstractmethod
    def parse_feed_page(self, url: str, type: HouseType, sale_type: SaleType) -> list[str]:
        pass
