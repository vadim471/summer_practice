from datetime import datetime, timedelta

from app.models import Apartment
from .database import SessionLocal
from parsing.HTMLFetch import HTMLFetcher
from parsing.YandexParser import YandexParser
from parsing.CianParser import CianParser


def check_and_update_announcements():
    session = SessionLocal()    
    fetcher = HTMLFetcher()
    three_days_ago = datetime.utcnow() - timedelta(days=1)
    old_announcements = session.query(Apartment).filter(Apartment.add_date < three_days_ago).limit(5)
    
    for announcement in old_announcements:
        url = announcement.url
        status_code = fetcher.check_status_code(url)
        
        if status_code == 404:
            session.delete(announcement)
            session.commit()        
        
        parser = YandexParser()
        if 'cian' in url:
            parser = CianParser()
            
        new_cost = parser.parse_url_flat(url)
        announcement.cost = new_cost
        announcement.add_date = datetime.utcnow()            
        session.commit()
        
        

