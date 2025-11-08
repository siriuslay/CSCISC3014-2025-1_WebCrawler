"""
Ticket grabbing module
"""

import os
import pickle
from time import sleep
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config import settings
from utils.logger import log


CUSTOM_SUBMIT_SELECTORS = [
    '//span[contains(text(), "立即提交")]',
    '//span[text()="立即提交"]',
]

CUSTOM_BUYER_SELECTORS = []


class TicketGrabber:
    """Ticket grabber class"""
    
    def __init__(self):
        self.status = 0
        self.login_method = 1
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.cookies_file = Path("cookies.pkl")
        self.target_url = ""
        
        log.info("TicketGrabber initialized")
    
    def start_browser(self, headless: bool = False):
        """Start browser"""
        log.info("Starting browser...")
        
        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.set_page_load_timeout(30)
        self.driver.maximize_window()
        
        log.success("Browser started")
    
    def set_cookies(self):
        """First login and save cookies"""
        damai_url = 'https://www.damai.cn/'
        self.driver.get(damai_url)
        
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(0.5)
        
        while self.driver.title != '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':
            sleep(0.5)
        
        pickle.dump(self.driver.get_cookies(), open(self.cookies_file, 'wb'))
        self.driver.get(self.target_url)
    
    def get_cookie(self):
        """Load cookies from file"""
        cookies = pickle.load(open(self.cookies_file, 'rb'))
        for cookie in cookies:
            cookie_dict = {
                'domain': '.damai.cn',
                'name': cookie.get('name'),
                'value': cookie.get('value')
            }
            self.driver.add_cookie(cookie_dict)
    
    def login(self):
        """Login"""
        if self.login_method == 0:
            login_url = 'https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F'
            self.driver.get(login_url)
        elif self.login_method == 1:
            if not os.path.exists(self.cookies_file):
                self.set_cookies()
            else:
                self.driver.get(self.target_url)
                self.get_cookie()
    
    def enter_concert(self):
        """Enter concert page"""
        self.login()
        self.driver.refresh()
        self.status = 2
        sleep(0.5)
    
    def safe_click(self, element):
        """Safe click with scroll"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        sleep(0.5)
        element.click()
        return True
    
    def find_element_robust(self, selectors: List[Tuple[str, str]], element_name: str = "element"):
        """Find element with multiple selectors"""
        for i, (by_type, selector) in enumerate(selectors, 1):
            if by_type == By.XPATH:
                elements = self.driver.find_elements(By.XPATH, selector)
            elif by_type == By.CLASS_NAME:
                elements = self.driver.find_elements(By.CLASS_NAME, selector)
            elif by_type == By.ID:
                elements = self.driver.find_elements(By.ID, selector)
            elif by_type == By.CSS_SELECTOR:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            else:
                continue

            visible_elements = [el for el in elements if el.is_displayed()]
            
            if visible_elements:
                # print(visible_elements[0])
                # print(selector)
                return visible_elements[0]
        
        return None
    
    def select_session_and_price(self):
        """Select session and price"""
        session_selectors = [
            (By.XPATH, '//div[contains(text(), "场次")]/../following-sibling::*//div[contains(@class, "item")]'),
            (By.XPATH, '//*[contains(text(), "场次")]//following::*[contains(@class, "session")]'),
            (By.XPATH, '//*[contains(text(), "2025-") and contains(text(), "周")]'),
            (By.XPATH, '//div[contains(@class, "session-item")]'),
            (By.XPATH, '//div[contains(@class, "time-item")]'),
        ]
        
        session = self.find_element_robust(session_selectors, "session")
        if session:
            self.safe_click(session)
            sleep(0.5)
        
        price_selectors = [
            (By.XPATH, '//div[contains(text(), "票档")]/../following-sibling::*//div[contains(@class, "item")]'),
            (By.XPATH, '//*[contains(text(), "元")]'),
            (By.XPATH, '//div[contains(text(), "早鸟票")]'),
            (By.XPATH, '//div[contains(@class, "price-item")]'),
            (By.XPATH, '//div[contains(@class, "sku-item")]'),
        ]
        
        price = self.find_element_robust(price_selectors, "price")
        if price:
            self.safe_click(price)
            sleep(0.5)
        
        return True
    
    def click_confirm_button(self):
        """Click confirm button"""
        confirm_selectors = [
            (By.XPATH, '//button[contains(text(), "确定")]'),
            (By.XPATH, '//button[contains(text(), "立即购买")]'),
            (By.XPATH, '//button[contains(text(), "确认")]'),
            (By.XPATH, '//div[@class="footer"]//button'),
            (By.XPATH, '//div[contains(@class, "footer")]//button'),
            (By.XPATH, '//div[contains(@class, "bottom")]//button'),
            (By.XPATH, '//button[contains(@class, "submit")]'),
            (By.XPATH, '//button[contains(@class, "confirm")]'),
            (By.CSS_SELECTOR, '.footer button'),
            (By.CSS_SELECTOR, '.bottom-bar button'),
            (By.XPATH, '//*[@id="app"]//button[last()]'),
        ]
        
        confirm_btn = self.find_element_robust(confirm_selectors, "confirm button")
        
        if confirm_btn:
            if self.safe_click(confirm_btn):
                sleep(0.5)
                return True
        
        return False
    
    def choose_ticket(self):
        """Choose ticket"""
        if self.status == 2:
            max_attempts = 10
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                current_title = self.driver.title

                order_keywords = ['确认订单', '订单确认', '确认购买', '提交订单']
                if any(keyword in current_title for keyword in order_keywords):
                    self.status = 3
                    break
                
                buy_button_selectors = [
                    (By.CLASS_NAME, 'buy-button'),
                    (By.XPATH, '//*[contains(text(), "立即购票")]'),
                    (By.XPATH, '//*[contains(text(), "立即预订")]'),
                    (By.XPATH, '//button[contains(text(), "购票")]'),
                    (By.XPATH, '//div[contains(@class, "buy")]'),
                ]
                
                buy_button = self.find_element_robust(buy_button_selectors, "buy button")
                
                if buy_button:
                    button_text = buy_button.text
                    
                    if '立即购票' in button_text or '立即预订' in button_text:
                        if self.safe_click(buy_button):
                            sleep(0.5)
                            self.select_session_and_price()

                            if self.click_confirm_button():
                                sleep(0.5)
                                
                                new_title = self.driver.title
                                
                                if any(keyword in new_title for keyword in order_keywords):
                                    self.status = 3
                                    break
                                elif '选座' in new_title:
                                    self.choice_seats()
                                    continue
                            
                    elif '缺货登记' in button_text or '提交缺货' in button_text:
                        self.driver.refresh()
                        sleep(0.5)
                        
                    elif '即将开票' in button_text or '即将开抢' in button_text:
                        sleep(0.5)
                        
                    else:
                        sleep(0.5)
                else:
                    sleep(0.5)
            
            if self.status >= 3:
                self.check_order()
    
    def choice_seats(self):
        """Select seats"""
        log.info("Please select seats manually")
        
        for i in range(30, 0, -1):
            sleep(0.5)
            
            order_keywords = ['确认订单', '确认购买', '提交订单']
            if any(keyword in self.driver.title for keyword in order_keywords):
                return
    
    def check_order(self):
        """Check and submit order"""
        submit_selectors = [
            (By.XPATH, '//span[contains(text(), "立即提交")]'),
            (By.XPATH, '//span[text()="立即提交"]'),
            (By.XPATH, '//span[contains(text(), "立即提交")]/..'),
            (By.XPATH, '//span[text()="立即提交"]/parent::*'),
            (By.XPATH, '//span[contains(text(), "立即提交")]/parent::div'),
            (By.XPATH, '//span[contains(text(), "立即提交")]/parent::button'),
            (By.XPATH, '//span[contains(text(), "提交订单")]'),
            (By.XPATH, '//span[contains(text(), "确认提交")]'),
            (By.XPATH, '//span[contains(text(), "确认购买")]'),
            (By.XPATH, '//span[contains(text(), "提交订单")]/..'),
            (By.XPATH, '//span[contains(text(), "确认提交")]/..'),
            (By.XPATH, '//span[contains(text(), "确认购买")]/..'),
            (By.XPATH, '//button[contains(text(), "立即提交")]'),
            (By.XPATH, '//button[contains(text(), "提交订单")]'),
            (By.XPATH, '//button[contains(text(), "确认提交")]'),
            (By.XPATH, '//div[contains(@class, "footer")]//button'),
            (By.XPATH, '//div[contains(@class, "bottom")]//button'),
            (By.XPATH, '//footer//button'),
            (By.XPATH, '//button[last()]'),
        ]
        
        for selector in CUSTOM_SUBMIT_SELECTORS:
            if selector not in [s[1] for s in submit_selectors[:2]]:
                submit_selectors.insert(0, (By.XPATH, selector))
        
        submit_element = self.find_element_robust(submit_selectors, "submit button")
        
        if submit_element:
            buyer_selectors = [
                (By.XPATH, '//label[contains(@class, "buyer")]'),
                (By.XPATH, '//div[contains(@class, "viewer")]//label'),
                (By.XPATH, '//input[@type="checkbox"][1]/..'),
                (By.XPATH, '//span[contains(text(), "观演人")]/..//input/..'),
                (By.XPATH, '//label[1]'),
            ]
            
            for selector in CUSTOM_BUYER_SELECTORS:
                buyer_selectors.insert(0, (By.XPATH, selector))
            
            buyer = self.find_element_robust(buyer_selectors, "buyer")
            
            if buyer:
                self.safe_click(buyer)
                sleep(0.5)
            
            sleep(0.5)
            
            if self.safe_click(submit_element):
                log.success("Order submitted")
                
                for i in range(60, 0, -1):
                    sleep(0.5)
    
    def grab_ticket(self, concert_url: str, ticket_config: Dict = None) -> bool:
        """Main ticket grabbing process"""
        self.target_url = concert_url
        
        log.info(f"Target URL: {concert_url}")
        
        self.enter_concert()
        self.choose_ticket()
        
        log.success("Ticket grabbing process completed")
        
        return True
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
        log.info("Browser closed")
    
    def __enter__(self):
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def quick_grab(concert_url: str, ticket_config: Dict = None) -> bool:
    """Quick ticket grabbing"""
    grabber = TicketGrabber()
    grabber.start_browser(headless=False)
    
    success = grabber.grab_ticket(concert_url, ticket_config)
    
    if success:
        log.info("Please complete payment in browser")
        sleep(300)
    
    grabber.close()
    return success