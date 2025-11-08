
import os
from pathlib import Path
from typing import List, Optional


class Settings:
    
    # ========== basic ==========
    PROJECT_NAME: str = "Damai Tickets Scraper"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ========== crawer ==========
    TARGET_URL: str = "https://m.damai.cn"   # We use mobile site to scrape
    SEARCH_URL: str = "https://m.damai.cn/shows/search.html"   # We use mobile search page to find events
    COOKIE: str = "cna=Z7uMIWTgm1wCAcqvQ/aPW6T8; t=eff921da1068482372783cf712ceabef; munb=2217727089916; damai.cn_nickName=%E9%BA%A6%E5%AD%907yojn; dm_nickname=%E9%BA%A6%E5%AD%907yojn; usercode=486294353; havanaId=2217727089916; xlly_s=1; tfstk=g_aqeXA1uZQ2xIJ5l83wTtdI4RgxoVWC_PMss5ViGxD0G5cZ78waGcXY18kgH8pXlqqjsFySFRT_GROY2JNHlrsx5FuxWVXCdwgNMS3tS7wlfO9vEXcF5nmmmq3llgEdLw_QMSdji6NlRoZvVHGsIVmmn7VoeXtDIRmmZbD-6fvmsEfzZYHkoIcDSamoOj-MjR0Ga7D-sVc0ImfzZYhiSADFmADBzXocNvKTbUs6MqH3iY8M8BhmmLV2fF8azjo4S5krsf4rgqknbv2X1r27srax29JnW7ZUQl2OA334so0mOSQ2z2V0VPl751tZn-UzZrnyTeuam-rivu7pvmmZ3u4m4CYgw4qoblyV3nH0c8oKZ0ANJbwIESU041puiJMqobm5-6Pojuaxvr6ku2qLGqZgBMt-u5qmzgJvBbbGfPE2IhomwbkCa_88T-hkxJ04HhKtDuhrdsCvXhnmwbkCa_-9Xm3-av1AM; mtop_partitioned_detect=1; _m_h5_tk=45c3f826fc947d00c40e4916bad7e2f3_1762561197312; _m_h5_tk_enc=4410f32ce51036100581b23d169e0ed6"
    # We use cookie string for authenticated requests
    
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_DELAY_MIN: float = 1.0
    REQUEST_DELAY_MAX: float = 3.0
    
    USER_AGENTS: List[str] = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    ]
    
    # ========== agent ==========
    USE_PROXY: bool = os.getenv("USE_PROXY", "false").lower() == "true"
    PROXY_URL: Optional[str] = os.getenv("PROXY_URL")
    PROXY_POOL: List[str] = []
    PROXY_ROTATION: bool = True
    
    # ========== anti-detect ==========
    USE_STEALTH: bool = True
    HEADLESS: bool = True
    USE_CURL_CFFI: bool = True
    IMPERSONATE_BROWSER: str = "chrome120"

    # COOKIE: str = "cna=3aWPISdRbH8CAcqvQ+mdXJou; xlly_s=1; mtop_partitioned_detect=1; _m_h5_tk=83d60ee54f0a51f05133293da65ef068_1762188804166; _m_h5_tk_enc=8b5a9e29989f109f89413b5ee89795bf; XSRF-TOKEN=425e90d1-766a-4f7c-a938-560374551a8a; isg=BJeXuj7qsubzaTZqbiruLluYJgvh3Gs-qRKcsenHfWbNGLNa_65Ujnl7ergG9kO2; tfstk=gzYiBHjZlhS6mUz_jjbsjFpsAZnp1N_fhKUAHZBqY9WQWhn1DtVcKLl1Xct9xtvhdPKtfiB0i9vakGpvoHaDNITt1Zh15C_fuYH-yKA61ZwdP7OSpBlVGZfaAoES5C_fuvH-y4d61dQwVvxNuXbFisaNuO7VLXfVwZzN0PrUL91VuZJVuXxBHeQV3KSZtBWCgZW23ZkC2cW6ue8Ehn9jEHqLvefGjT4AKr4mM1jGUCWhO6TElGXy_94qIU00KtXBzvnHOH-wB69mrvbXdnJVipyEHGO2xpfMBY2fHFO9oOdibAOh8OvNjHczf6ApSIxVxfuwtNXG2evaZk7M0dTcfhVjNB7wd365bDMCtFLRmTs3LARptOSkmdHQuOKkTpjJJJURlpt23svUIgWaYuko5r1EMerbcG5CtTK0GUrrAlFFtXc34jsNO16-tXqbcG5CtThntuufb611e"
    COOKIE_FILE: Path = Path("cookies.json")
    
    # ========== captcha ==========
    CAPSOLVER_API_KEY: str = os.getenv("CAPSOLVER_API_KEY", "")
    AUTO_SOLVE_CAPTCHA: bool = False
    
    # ========== sql ==========
    # MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    # MONGO_DB: str = "damai_scraper"
    SQLITE_DB: Path = Path("data/damai.db")
    

    # ========== log ==========
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("logs/scraper.log")
    LOG_ROTATION: str = "500 MB"
    LOG_RETENTION: str = "10 days"
    
    # ========== Streamlit ==========
    STREAMLIT_THEME: str = "dark"
    PAGE_TITLE: str = "Tickets Scraper"
    PAGE_ICON: str = "🎫"
    LAYOUT: str = "wide"


settings = Settings()


def ensure_directories():
    directories = [Path("logs"), Path("data"), Path("screenshots"), Path("exports")]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


ensure_directories()
