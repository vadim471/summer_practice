import re
from .Apartment import Apartment, HouseType, SaleType
from bs4 import BeautifulSoup
from bs4.element import Tag
from .URLType import URLType
from .HTMLFetch import HTMLFetcher
from geopy.geocoders import Nominatim

class CianParser:
    
    def get_coordinate(self, address : str) -> tuple[float, float]:
        geolocator = Nominatim(user_agent="Tester")
        parts = address.replace('р-н', 'район').split(',')
        
        for i in range(len(parts), 0, -1):
            current_address = ', '.join(parts[:i]).strip()
            location = geolocator.geocode(current_address)
            if location:
                return (location.latitude, location.longitude)
    
    def parse_title(self, title: Tag) -> None | tuple[int, float, int]:
        regex = r"(?:(\d+?)\-комн.) .+?\, ((?:\d+)(?:,\d+)?) .+? (\d+)\/\d+"

        title_text = title.text
        matches = re.finditer(regex, title_text)

        for match in matches:
            return (
                int(match.group(1)),
                float(match.group(2).replace(",", ".")),
                int(match.group(3)),
            )
        
        regex = r"((?:\d+)(?:,\d+)?) .+? (\d+)\/\d+"
        #regex = r"(\d+)\s*м²,\s*(\d+)\/\d+\s*этаж"
        matches = re.finditer(regex, title_text)
        for match in matches:
             return 0, float(match.group(1).replace(",", ".")), int(match.group(2))
        return None

        

    def parse_card(self, card_tag: Tag, house_type: HouseType) -> Apartment:
        offer_title = card_tag.find("span", {"data-mark": "OfferTitle"})                        
        offer_subtitle = card_tag.find("span", {"data-mark": "OfferSubtitle"})

        if offer_title is None:
            raise Exception("Can't parse title")

        res = self.parse_title(offer_title)
        if res is None and type(offer_subtitle) is Tag:
            res = self.parse_title(offer_subtitle)
        if res is None:
            raise Exception("Can't parse title")

        rooms, area, floor = res
        main_price_raw = card_tag.find("span", {"data-mark": "MainPrice"})
        if type(main_price_raw) is not Tag:
            raise Exception("Can't parse price")
        
        match = re.search(r'\d+', main_price_raw.get_text().replace(' ', ''))
        if match:
            main_price = int(match.group(0))
        sale_type = SaleType.SALE
        if 'мес' in main_price_raw.get_text():
            sale_type = SaleType.RENT
       
        # price_info_raw = card_tag.find('p', {'data-mark': 'PriceInfo'})
        # if type(price_info_raw) is not Tag:
        #     raise Exception("Can't parse price")
        # price_info = price_info_raw.get_text()

        address = ", ".join(
            [a.get_text() for a in card_tag.find_all("a", {"data-name": "GeoLabel"})]
        )
        url_tag = card_tag.find("a", href = True)
        url = url_tag['href']
        coordinates = self.get_coordinate(address)
        longitude, latitude = coordinates
       
        return Apartment(
            address, main_price, area, rooms, floor, sale_type, house_type, url, longitude, latitude
        )

    def parse_feed_page(self, html_content: str, url_type: URLType, sum_card: int) -> list[Apartment]:
        soup = BeautifulSoup(html_content, "html.parser")
        cards = soup.find_all("div", {"data-name": "LinkArea"})
        
        apartments = []
        for i, card in enumerate(cards): 
            if card.find("button"):
                continue
            if sum_card > len(apartments):
                apartments.append(self.parse_card(card, url_type.house_type))
            else:
                break
        return apartments
    
    def parse_url_flat(self, url: str) -> int:
        html_content = HTMLFetcher().fetch_html(url)
        soup = BeautifulSoup(html_content, "html.parser")
        cost_text = soup.find("div", {"data-testid" : "price-amount"}).get_text()
        cost = int(cost_text.replace('\xa0', '').split('₽')[0])
        
        return cost