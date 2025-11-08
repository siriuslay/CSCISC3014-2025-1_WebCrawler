
import time
from typing import Optional, Dict
import requests
from config import settings
from utils.logger import log


class CaptchaSolver:
    
    def __init__(self):
        self.api_key = settings.CAPSOLVER_API_KEY if hasattr(settings, 'CAPSOLVER_API_KEY') else ""
        self.create_task_url = "https://api.capsolver.com/createTask"
        self.get_result_url = "https://api.capsolver.com/getTaskResult"
    
    def solve_recaptcha_v2(self, 
                          website_url: str, 
                          website_key: str,
                          proxy: Optional[str] = None) -> Optional[str]:
        
        if not self.api_key:
            return None
        
        try:
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ReCaptchaV2TaskProxyless",
                    "websiteURL": website_url,
                    "websiteKey": website_key,
                }
            }

            if proxy:
                task_data["task"]["type"] = "ReCaptchaV2Task"
                task_data["task"]["proxy"] = proxy
            
            response = requests.post(self.create_task_url, json=task_data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errorId") != 0:
                return None
            
            task_id = result.get("taskId")
            
            max_attempts = 60
            for attempt in range(max_attempts):
                time.sleep(3)
                
                result_response = requests.post(
                    self.get_result_url,
                    json={"clientKey": self.api_key, "taskId": task_id},
                    timeout=30
                )
                result_data = result_response.json()
                
                if result_data.get("status") == "ready":
                    token = result_data.get("solution", {}).get("gRecaptchaResponse")
                    return token
                    
                elif result_data.get("status") == "processing":
                    continue
                else:
                    return None

            return None
            
        except Exception as e:
            return None
    
    def solve_recaptcha_v3(self,
                          website_url: str,
                          website_key: str,
                          page_action: str = "submit",
                          min_score: float = 0.9) -> Optional[str]:
        
        if not self.api_key:
            return None
        
        try:
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ReCaptchaV3TaskProxyless",
                    "websiteURL": website_url,
                    "websiteKey": website_key,
                    "pageAction": page_action,
                    "minScore": min_score,
                }
            }
            
            response = requests.post(self.create_task_url, json=task_data, timeout=30)
            result = response.json()
            
            if result.get("errorId") != 0:
                return None
            
            task_id = result.get("taskId")
            
            for attempt in range(40):
                time.sleep(3)
                
                result_response = requests.post(
                    self.get_result_url,
                    json={"clientKey": self.api_key, "taskId": task_id},
                    timeout=30
                )
                result_data = result_response.json()
                
                if result_data.get("status") == "ready":
                    token = result_data.get("solution", {}).get("gRecaptchaResponse")
                    score = result_data.get("solution", {}).get("score", 0)
                    return token
                    
                elif result_data.get("status") == "processing":
                    continue
                else:
                    return None
            
            return None
            
        except Exception as e:
            return None
    
    def solve_slider_captcha(self, 
                            website_url: str,
                            image_url: str = "") -> Optional[Dict]:
        
        if not self.api_key:
            time.sleep(30)
            return {'manual': True}

        time.sleep(30)
        
        return {'manual': True}
    
    def solve_click_captcha(self, 
                           website_url: str,
                           image_url: str = "") -> Optional[Dict]:
        
        if not self.api_key:
            time.sleep(30)
            return {'manual': True}
        
        time.sleep(30)
        
        return {'manual': True}
    
    def solve_text_captcha(self, image_path: str) -> Optional[str]:
        
        try:
            
            time.sleep(30)
            
            return None
            
        except Exception as e:

            return None
    
    def wait_for_manual_solve(self, timeout: int = 30) -> bool:
        
        time.sleep(timeout)
        return True
    
    def get_balance(self) -> Optional[float]:
        
        if not self.api_key:
            return None
        
        try:
            url = "https://api.capsolver.com/getBalance"
            response = requests.post(
                url,
                json={"clientKey": self.api_key},
                timeout=10
            )
            result = response.json()
            
            if result.get("errorId") == 0:
                balance = result.get("balance", 0)
                return balance
            else:
                return None
                
        except Exception as e:
            return None

captcha_solver = CaptchaSolver()


def solve_captcha(captcha_type: str, **kwargs) -> Optional[any]:
    
    if captcha_type == 'recaptcha_v2':
        return captcha_solver.solve_recaptcha_v2(**kwargs)
    elif captcha_type == 'recaptcha_v3':
        return captcha_solver.solve_recaptcha_v3(**kwargs)
    elif captcha_type == 'slider':
        return captcha_solver.solve_slider_captcha(**kwargs)
    elif captcha_type == 'click':
        return captcha_solver.solve_click_captcha(**kwargs)
    elif captcha_type == 'text':
        return captcha_solver.solve_text_captcha(**kwargs)
    else:
        return None