from datetime import datetime, timedelta
import time
from . import models, schemas, database
from .database import SessionLocal
from parsing.HTMLFetch import HTMLFetcher
from parsing.YandexParser import YandexParser
from parsing.CianParser import CianParser


class UpdateService:
    
    def check_and_update_announcements(self):
        session = SessionLocal()     
        fetcher = HTMLFetcher()
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        old_announcements = session.query(models.Apartment).filter(models.Apartment.add_date < three_days_ago).limit(5).all()
    
        for announcement in old_announcements:
            url = announcement.url
            status_code = fetcher.check_status_code(url)
        
            parser = YandexParser()
            if 'cian' in url:
                parser = CianParser()
            
            if status_code == 200:
                new_cost = parser.parse_url_flat(url)
                announcement.cost = new_cost
                announcement.add_date = datetime.utcnow() 
                session.commit()
            else:
                session.delete(announcement)
                session.commit()        
        
    def run(self):
        while True:
            self.check_and_update_announcements()
            time.sleep(600) 
            
        
           
        
        

