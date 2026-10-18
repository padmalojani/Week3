
import requests
from bs4 import BeautifulSoup

URL = "https://www.bbc.com/news"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
}

try:
    # 1. Fetch the webpage
    response = requests.get(
        URL,
        headers=headers,
        timeout=15
    )

    # 2. Check the HTTP status before parsing
    response.raise_for_status()
    print(f"HTTP status: {response.status_code}")

    # 3. Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 4. Extract headlines using a CSS selector
    # Verify this selector in Chrome DevTools first.
    elements = soup.select("article h2")

    headlines = []
    seen = set()

    for element in elements:
        headline = element.get_text(" ", strip=True)

        if headline and headline not in seen:
            headlines.append(headline)
            seen.add(headline)

        if len(headlines) == 5:
            break

    # 5. Print the results
    if not headlines:
        print("No headlines found. Check the HTML and CSS selector.")
    else:
        print("\nTop BBC News Headlines:\n")

        for number, headline in enumerate(headlines, start=1):
            print(f"{number}. {headline}")

        if len(headlines) < 5:
            print(
                f"\nOnly {len(headlines)} unique headlines "
                "were found; expected 5."
            )

except requests.RequestException as error:
    print(f"Failed to fetch the webpage: {error}")
