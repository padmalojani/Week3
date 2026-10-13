import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class WebsiteCrawler:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TN-Schemes-RAG/1.0"
        })

    def fetch_scheme_listings(self) -> List[Dict[str, Any]]:
        """
        Opens the official Tamil Nadu Government scheme list URL, 
        extracts scheme listings, department names, and official detail-page URLs.
        """
        schemes = []
        try:
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()
            
            # Fix potential encoding issues for Tamil / regional text
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract department name or page title if available
            dept_heading = soup.find('h1') or soup.find('h2')
            department_name = dept_heading.get_text(strip=True) if dept_heading else "Tamil Nadu Government Department"

            # Parse scheme links from the listing page
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Filter out navigation links and retain likely scheme titles
                if text and len(text) > 15 and not href.startswith('#'):
                    detail_url = urljoin(self.base_url, href)
                    schemes.append({
                        "scheme_name_en": text,
                        "department": department_name,
                        "detail_url": detail_url,
                        "source_url": self.base_url
                    })
                    
        except Exception as e:
            logger.error(f"Error crawling website {self.base_url}: {e}")
            
        return schemes