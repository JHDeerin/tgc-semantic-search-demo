"""Utilities for scraping article data from The Gospel Coalition website."""
from datetime import datetime
import re
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclass
class ArticleData:
    """Data from a TGC article post."""
    title: str
    author: str
    publish_datetime: datetime
    text: List[str]
    url: str


def parse_article_urls(html: str) -> List[str]:
    """Return all the TGC article URLs that appear in the given HTML."""
    soup = BeautifulSoup(html, features="html.parser")
    article_urls = soup.find_all("a", href=re.compile("/article"))
    return [url["href"] for url in article_urls]


def search_tgc(max_posts: int) -> str:
    """Run a search on recent TGC articles and return the resulting search page HTML."""
    search_url = f"https://www.thegospelcoalition.org/wp-content/themes/sage/tgc-ajax.php?action=search_load_more&post_id=&args%5Bs%5D=&args%5Border%5D=DESC&args%5Borderby%5D=post_date&page=1&posts_per_page={max_posts}"
    # User-Agent header required, or else we get a 403 error
    res = requests.get(search_url, headers={"User-Agent": "Requests/2.31.0"})
    assert res.status_code < 400
    return res.json()["data"]["html"]


def parse_article(article_html: str) -> ArticleData:
    soup = BeautifulSoup(article_html, features="html.parser")
    title = soup.find("title").text
    author = soup.find("article").find("span", class_="author").text
    paragraphs = soup.find("article").find_all("p")
    publish_datetime = datetime.fromisoformat(
        soup.find("article").find("time")["datetime"]
    )
    article_url = soup.find("link", rel=re.compile("canonical"))["href"]

    return ArticleData(
        title=title,
        author=author.strip(),
        publish_datetime=publish_datetime,
        text=[p.text for p in paragraphs],
        url=article_url
    )


def fetch_article(url: str) -> ArticleData:
    """Fetch the given article's data from the TGC website."""
    res = requests.get(url)
    assert res.status_code < 400
    return parse_article(res.text)
