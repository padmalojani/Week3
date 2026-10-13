import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TNgovSchemeLoader:
    def __init__(self, base_url: str = "https://www.tn.gov.in/"):
        self.base_url = base_url
        self.session = requests.Session()
        # Set a standard browser User-Agent to avoid blocking or 403 Forbidden responses
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ta;q=0.8"
        })

    def load_scheme_list(self, dep_id_url: str) -> List[Dict[str, Optional[str]]]:
        """
        Fetches the scheme listing page and parses out scheme titles, 
        detail page links, and available document attachments.
        """
        logger.info(f"Fetching data from URL: {dep_id_url}")
        
        try:
            response = self.session.get(dep_id_url, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            return []

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        extracted_schemes = []

        # Target scheme listing rows (adjust selectors based on exact page DOM structure)
        rows = soup.select("table tr")
        if not rows:
            # Fallback selector if list is formatted as divs or unorganized lists
            rows = soup.select(".scheme-item, .view-content tr")

        for idx, row in enumerate(rows):
            cols = row.find_all("td")
            if len(cols) >= 1:
                # Extract scheme name and link
                link_tag = cols[0].find("a")
                scheme_name = link_tag.get_text(strip=True) if link_tag else cols[0].get_text(strip=True)
                
                if not scheme_name:
                    continue

                relative_url = link_tag.get("href") if link_tag and link_tag.has_attr("href") else None
                detail_url = urljoin(self.base_url, relative_url) if relative_url else None

                # Look for downloadable guidelines or PDF links within the row or detail view
                pdf_links = []
                for a_tag in row.find_all("a", href=True):
                    href = a_tag["href"]
                    if ".pdf" in href.lower():
                        pdf_links.append(urljoin(self.base_url, href))

                extracted_schemes.append({
                    "index": idx,
                    "scheme_name": scheme_name,
                    "detail_url": detail_url,
                    "supporting_docs": pdf_links
                })

        logger.info(f"Successfully extracted {len(extracted_schemes)} schemes from department listing.")
        return extracted_schemes

    def fetch_scheme_detail_page(self, detail_url: str) -> Dict[str, str]:
        """
        Deep-dives into an individual scheme's detail page to extract descriptions,
        eligibility requirements, and application procedures.
        """
        if not detail_url:
            return {}

        try:
            response = self.session.get(detail_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract main content body text safely
            content_div = soup.find("div", class_="content") or soup.find("main") or soup.body
            text_content = content_div.get_text(separator="\n", strip=True) if content_div else ""

            return {
                "source_url": detail_url,
                "raw_text": text_content
            }
        except Exception as e:
            logger.warning(f"Could not load detail page {detail_url}: {e}")
            return {}

# Example execution snippet
if __name__ == "__main__":
    loader = TNgovSchemeLoader()
    target_url = "https://www.tn.gov.in/scheme_list.php?dep_id=Mg=="
    
    schemes = loader.load_scheme_list(target_url)
    for scheme in schemes[:3]:  # Print first 3 discovered entries
        print(scheme)