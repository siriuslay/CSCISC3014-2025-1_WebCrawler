import requests
import json
import time
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

from config import settings
from utils.logger import log


class DamaiScraper:
    """
    - Damai mtop API
    - generate sign
    - Cookie management
    - multi-page scraping
    """
    
    def __init__(self, cookie_str: str = ""):
        self.base_url = "https://mtop.damai.cn/h5/mtop.damai.wireless.search.search/1.0/"  # mobile search URL
        # self.base_url = "https://search.damai.cn/searchajax.html"   # PC search URL
        self.app_key = "12574478"
        self.session = requests.Session()
        
        # cookies
        if cookie_str:
            self._set_cookies_from_string(cookie_str)
        else:
            self._load_cookies()
        
        # headers
        self.headers = {
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
        
        self.stats = {
            'requests': 0,
            'success': 0,
            'failed': 0,
        }
        
        log.info("DamaiScraper initialized")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _set_cookies_from_string(self, cookie_str: str):
        cookie_dict = {}
        for item in cookie_str.split('; '):
            if '=' in item:
                key, value = item.split('=', 1)
                cookie_dict[key] = value
        
        for key, value in cookie_dict.items():
            self.session.cookies.set(key, value, domain='.damai.cn')
        
        log.debug(f"Set {len(cookie_dict)} cookies")
    
    def _load_cookies(self):
        if settings.COOKIE_FILE.exists():
            with open(settings.COOKIE_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if isinstance(cookies, list):
                # Selenium format: [{name, value, domain}, ...]
                for cookie in cookies:
                    self.session.cookies.set(
                        cookie['name'], 
                        cookie['value'], 
                        domain=cookie.get('domain', '.damai.cn')
                    )
            elif isinstance(cookies, dict):
                # {name: value, ...}
                for name, value in cookies.items():
                    self.session.cookies.set(name, value, domain='.damai.cn')
            
            log.info("Load cookies from file")
    
    def _save_cookies(self):
        """Save cookies"""
        settings.COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        cookies = self.session.cookies.get_dict()
        with open(settings.COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        
        log.debug("cookies saved to file")
    
    def _get_token(self) -> str:
        cookies = self.session.cookies.get_dict()
        token = cookies.get('_m_h5_tk', '')
        if '_' in token:
            return token.split('_')[0]
        return token
    
    def _generate_sign(self, t: str, data_str: str) -> str:
        token = self._get_token()
        sign_str = f"{token}&{t}&{self.app_key}&{data_str}"
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def _search_page(self, keyword: str, city: str = "全国", page: int = 1, page_size: int = 10) -> Optional[Dict]:
        city_id_map = {
            "全国": 0,
            "北京": 110100,
            "上海": 310100,
            "广州": 440100,
            "深圳": 440300,
            "杭州": 330100,
            "成都": 510100,
            "重庆": 500100,
            "南京": 320100,
            "武汉": 420100,
        }
        city_id = city_id_map.get(city, 0)
        
        data_dict = {
            "cityId": city_id,
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
        
        params = {
            "jsv": "2.7.5",
            "appKey": self.app_key,
            "t": t,
            "sign": sign,
            "api": "mtop.damai.wireless.search.search",
            "v": "1.0",
            "H5Request": "true",
            "type": "originaljson",
            "timeout": "10000",
            "dataType": "json",
            "valueType": "original",
            "forceAntiCreep": "true",
            "AntiCreep": "true",
            "data": data_str
        }
        
        self.stats['requests'] += 1
        
        response = self.session.get(
            self.base_url,
            params=params,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("ret") and result["ret"][0].startswith("SUCCESS"):
            self.stats['success'] += 1
            return result
        else:
            self.stats['failed'] += 1
            log.warning(f"API return error: {result.get('ret', 'Unknown error')}")
            return None
                
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
    
    def search_concerts(self, keyword: str, city: str = "全国", max_pages: int = 5, page_size: int = 10) -> List[Dict]:
        log.info(f"Search begin: '{keyword}', '{city}', Max pages: {max_pages}")
        
        all_concerts = []
        
        for page in range(1, max_pages + 1):
            result = self._search_page(keyword, city, page, page_size)
            
            if result:
                data = result.get("data", {})
                projects = data.get("projectInfo", [])
                total = data.get("total", 0)
                
                log.info(f" {len(projects)} / {total} data")
                
                if len(projects) == 0:
                    log.info("No more data, stopping.")
                    break
                
                for project in projects:
                    parsed = self._parse_project_info(project)
                    all_concerts.append(parsed)
                    
                    name_display = parsed['title'][:30] + "..." if len(parsed['title']) > 30 else parsed['title']
                    log.debug(f"    - {name_display}")
            else:
                log.warning(f"{page} page fetch failed, retrying after delay...")
                time.sleep(2)
                continue

            if page < max_pages:
                delay = settings.REQUEST_DELAY_MIN if hasattr(settings, 'REQUEST_DELAY_MIN') else 2
                time.sleep(delay)
        
        log.success(f"complete！Get {len(all_concerts)} records")
        
        return all_concerts
    
    def get_concert_detail(self, concert_url: str) -> Optional[Dict]:
    
        return None
    
    def close(self):
        self.session.close()
        log.info("DamaiScraper Closed")

def quick_search(keyword: str, city: str = "全国", **kwargs) -> List[Dict]:
    
    with DamaiScraper() as scraper:
        return scraper.search_concerts(keyword, city, **kwargs)


def quick_detail(concert_url: str) -> Optional[Dict]:
    
    with DamaiScraper() as scraper:
        return scraper.get_concert_detail(concert_url)


def main():

    import sys
    
    if len(sys.argv) < 2:

        return
    
    keyword = sys.argv[1]
    city = sys.argv[2] if len(sys.argv) > 2 else "全国"
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    try:
        concerts = quick_search(keyword, city, max_pages=max_pages)
        
        print("=" * 80)
        
        for i, concert in enumerate(concerts, 1):
            print(f"\n{i}. {concert.get('title', 'Unknown')}")
            print(f"   ID: {concert.get('id', 'N/A')}")
            print(f"   艺人: {concert.get('artist', 'Unknown')}")
            print(f"   场馆: {concert.get('venue', 'Unknown')}")
            print(f"   城市: {concert.get('city', 'Unknown')}")
            print(f"   日期: {concert.get('date', 'Unknown')}")
            print(f"   价格: {concert.get('price', 'Unknown')}")
            print(f"   状态: {concert.get('status', 'Unknown')}")
            print(f"   链接: {concert.get('link', 'Unknown')}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
