import hashlib
import sqlite3
import os
from datetime import datetime
from typing import Dict, List
from ingestion.scraper import SchemeWebScraper

class SchemeIngestionPipeline:
    def __init__(self, db_path: str = "./data/metadata.db"):
        self.db_path = db_path
        self._init_db()
        self.scraper = SchemeWebScraper()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_schemes (
                scheme_id TEXT PRIMARY KEY,
                content_hash TEXT,
                last_verified TEXT,
                source_url TEXT
            )
        """)
        conn.commit()
        conn.close()

    def compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def run_sync(self, department_url: str) -> List[Dict]:
        listings = self.scraper.fetch_scheme_listing(department_url)
        processed = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in listings:
            scheme_id = hashlib.md5(item["scheme_name"].encode()).hexdigest()
            content_hash = self.compute_hash(item["scheme_name"])
            
            cursor.execute("SELECT content_hash FROM processed_schemes WHERE scheme_id = ?", (scheme_id,))
            row = cursor.fetchone()

            if not row or row[0] != content_hash:
                cursor.execute("""
                    INSERT OR REPLACE INTO processed_schemes (scheme_id, content_hash, last_verified, source_url)
                    VALUES (?, ?, ?, ?)
                """, (scheme_id, content_hash, datetime.utcnow().isoformat(), item.get("detail_url")))
                processed.append(item)

        conn.commit()
        conn.close()
        return processed