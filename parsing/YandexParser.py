import re
from .Apartment import Apartment, HouseType, SaleType
from bs4 import BeautifulSoup
from bs4.element import Tag
from .URLType import URLType
from .HTMLFetch import HTMLFetcher
from geopy.geocoders import Nominatim


class YandexParser:
    def get_coordinate(self, address : str) -> tuple[float, float]:
        geolocator = Nominatim(user_agent="Tester")
        parts = address.replace('р-н', 'район').split(',')
        
        for i in range(len(parts), 0, -1):
            current_address = ', '.join(parts[:i]).strip()
            location = geolocator.geocode(current_address)
            if location:
                return (location.latitude, location.longitude)
    
    def parse_feed_page(self, html_content: str, url_type: URLType, sum_card: int) -> list[Apartment]:
        soup = BeautifulSoup(html_content, "html.parser")
        cards = soup.find_all("div", {"class": "OffersSerpItem__main"})
        #offers = driver.find_elements(By.CSS_SELECTOR, '.OffersSerpItem')
        apartments = []

        for i, card in enumerate(cards): 
            if sum_card > len(apartments):
                flat = self.parse_card(card, url_type.house_type)
                if flat != None:
                    apartments.append(flat)
            else:
                break
            
        return apartments

    def parse_card(self, offer: Tag, house_type: HouseType) -> Apartment:
        link = 'https://realty.ya.ru'+offer.find("a", href=True)['href']
        cost_text = offer.find("div",{"class": "Price"}).get_text()
        cost = int(cost_text.replace('\xa0', '').split('₽')[0])
        title = offer.find("span").get_text().replace('\xa0', '')
        #title = offer.find_element(By.CSS_SELECTOR, '.OffersSerpItem__title').text
        rooms_count = self.get_rooms_count(title)
        floor = self.get_floor(title)
        square = self.get_square(title)

        # type_of_deal = get_deal_type(url)
        sale_type = SaleType.SALE

        if 'месяц' in cost_text:
            sale_type = SaleType.RENT
        address = offer.find( "div", {"class" : "AddressWithGeoLinks__addressContainer--4jzfZ"}).get_text()
        coordinates = self.get_coordinate(address)
        if coordinates == None:
            return None
        longitude, latitude = coordinates
        return Apartment(
            address, cost, square, rooms_count, floor, sale_type, house_type, link, longitude, latitude
        )

    def get_rooms_count(self, title) -> int:
        rooms_match = re.search(r'((\d+)-комнатная квартира|квартира-студия)', title)
        if rooms_match:
            if 'студия' in rooms_match.group(1):
                return 0
            else:
                return int(rooms_match.group(1).split('-')[0])

    def get_floor(self, title) -> int:
        floor_match = re.search(r'(\d+)этажиз(\d+)', title)
        return int(floor_match.group(1)) if floor_match else 0

    def get_square(self, title) -> float:
        square_match = re.search(r'(\d+(?:,\d+)?)м²', title)
        return float(square_match.group(1).replace(',', '.')) if square_match else 0
      
    def parse_url_flat(self, url: str) -> int:
        html_content = HTMLFetcher().fetch_html(url)
        soup = BeautifulSoup(html_content, "html.parser")
        cost_text = soup.find("span", {"class" : "OfferCardSummaryInfo__price--2FD3C OfferCardSummaryInfo__priceWithLeftMargin--3I6Y8"}).get_text()
        cost = int(cost_text.replace('\xa0', '').split('₽')[0])
        
        return cost
    