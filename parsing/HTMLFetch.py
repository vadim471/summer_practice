from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HTMLFetcher:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome()

    def fetch_html(self, url: str) -> str:
        self.driver.get(url)
        WebDriverWait(self.driver, 10)
        
        page_source = self.driver.page_source
        return page_source
    
    def check_status_code(self, url: str) -> int:
        self.driver.get(url)
        status_code = self.driver.execute_script("""
            var xhr = new XMLHttpRequest();
            xhr.open('GET', arguments[0], false);
            xhr.send(null);
            return xhr.status;
        """, url)
        return status_code
       

 