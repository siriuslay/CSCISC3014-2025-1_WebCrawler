
from demo.damai_scraper import DamaiScraper
import csv

keyword = "music"

TARGET_URL: str = "https://m.damai.cn"   # We use mobile site to scrape
SEARCH_URL: str = "https://m.damai.cn/shows/search.html"   # We use mobile search page to find events
COOKIE: str = "cna=Z7uMIWTgm1wCAcqvQ/aPW6T8; t=eff921da1068482372783cf712ceabef; munb=2217727089916; damai.cn_nickName=%E9%BA%A6%E5%AD%907yojn; dm_nickname=%E9%BA%A6%E5%AD%907yojn; usercode=486294353; havanaId=2217727089916; cookie2=131ba03ea7d59fe8a0ee6fea0ebde6fa; _tb_token_=e18beee4e53de; _samesite_flag_=true; _hvn_login=18; sgcookie=E100IlOLEEDrTkMb0a0ZNwszXcb6f0lnBwyAzwWl%2F2tga7BpIARgWXo5%2B53oSJBV73GaixZ6r2k%2F3nKU5Hnl9mwkKoXOm0WSyEEZtTLhE2bYROU%3D; csg=7cbd8578; damai.cn_user=vqMZUEZdyv2g6+QlUfCOW4ImtAjp2Y2UR2WCRIxqPkO5PMPxOtazxrFpmq0zxzoJGxb2+Rjuqig=; damai.cn_user_new=vqMZUEZdyv2g6%2BQlUfCOW4ImtAjp2Y2UR2WCRIxqPkO5PMPxOtazxrFpmq0zxzoJGxb2%2BRjuqig%3D; h5token=92a5829164b846c291dd100f61d6ced6_1_1; damai_cn_user=vqMZUEZdyv2g6%2BQlUfCOW4ImtAjp2Y2UR2WCRIxqPkO5PMPxOtazxrFpmq0zxzoJGxb2%2BRjuqig%3D; loginkey=92a5829164b846c291dd100f61d6ced6_1_1; user_id=486294353; isg=BCMjFpLMTgSdfQIwNK6vT4S5smfNGLdaHQ6IjVWA_QLUlEK21OsbqhfXiGSaNA9S; xlly_s=1; tfstk=gDSmHVY4fZ8XU_ijoRxbo1YB_64-Mnt661n96hdazQRWkFP_lGxGMQIvWnRxI1XFCIWv6-sGrs6ekhIGCcvNQ1wX6-aRhtt6bWdGskBfhzwqrdFJbRWyXdXuZJrhhtt6bYhaJaWbj3m51d-N_38yHptZ7K8aE3Jpnho27muraQ9wbh82_QuyId3Z_K8aETRWQhRN_hyk4Q9wbC5wbxTQuIsN4gP13jI4s1cd1KYDTtRVHtIzVE3f3Qb5rgvcEBWqzcoNqIYcqOqCuaYA79TCDiriVnBhz3JdhomkYtJhMQCUY0xPeT59RaNsvU1ljes2uAyyaiflcn5Y7DfHm1YF0UDZXtWya3vPYR3BwgAA_iYzpDY94MLe0aU7MFKDK1SfiAmNTTBdcUsgtbR1kptyptZmqHW2Qg7iz2P3cc9zBgus5EJWEBQiCMuEITqcY82o8RT2FKOLE80s5EJWEBeuE2r6uL9X9; mtop_partitioned_detect=1; _m_h5_tk=b9249b4bd23821dd9d2983469ed1f8ac_1762593922499; _m_h5_tk_enc=4d2ee8a3e1918714075e37c3c8ccc280"
# We use cookie string for authenticated requests


scraper = DamaiScraper(cookie_str=COOKIE)
concerts = scraper.search_concerts(
    keyword=keyword,
    max_pages=10,
    page_size=10
)
scraper.close()

filename = f"damai_music.csv"
        
fieldnames = [
    'id', 'title', 'artist', 'venue', 'city', 'date', 
    'price', 'category', 'sub_category', 'status', 
    'views', 'image', 'link'
]

# Write to CSV
with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    writer.writeheader()
    
    for concert in concerts:
        row = {field: concert.get(field, '') for field in fieldnames}
        writer.writerow(row)