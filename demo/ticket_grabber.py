from pathlib import Path
import os
import pickle
from time import sleep
from typing import Dict, Optional, List, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


LOGIN_URL = 'https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F'
WEBSITE_URL = 'https://www.damai.cn/'


class TicketGrabber:

    def __init__(self):
        self.status = 0  # 0: not started, 1: logged in, 2: on concert page, 3: order page
        self.login_method = 1
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.cookies_file = Path("cookies.pkl")
        self.target_url = ""

    
    def start_browser(self, headless: bool = False):
        options = Options()
        if headless:
            options.add_argument('--headless')    # headless = do not open browser window
            options.add_argument('--disable-gpu')
        
        options.add_argument('--disable-blink-features=AutomationControlled')  # anti-detection
        options.add_experimental_option('excludeSwitches', ['enable-automation'])   # do not show "Chrome is being controlled by automated test software"
        options.add_experimental_option('useAutomationExtension', False)   # disable automation extension
        options.add_argument('--no-sandbox')    # bypass OS security model
        options.add_argument('--disable-dev-shm-usage')   # overcome limited resource problems
        options.add_argument('--window-size=1920,1080')   # set window size
        
        service = Service(ChromeDriverManager().install())   #
        self.driver = webdriver.Chrome(service=service, options=options)   # initialize Chrome driver
        self.wait = WebDriverWait(self.driver, 10)   # wait up to 10 seconds for elements to appearq
        self.driver.set_page_load_timeout(30)
        self.driver.maximize_window()


    def _set_cookies(self):
        """First login and save cookies"""
        self.driver.get(WEBSITE_URL)
        print(self.driver.title)
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:   # wait until redirected to login page
            sleep(0.5)
        
        print(self.driver.title)
        while self.driver.title != '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':  # wait until login is complete
            sleep(0.5)
        
        print(self.driver.title)
        # print(self.driver.get_cookies())
        pickle.dump(self.driver.get_cookies(), open(self.cookies_file, 'wb'))
        self.driver.get(self.target_url)
    

    def _get_cookie(self):
        cookies = pickle.load(open(self.cookies_file, 'rb'))
        for cookie in cookies:
            cookie_dict = {
                'domain': '.damai.cn',
                'name': cookie.get('name'),
                'value': cookie.get('value')
            }
            self.driver.add_cookie(cookie_dict)    # add cookie to browser

        
    def _find_element(self, selector: List[Tuple[str, str]]):

        selector = '//*[contains(text(), "立即购票")]'
        elements = self.driver.find_elements(By.XPATH, selector)
        visible_elements = [el for el in elements if el.is_displayed()]
        if visible_elements:
            return visible_elements[0]
        
        return None
    

    def _scroll_click(self, element):
        """Scroll and click"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)   # scroll element into view
        sleep(0.5)
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element) # click using JavaScript if normal click fails
        return True

    
    def login(self):
        """Login"""
        if self.login_method == 0:
            self.driver.get(LOGIN_URL)
        elif self.login_method == 1:
            if not os.path.exists(self.cookies_file):
                self._set_cookies()
            else:
                self.driver.get(self.target_url)
                self._get_cookie()


    def grab_ticket(self, concert_url: str) -> bool:
        """Main ticket grabbing process"""
        self.target_url = concert_url
        
        self.enter_concert()
        # self.choose_ticket()

        return self.choose_ticket()


    def enter_concert(self):
        self.login()
        self.driver.refresh()
        self.status = 2
        sleep(0.5)
    

    def choose_ticket(self):
        if self.status == 2:
            max_attempts = 10
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                current_title = self.driver.title
                print(current_title)     # 商品详情

                order_keywords = '确认购买'
                if current_title == order_keywords:
                    self.status = 3
                    break
                
                buy_button_selector = (By.XPATH, '//*[contains(text(), "立即购票")]')
                buy_button = self._find_element(buy_button_selector)
                
                if buy_button:
                    button_text = buy_button.text
                    
                    if '立即购票' in button_text:  
                        if self._scroll_click(buy_button):
                            sleep(0.5)
                            self.select_session_and_price()

                            if self.click_confirm_button():
                                sleep(0.5)
                                
                                new_title = self.driver.title
                                print(new_title)
                                
                                if new_title == order_keywords:
                                    self.status = 3
                                    break
                                else:
                                    pass
                    # elif '缺货登记' in button_text:
                        # self.driver.refresh()
                        # sleep(0.5)
            
            if self.status >= 3:
                return self.check_order()
        return False

    
    def check_order(self):
        """Check and submit order"""
        submit_selector = (By.XPATH, '//span[contains(text(), "立即提交")]')
        submit_element = self._find_element(submit_selector)
        
        if submit_element:
            # buyer_selector = (By.XPATH, '//*[contains(text(), "观演人")]')
            # buyer = self._find_element(buyer_selector)
            # if buyer:
            #     # self._scroll_click(buyer)
            #     sleep(0.5)
            # sleep(0.5)
            
            if self._scroll_click(submit_element):
                print("submit clicked")
                # print(submit_element)
                for i in range(60, 0, -1):
                    sleep(0.5)
                return True
            
        return False


    def close(self):
        if self.driver:
            self.driver.quit()


    def select_session_and_price(self):
        """Select session and price"""
        session_selector = (By.XPATH, '//*[contains(text(), "2025-")]')
        session = self._find_element(session_selector)
        if session:
            self._scroll_click(session)
            sleep(0.5)
        
        price_selector = (By.XPATH, '//*[contains(text(), "元")]')
        price = self._find_element(price_selector)
        if price:
            self._scroll_click(price)
            sleep(0.5)
        
        return True


    def click_confirm_button(self):
        """Click confirm button"""
        confirm_selector = (By.XPATH, '//button[contains(text(), "确定")]')
        confirm_btn = self._find_element(confirm_selector)
        
        if confirm_btn:
            if self._scroll_click(confirm_btn):
                sleep(0.5)
                return True
        
        return False