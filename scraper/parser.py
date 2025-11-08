

from typing import List, Dict, Optional
import json
from utils.logger import log


class DamaiParser:
    
    @staticmethod
    def parse_api_response(response_data: Dict) -> List[Dict]:
        
        concerts = []
        

        ret = response_data.get("ret", [])
        if not ret or not ret[0].startswith("SUCCESS"):
            return concerts

        data = response_data.get("data", {})
        projects = data.get("projectInfo", [])
        
        if not projects:

            return concerts

        for project in projects:
            try:
                concert = DamaiParser._parse_project(project)
                if concert:
                    concerts.append(concert)
            except Exception as e:

                continue

        return concerts
    
    @staticmethod
    def _parse_project(project: Dict) -> Optional[Dict]:
        
        try:
            concert = {
                "id": str(project.get("id", "")),
                "title": project.get("name", ""),
                "artist": project.get("actores", ""),
                "venue": project.get("venueName", ""),
                "city": project.get("cityName", ""),
                "date": project.get("showTime", ""),
                "price": project.get("priceStr", ""),
            }
            
            concert["category"] = project.get("categoryName", "")
            concert["sub_category"] = project.get("guideSubCategoryName", "")
            
            show_status = project.get("showStatus", {})
            if isinstance(show_status, dict):
                concert["status"] = show_status.get("desc", "")
            else:
                concert["status"] = ""
            
            concert["image"] = project.get("verticalPic", "") or project.get("horizontalPic", "")
            
            concert["views"] = project.get("ipvuv", 0)
            
            item_id = project.get("id", "")
            concert["link"] = f"https://m.damai.cn/damai/detail/item.html?itemId={item_id}" if item_id else ""
            
            if not concert["title"]:
                return None
            
            return concert
            
        except Exception as e:
            return None
    
    @staticmethod
    def parse_search_result(result: Dict) -> Dict:
        
        try:
            data = result.get("data", {})
            
            stats = {
                "total": data.get("total", 0),
                "page_index": data.get("pageIndex", 0),
                "page_size": data.get("pageSize", 0),
                "has_more": data.get("hasMore", False),
                "count": len(data.get("projectInfo", [])),
            }
            
            return stats
            
        except Exception as e:

            return {
                "total": 0,
                "page_index": 0,
                "page_size": 0,
                "has_more": False,
                "count": 0,
            }
    
    @staticmethod
    def extract_concert_ids(concerts: List[Dict]) -> List[str]:
        
        return [c.get("id", "") for c in concerts if c.get("id")]
    
    @staticmethod
    def filter_by_city(concerts: List[Dict], city: str) -> List[Dict]:
        
        if city == "全国" or not city:
            return concerts
        
        return [c for c in concerts if c.get("city") == city]
    
    @staticmethod
    def filter_by_status(concerts: List[Dict], status: str = "在售") -> List[Dict]:
       
        if not status:
            return concerts
        
        return [c for c in concerts if status in c.get("status", "")]
    
    @staticmethod
    def sort_by_date(concerts: List[Dict], reverse: bool = False) -> List[Dict]:
        
        try:
            return sorted(
                concerts,
                key=lambda x: x.get("date", ""),
                reverse=reverse
            )
        except Exception as e:
            return concerts
    
    @staticmethod
    def get_city_distribution(concerts: List[Dict]) -> Dict[str, int]:
       
        distribution = {}
        
        for concert in concerts:
            city = concert.get("city", "未知")
            distribution[city] = distribution.get(city, 0) + 1
        
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    @staticmethod
    def get_price_range(concerts: List[Dict]) -> Dict[str, float]:
        
        prices = []
        
        for concert in concerts:
            price_str = concert.get("price", "")
            try:
                import re
                numbers = re.findall(r'\d+', price_str)
                if numbers:
                    prices.append(float(numbers[0]))
            except:
                continue
        
        if not prices:
            return {"min": 0, "max": 0, "avg": 0}
        
        return {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices)
        }


parser = DamaiParser()


def parse_concerts(response_data: Dict) -> List[Dict]:
   
    return parser.parse_api_response(response_data)


def get_statistics(concerts: List[Dict]) -> Dict:
    
    return {
        "total": len(concerts),
        "cities": parser.get_city_distribution(concerts),
        "price": parser.get_price_range(concerts),
    }
