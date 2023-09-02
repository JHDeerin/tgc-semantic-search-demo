"""Utilities for scraping article data from The Gospel Coalition website."""
import re
from typing import List

from bs4 import BeautifulSoup


def get_article_urls(html: str) -> List[str]:
    """Return all the TGC article URLs that appear in the given HTML."""
    # TODO: Implement this!
    soup = BeautifulSoup(html)
    article_urls = soup.find_all("a", href=re.compile("/article"))
    return [url["href"] for url in article_urls]