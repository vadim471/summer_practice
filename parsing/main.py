import asyncio
from datetime import datetime
from enum import Enum
import re

import bs4
import requests
from sqlalchemy import DateTime, Float, MetaData, Table, Column, Integer, String, Enum as Sqlenum
from CianParser import CianParser
from HTMLFetch import HTMLFetcher
from Parser import Parser
from Apartment import Apartment, HouseType, SaleType
from URLType import FeedType, URLType
from database import SessionLocal, engine
from models import Base, Apartment
from sqlalchemy.orm import Session


def count_apartments(feed_pages: list[URLType], needed_count: int) -> list[URLType]:
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


def main():
    feed_pages: list[URLType] = [
        URLType(
            HouseType.NEW,
            "https://chelyabinsk.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_seller_type%5B0%5D=1&offer_type=flat&p=1&region=5048&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1",
            0,
            SaleType.SALE,
            FeedType.NEW_SALE,
        ),
        URLType(
            HouseType.SECONDARY,
            "https://chelyabinsk.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_seller_type%5B0%5D=2&offer_seller_type%5B1%5D=3&offer_type=flat&p=1&region=5048&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1",
            0,
            SaleType.SALE,
            FeedType.SECONDARY_SALE,
        ),
        URLType(
            HouseType.SECONDARY,
            "https://chelyabinsk.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&p=1&region=5048&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room9=1&type=4",
            0,
            SaleType.RENT,
            FeedType.SECONDARY_RENT,
        ),
    ]


    session = SessionLocal()
    parser = CianParser()
    fetcher = HTMLFetcher()
    
    meta=MetaData()
    t=Table(
        "flat",
        meta,
        Column('id', Integer, primary_key=True, index=True),
        Column('type_of_deal', Sqlenum(SaleType), nullable=False),
        Column('type_of_building', Sqlenum(HouseType), nullable=False),
        Column('url', String, nullable=False),
        Column('cost', Integer, nullable=False),
        Column('rooms_count', Integer, nullable=False),
        Column('address', String, nullable=False),
        Column('floor', Integer, nullable=False),
        Column('square', Float, nullable=False),
        Column('add_date', DateTime, default=datetime.utcnow),
    )
   

    apartments: list[Apartment] = []
    
    #meta.create_all(engine)
    
    feed_pages = count_apartments(feed_pages, 1000)

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
        print(apartment)
        db_apartment = Apartment(
            type_of_deal=apartment.sale_type,
            type_of_building=apartment.house_type,
            url=apartment.url,
            cost=apartment.price,
            rooms_count=apartment.rooms,
            address=apartment.address,
            floor=apartment.floor,
            square=apartment.square,
            add_date=datetime.now()
        )
        session.add(db_apartment)
    session.commit()
    session.close()

    


if __name__ == "__main__":
    main()
