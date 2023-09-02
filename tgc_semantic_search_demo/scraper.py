"""Utilities for scraping article data from The Gospel Coalition website."""
import re
from typing import List

import requests
from bs4 import BeautifulSoup


def parse_article_urls(html: str) -> List[str]:
    """Return all the TGC article URLs that appear in the given HTML."""
    soup = BeautifulSoup(html)
    article_urls = soup.find_all("a", href=re.compile("/article"))
    return [url["href"] for url in article_urls]


def search_tgc(max_posts: int) -> str:
    """Run a search on recent TGC articles and return the resulting search page HTML."""
    search_url = f"https://www.thegospelcoalition.org/wp-content/themes/sage/tgc-ajax.php?action=search_load_more&post_id=&args%5Bs%5D=&args%5Border%5D=DESC&args%5Borderby%5D=post_date&page=1&posts_per_page={max_posts}"
    # User-Agent header required, or else we get a 403 error
    res = requests.get(search_url, headers={"User-Agent": "Requests/2.31.0"})
    return res.json()["data"]["html"]