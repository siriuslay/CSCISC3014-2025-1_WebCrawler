

import random
import time
from typing import Optional, Dict, Any
from config import settings
from utils.logger import log

try:
    from playwright_stealth import stealth_sync
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False

try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False


class AntiDetection:
    
    def __init__(self):
        if FAKE_UA_AVAILABLE:
            try:
                self.ua = UserAgent()
            except:
                self.ua = None
        else:
            self.ua = None
        
        self.user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
        ]
    
    def get_random_user_agent(self) -> str:
        if self.ua:
            try:
                return self.ua.random
            except:
                pass
        return random.choice(self.user_agents)
    
    def get_stealth_headers(self) -> Dict[str, str]:
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        return headers
    
    def setup_stealth_page(self, page: Any) -> Any:
        if STEALTH_AVAILABLE:
            stealth_sync(page)
        return page
    
    def random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def human_like_mouse_move(self, page: Any, element: Any):
        box = element.bounding_box()
        if not box:
            return
        
        target_x = box['x'] + random.uniform(5, box['width'] - 5)
        target_y = box['y'] + random.uniform(5, box['height'] - 5)
        
        steps = random.randint(8, 15)
        for i in range(steps):
            progress = (i + 1) / steps
            x = target_x * progress + random.uniform(-2, 2)
            y = target_y * progress + random.uniform(-2, 2)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.01, 0.03))

    
    def simulate_human_behavior(self, page: Any):
        for _ in range(random.randint(2, 4)):
            scroll_y = random.randint(100, 500)
            page.evaluate(f"window.scrollBy(0, {scroll_y})")
            time.sleep(random.uniform(0.5, 1.5))


anti_detect = AntiDetection()