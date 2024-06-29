from bs4 import Tag
import re

from Apartment import HouseType, Apartment, SaleType
from Parser import Parser
from selenium.webdriver.common.by import By


class YandexParser(Parser):
    def parse_feed_page(self, url: str, type: HouseType, sale_type: SaleType) -> list[str]:
        pass

    def parse_card(self, offer: Tag, house_type: HouseType) -> Apartment:
        link = offer.find_element(By.CSS_SELECTOR, '.OffersSerpItem__link').get_attribute('href')
        cost = int(offer.find_element(By.CSS_SELECTOR, '.OffersSerpItem__price').text.split('₽')[0])

        title = offer.find_element(By.CSS_SELECTOR, '.OffersSerpItem__title').text
        rooms_count = self.get_rooms_count(title)
        floor = self.get_floor(title)
        square = self.get_square(title)

        # type_of_deal = get_deal_type(url)
        sale_type = SaleType.SALE

        if 
        address = offer.find_element(By.CSS_SELECTOR, '.AddressWithGeoLinks__addressContainer--4jzfZ').text
        return Apartment(
            address, cost, square, rooms_count, floor, sale_type, house_type
        )

    def get_rooms_count(self, title) -> int:
        rooms_match = re.search(r'((\d+)-комнатная квартира|квартира-студия)', title)
        if rooms_match:
            if 'студия' in rooms_match.group(1):
                return 0
            else:
                return int(rooms_match.group(1).split('-')[0])

    def get_floor(self, title) -> int:
        floor_match = re.search(r'(\d+) этаж из (\d+)', title)
        return int(floor_match.group(1)) if floor_match else 0

    def get_square(self, title) -> float:
        square_match = re.search(r'(\d+(?:,\d+)?) м²', title)
        return float(square_match.group(1).replace(',', '.')) if square_match else 0