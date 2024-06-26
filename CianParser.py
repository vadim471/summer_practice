import requests
from Parser import Parser
from Apartment import Apartment, HouseType, SaleType
from bs4 import BeautifulSoup
from bs4.element import Tag
import aiohttp

import re

from URLType import URLType


class CianParser(Parser):
    def parse_title(self, title: Tag) -> None | tuple[int, float, int]:
        regex = r"(?:(\d+?)\-комн.) .+?\, ((?:\d+)(?:,\d+)?) .+? (\d+)\/\d+"

        title_text = title.text
        matches = re.finditer(regex, title_text)
        if matches is None:
            regex = r"(?:Студия,) .+?\, ((?:\d+)(?:,\d+)?) .+? (\d+)\/\d+"

            matches = re.finditer(regex, title_text)
            for match in matches:
                return 0, float(match.group(1).replace(",", ".")), int(match.group(2))

        for match in matches:
            return (
                int(match.group(1)),
                float(match.group(2).replace(",", ".")),
                int(match.group(3)),
            )

    async def parse_card(self, card_tag: Tag, house_type: HouseType) -> Apartment:
        offer_title = card_tag.find("span", {"data-mark": "OfferTitle"})
        offer_subtitle = card_tag.find("span", {"data-mark": "OfferSubtitle"})

        if type(offer_title) is not Tag:
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
        main_price = int(main_price_raw.get_text())

        # price_info_raw = card_tag.find('p', {'data-mark': 'PriceInfo'})
        # if type(price_info_raw) is not Tag:
        #     raise Exception("Can't parse price")
        # price_info = price_info_raw.get_text()

        address = ", ".join(
            [a.get_text() for a in card_tag.find_all("a", {"data-name": "GeoLabel"})]
        )

        return Apartment(
            address, main_price, area, rooms, floor, SaleType.RENT, house_type
        )

    async def parse_feed_page(self, url_type: URLType) -> list[Apartment]:
        current_cards = 0
        current_page = 1
        
        apartments: list[Apartment] = []
        
        url_type.url = url_type.url.replace("&p=1", "&p=0")
        async with aiohttp.ClientSession() as session:
            session.headers.update({"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"})
            session.headers.update({"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"})
            session.headers.update({"accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"})
            session.headers.update({"accept-encoding": "gzip, deflate, br"})
            session.headers.update({"upgrade-insecure-requests": "1"})
            session.headers.update({"cache-control": "max-age=0"})
            while current_cards < url_type.count:
                async with session.get(url_type.url.replace(f"&p={current_page-1}", f"&p={current_page}")) as response:
                    if response.status != 200:
                        raise Exception("Can't get response")
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    cards = soup.find_all("div", {"data-name":"LinkArea"})
                    
                    for card in cards:
                        apartments.append(await self.parse_card(card, url_type.house_type))

                    current_page += 1
                    current_cards += len(cards)
        
        return apartments
                    
