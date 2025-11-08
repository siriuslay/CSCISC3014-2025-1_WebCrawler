

import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import sqlite3
from config import settings
from utils.logger import log


class Database:
    
    def __init__(self):
        self.use_mongodb = False
        self._init_sqlite()
    
    
    def _init_sqlite(self):
        settings.SQLITE_DB.parent.mkdir(parents=True, exist_ok=True)
        
        self.sqlite_conn = sqlite3.connect(
            str(settings.SQLITE_DB),
            check_same_thread=False
        )
        self.sqlite_conn.row_factory = sqlite3.Row
        
        cursor = self.sqlite_conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concerts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT,
                venue TEXT,
                city TEXT,
                date TEXT,
                price TEXT,
                link TEXT,
                image TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concert_details (
                concert_id TEXT PRIMARY KEY,
                title TEXT,
                artist TEXT,
                venue TEXT,
                address TEXT,
                date TEXT,
                time TEXT,
                price_range TEXT,
                description TEXT,
                tags TEXT,
                images TEXT,
                tickets TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (concert_id) REFERENCES concerts (id)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON concerts(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_city ON concerts(city)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON concerts(date)")
        
        self.sqlite_conn.commit()
    

    def save_concerts(self, concerts: List[Dict]) -> int:

        if not concerts:
            return 0
        
        saved_count = 0
        
        for concert in concerts:
            concert['created_at'] = datetime.now()
            concert['updated_at'] = datetime.now()
            
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO concerts 
                (id, title, artist, venue, city, date, price, link, image, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                concert.get('id', ''),
                concert.get('title', ''),
                concert.get('artist', ''),
                concert.get('venue', ''),
                concert.get('city', ''),
                concert.get('date', ''),
                concert.get('price', ''),
                concert.get('link', ''),
                concert.get('image', ''),
                concert.get('status', ''),
                concert.get('created_at'),
                concert.get('updated_at'),
            ))
            self.sqlite_conn.commit()
            saved_count += 1
        return saved_count
    
    def save_concert_detail(self, detail: Dict) -> bool:
        
        if not detail:
            return False
        
        detail['created_at'] = datetime.now()
        concert_id = detail.get('id') or detail.get('concert_id')

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO concert_details
            (concert_id, title, artist, venue, address, date, time, 
                price_range, description, tags, images, tickets, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            concert_id,
            detail.get('title', ''),
            detail.get('artist', ''),
            detail.get('venue', ''),
            detail.get('address', ''),
            detail.get('date', ''),
            detail.get('time', ''),
            detail.get('price_range', ''),
            detail.get('description', ''),
            json.dumps(detail.get('tags', []), ensure_ascii=False),
            json.dumps(detail.get('images', []), ensure_ascii=False),
            json.dumps(detail.get('available_tickets', []), ensure_ascii=False),
            detail.get('created_at'),
        ))
        self.sqlite_conn.commit()
        return True
    
    def get_all_concerts(self, limit: int = 100) -> List[Dict]:
        
        concerts = []

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT * FROM concerts 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        concerts = [dict(row) for row in rows]

        
        return concerts
    
    def search_concerts(self, keyword: str, limit: int = 50) -> List[Dict]:
        
        concerts = []

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT * FROM concerts 
            WHERE title LIKE ? OR artist LIKE ? OR venue LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
        rows = cursor.fetchall()
        concerts = [dict(row) for row in rows]
        
        return concerts
    
    def get_concert_detail(self, concert_id: str) -> Optional[Dict]:
        
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                SELECT * FROM concert_details WHERE concert_id = ?
            """, (concert_id,))
            row = cursor.fetchone()
            if row:
                detail = dict(row)
                detail['tags'] = json.loads(detail.get('tags', '[]'))
                detail['images'] = json.loads(detail.get('images', '[]'))
                detail['available_tickets'] = json.loads(detail.get('tickets', '[]'))
                return detail
            return None
        except Exception as e:
            return None
    
    def get_statistics(self) -> Dict:
        
        stats = {
            'total_concerts': 0,
            'total_details': 0,
            'cities': [],
        }
        
        # if self.use_mongodb:

    #         stats['total_concerts'] = self.concerts_collection.count_documents({})
    #         stats['total_details'] = self.details_collection.count_documents({})
            
    #         pipeline = [
    #             {'$group': {'_id': '$city', 'count': {'$sum': 1}}},
    #             {'$sort': {'count': -1}},
    #             {'$limit': 10}
    #         ]
    #         cities = list(self.concerts_collection.aggregate(pipeline))
    #         stats['cities'] = [{'city': c['_id'], 'count': c['count']} for c in cities]

        # else:

        cursor = self.sqlite_conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM concerts")
        stats['total_concerts'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM concert_details")
        stats['total_details'] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT city, COUNT(*) as count 
            FROM concerts 
            WHERE city IS NOT NULL AND city != ''
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        stats['cities'] = [{'city': row[0], 'count': row[1]} for row in rows]
            
        
        return stats
    
    def close(self):
        self.sqlite_conn.close()



db = Database()
