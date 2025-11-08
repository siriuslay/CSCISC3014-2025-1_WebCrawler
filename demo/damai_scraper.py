import requests
import json
import time
from typing import List, Dict, Optional
import hashlib

API = "https://mtop.damai.cn/h5/mtop.damai.wireless.search.search/1.0/"
APP_KEY = "12574478"
REQ_HEADER = {
            "accept": "application/json",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://m.damai.cn",
            "referer": "https://m.damai.cn/shows/search.html",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }
REQ_PARAMS = {
            "t": "",
            "sign": "",
            "data": "",

            "jsv": "2.7.5",
            "appKey": APP_KEY,
            "api": "mtop.damai.wireless.search.search",
            "v": "1.0",
            "H5Request": "true",
            "type": "originaljson",
            "timeout": "10000",
            "dataType": "json",
            "valueType": "original",
            "forceAntiCreep": "true",
            "AntiCreep": "true",
        }


class DamaiScraper:
    
    def __init__(self, cookie_str: str = ""):
        self.base_url = API  # mobile search URL
        self.app_key = APP_KEY
        self.session = requests.Session()
        # headers
        self.headers = REQ_HEADER
        
        self.stats = {
            'requests': 0,
            'success': 0,
            'failed': 0,
        }
        # cookies
        self._set_cookies_from_string(cookie_str)
    
    def _generate_sign(self, t: str, data_str: str) -> str:
        token = self.session.cookies.get('_m_h5_tk', '')
        if '_' in token:
            token = token.split('_')[0]
        sign_str = f"{token}&{t}&{self.app_key}&{data_str}"
        return hashlib.md5(sign_str.encode()).hexdigest()


    def _set_cookies_from_string(self, cookie_str: str):
        cookie_dict = {}
        for item in cookie_str.split('; '):
            if '=' in item:
                key, value = item.split('=', 1)
                cookie_dict[key] = value
        
        for key, value in cookie_dict.items():
            self.session.cookies.set(key, value, domain='.damai.cn')
        

    def _parse_project_info(self, project: Dict) -> Dict:
        return {
            "id": project.get("id", ""),
            "title": project.get("name", ""),
            "city": project.get("cityName", ""),
            "venue": project.get("venueName", ""),
            "date": project.get("showTime", ""),
            "price": project.get("priceStr", ""),
            "artist": project.get("actores", ""),
            "category": project.get("categoryName", ""),
            "sub_category": project.get("guideSubCategoryName", ""),
            "views": project.get("ipvuv", 0),
            "status": project.get("showStatus", {}).get("desc", ""),
            "link": f"https://m.damai.cn/damai/detail/item.html?itemId={project.get('id', '')}",
            "image": project.get("verticalPic", ""),
        }

    def _search_page(self, keyword: str, page: int = 1, page_size: int = 10) -> Optional[Dict]:
        
        data_dict = {
            "cityId": 0,
            "longitude": 0,
            "latitude": 0,
            "pageIndex": page,
            "pageSize": page_size,
            "keyword": keyword,
            "sourceType": 11,
            "returnItemOption": 4,
            "distanceCityId": "852",
            "option": 434,
            "platform": "8",
            "comboChannel": "2",
            "dmChannel": "damai@damaih5_h5"
        }
        
        data_str = json.dumps(data_dict, separators=(',', ':'), ensure_ascii=False)
        t = str(int(time.time() * 1000))
        sign = self._generate_sign(t, data_str)
        
        REQ_PARAMS["t"] = t
        REQ_PARAMS["sign"] = sign
        REQ_PARAMS["data"] = data_str
        
        self.stats['requests'] += 1
        
        response = self.session.get(
            self.base_url,
            params=REQ_PARAMS,
            headers=self.headers,
            timeout=10
        )
        # print(response)
        response.raise_for_status()
        result = response.json()
        
        if result.get("ret") and result["ret"][0].startswith("SUCCESS"):
            self.stats['success'] += 1
            return result
        else:
            self.stats['failed'] += 1
            return None

    def search_concerts(self, keyword: str, max_pages: int = 5, page_size: int = 10) -> List[Dict]:
        all_concerts = []
        for page in range(1, max_pages + 1):
            result = self._search_page(keyword, page, page_size)

            # print(result)
            
            if result:
                data = result.get("data", {})
                projects = data.get("projectInfo", [])
                total = data.get("total", 0)

                for project in projects:
                    parsed = self._parse_project_info(project)
                    all_concerts.append(parsed)

        return all_concerts
    
    def close(self):
        self.session.close()