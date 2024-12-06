import asyncio
from datetime import datetime
from enum import Enum
import re
import bs4
import requests
from sqlalchemy import DateTime, Float, MetaData, Table, Column, Integer, String, Enum as Sqlenum

from . import models, schemas, database

from .database import SessionLocal, engine


from parsing.URLType import FeedType, URLType
from parsing.CianParser import CianParser
from parsing.YandexParser import YandexParser
from parsing.Apartment import HouseType, SaleType
from parsing.HTMLFetch import HTMLFetcher




    
    
def count_apartments_cian(feed_pages: list[URLType], needed_count: int) -> list[URLType]:
    total_request = requests.get(
        "https://chelyabinsk.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=5048&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1"
    )
    if total_request.status_code != 200:
        total_request = requests.get(
            "https://chelyabinsk.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=5048&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1"
        )
    parser = bs4.BeautifulSoup(total_request.text, "html.parser")
    total_raw = parser.find("div", {"data-name": "SummaryHeader"})
    if type(total_raw) is not bs4.element.Tag:
        raise Exception("Can't parse total count")

    total = int(re.findall(r"\d+", total_raw.get_text().replace(" ", ""))[0])

    total_secondary = 0

    for page in feed_pages:
        if page.url_type == FeedType.NEW_SALE:
            new_request = requests.get(page.url)

            parser = bs4.BeautifulSoup(new_request.text, "html.parser")
            new_raw = parser.find("div", {"data-name": "SummaryHeader"})
            if type(new_raw) is not bs4.Tag:
                raise Exception("Can't parse new count")

            page.count = int(
                int(re.findall(r"\d+", new_raw.get_text().replace(" ", ""))[0])
                / total
                * needed_count
            )

        elif page.url_type == FeedType.SECONDARY_SALE:
            secondary_sale_request = requests.get(page.url)

            parser = bs4.BeautifulSoup(secondary_sale_request.text, "html.parser")
            secondary_raw = parser.find("div", {"data-name": "SummaryHeader"})
            if type(secondary_raw) is not bs4.Tag:
                raise Exception("Can't parse secondary count")

            total_secondary = int(
                int(re.findall(r"\d+", secondary_raw.get_text().replace(" ", ""))[0])
                / total
                * needed_count
            )

            page.count = total_secondary // 2

        elif page.url_type == FeedType.SECONDARY_RENT:
            if total_secondary == 0:
                raise Exception("Invalid feed pages order")
            page.count = total_secondary // 2

    return feed_pages

def count_apartments_yandex(feed_pages: list[URLType], needed_count: int) -> list[URLType]:
    total_request_sale = requests.get(
        "https://realty.ya.ru/chelyabinsk/kupit/kvartira/"
    )
    #<div class="OffersSearchPageListing__sort--GZ5QI"><div><span class="OffersSerpSortSelect__totalCount--1Odl5">7&nbsp;877 объявлений:</span><div class="Select Select_size_l Select_theme_realty Select_view_white OffersSerpSortSelect__select--cWy6U" data-test="SelectControl"><button class="Button Button_js_inited Button_size_l Button_theme_realty Button_type_button Select__button" type="button"><span class="Button__text"><span class="Select__button-text-item">по актуальности</span></span><i class="Icon Icon_type_arrow2 Icon_direction_bottom Icon_animate-direction Select__button-tick"><svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M2.293 5.293a1 1 0 011.414 0L8 9.586l4.293-4.293a1 1 0 111.414 1.414l-5 5a1 1 0 01-1.414 0l-5-5a1 1 0 010-1.414z" fill="currentColor"></path></svg></i></button><select class="Select__control" tabindex="-1"><option value="RELEVANCE">по актуальности</option><option value="DATE_DESC">новые предложения</option><option value="PRICE">цена по возрастанию</option><option value="PRICE_DESC">цена по убыванию</option><option value="AREA">площадь по возрастанию</option><option value="AREA_DESC">площадь по убыванию</option><option value="PRICE_PER_SQUARE">цена за м2 - по возрастанию</option><option value="PRICE_PER_SQUARE_DESC">цена за м2 - по убыванию</option></select></div></div></div>
    #<span class="OffersSerpSortSelect__totalCount--1Odl5">7&nbsp;876 объявлений:</span>
    #<p class="ListingExtraText__text--2QLI3">Купить квартиру в Челябинске. — 7&nbsp;877 объявлений от агентств и собственников по продаже квартир по цене от 790&nbsp;000&nbsp;₽ до 39&nbsp;500&nbsp;000&nbsp;₽ на Яндекс Недвижимости. В нашем каталоге предложения площадью от 13&nbsp;м² до 1&nbsp;101&nbsp;м² в новостройках и вторичном жилье — фото, планировки и характеристики.</p>
    parser = bs4.BeautifulSoup(total_request_sale.text, "html.parser")
    total_raw = parser.find("span", {"class": "OffersSerpSortSelect__totalCount--1Odl5"}).get_text().replace('\xa0', '')
    #total_raw = parser.find('p', class_='ListingExtraText__text--2QLI3')
    total = int(re.findall(r"\d+", total_raw)[0])
    

    total_secondary = 0
    for page in feed_pages:
        if page.url_type == FeedType.NEW_SALE:
            new_request = requests.get(page.url)

            parser = bs4.BeautifulSoup(new_request.text, "html.parser")
            new_raw = parser.find("span", {"class": "OffersSerpSortSelect__totalCount--1Odl5"}).get_text().replace('\xa0', '')
            #new_raw = parser.find("span").get_text()
            page.count = int(
                int(re.findall(r"\d+", new_raw)[0])
                / total
                * needed_count
            )

        elif page.url_type == FeedType.SECONDARY_SALE:
            secondary_sale_request = requests.get(page.url)

            parser = bs4.BeautifulSoup(secondary_sale_request.text, "html.parser")
            secondary_raw = parser.find("span", {"class": "OffersSerpSortSelect__totalCount--1Odl5"}).get_text().replace('\xa0', '')
        
            total_secondary = int(
                int(re.findall(r"\d+", secondary_raw)[0])
                / total
                * needed_count
            )

            page.count = total_secondary 

        elif page.url_type == FeedType.SECONDARY_RENT:
            secondary_rent_request = requests.get(page.url)
            parser = bs4.BeautifulSoup(secondary_rent_request.text, "html.parser")
            count_text = parser.find("span", {"class": "OffersSerpSortSelect__totalCount--1Odl5"}).get_text().replace('\xa0', '')
            page.count = int(re.findall(r"\d+", count_text)[0])
            
        return feed_pages

def fill_db():
    
    feed_pages: list[URLType] = [
        URLType(
            HouseType.NEW,
            "https://chelyabinsk.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_seller_type%5B0%5D=1&offer_type=flat&p=1&region=5048&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1",
            250,
            SaleType.SALE,
            FeedType.NEW_SALE,
        ),
        URLType(
            HouseType.SECONDARY,
            "https://chelyabinsk.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_seller_type%5B0%5D=2&offer_seller_type%5B1%5D=3&offer_type=flat&p=1&region=5048&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1",
            500,
            SaleType.SALE,
            FeedType.SECONDARY_SALE,
        ),
        URLType(
            HouseType.SECONDARY,
            "https://chelyabinsk.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&p=1&region=5048&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1&type=4",
            290,
            SaleType.RENT,
            FeedType.SECONDARY_RENT,
        ),
    ]

    session = SessionLocal()
    parser = CianParser()
    fetcher = HTMLFetcher()
    """
    apartments: list[models.Apartment] = []
    
    
    #feed_pages = count_apartments_cian(feed_pages, 5000)

    for page in feed_pages:
        curr_card = 0
        curr_page = 0

        while curr_card < page.count: 
            page.url = page.url.replace(f"&p={curr_page}", f"&p={curr_page + 1}")
            html_content = fetcher.fetch_html(page.url)
            page_apartments = parser.parse_feed_page(html_content, page, page.count-curr_card)
            curr_page += 1
            curr_card += len(page_apartments)
            apartments.extend(page_apartments)
    
    for apartment in apartments:
        db_apartment = models.Apartment(
            type_of_deal=apartment.sale_type.name,
            type_of_building=apartment.house_type.name,
            url=apartment.url,
            cost=apartment.price,
            rooms_count=apartment.rooms,
            address=apartment.address,
            floor=apartment.floor,
            square=apartment.square,
            add_date= datetime.now(),
            longitude=apartment.longitude,
            latitude=apartment.latitude
            )
        session.add(db_apartment)
    session.commit()
    """
    apartments: list[models.Apartment] = []
    parser = YandexParser()
    feed_pages: list[URLType] = [
        URLType(
            HouseType.NEW,
            "https://realty.ya.ru/chelyabinsk/kupit/kvartira/?roomsTotal=STUDIO&roomsTotal=1&roomsTotal=2&roomsTotal=3&roomsTotal=PLUS_4&newFlat=YES&page=0",
            400,
            SaleType.SALE,
            FeedType.NEW_SALE,
        ),
        URLType(
            HouseType.SECONDARY,
            "https://realty.ya.ru/chelyabinsk/kupit/kvartira/?roomsTotal=STUDIO&roomsTotal=1&roomsTotal=2&roomsTotal=3&roomsTotal=PLUS_4&newFlat=NO&page=0",
            400,
            SaleType.SALE,
            FeedType.SECONDARY_SALE,
        ),
        URLType(
            HouseType.SECONDARY,
            "https://realty.ya.ru/chelyabinsk/snyat/kvartira/?roomsTotal=STUDIO&roomsTotal=1&roomsTotal=2&roomsTotal=3&roomsTotal=PLUS_4&page=0",
            150,
            SaleType.RENT,
            FeedType.SECONDARY_RENT,
        ),
    ]
    #feed_pages = count_apartments_yandex(feed_pages, 5)

    for page in feed_pages:
        curr_card = 0
        curr_page = 0

        while curr_card < page.count: 
            page.url = page.url.replace(f"&page={curr_page}", f"&page={curr_page + 1}")
            html_content = fetcher.fetch_html(page.url)
            page_apartments = parser.parse_feed_page(html_content, page, page.count-curr_card)
            curr_page += 1
            curr_card += len(page_apartments)
            apartments.extend(page_apartments)
            if len(apartments) > 20:
                for apartment in apartments:
                    db_apartment = models.Apartment(
                        type_of_deal=apartment.sale_type.name,
                        type_of_building=apartment.house_type.name,
                        url=apartment.url,
                        cost=apartment.price,
                        rooms_count=apartment.rooms,
                        address=apartment.address,
                        floor=apartment.floor,
                        square=apartment.square,
                        add_date= datetime.now(),
                        longitude=apartment.longitude,
                        latitude=apartment.latitude
                        )
                    session.add(db_apartment)
                session.commit()   
                apartments: list[models.Apartment] = []
    session.close()

