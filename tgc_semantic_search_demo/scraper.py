"""Utilities for scraping article data from The Gospel Coalition website."""
import dataclasses
import json
import logging
import os
import re
import string
import time
from datetime import datetime
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclasses.dataclass
class ArticleData:
    """Data from a TGC article post."""
    title: str
    author: str
    publish_datetime: datetime
    text: List[str]
    url: str

    def to_json(self) -> dict:
        data = dataclasses.asdict(self)
        data["publish_datetime"] = self.publish_datetime.isoformat()
        return data


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
    if res.status_code >= 400:
        raise requests.exceptions.HTTPError(response=res)
    return res.json()["data"]["html"]


def parse_article(article_html: str) -> ArticleData:
    soup = BeautifulSoup(article_html, features="html.parser")
    title = soup.find("title").text
    author = soup.find("article").find("span", class_="author").text
    paragraphs = soup.find("article").find("div", class_="content_container").find_all("p")
    text_paragraphs = [
        p for list in [p.text.split("\n") for p in paragraphs] for p in list
    ]
    text_paragraphs = [p for p in text_paragraphs if p.strip()]
    # remove duplicate paragraphs
    # TODO: Find the bug that introduces duplicate paragrpahs in the first place
    text_paragraphs = list(dict.fromkeys(text_paragraphs).keys())

    publish_datetime = datetime.fromisoformat(
        soup.find("article").find("time")["datetime"]
    )
    article_url = soup.find("link", rel=re.compile("canonical"))["href"]

    return ArticleData(
        title=title,
        author=author.strip(),
        publish_datetime=publish_datetime,
        text=text_paragraphs,
        url=article_url
    )


def fetch_article(url: str) -> ArticleData:
    """Fetch the given article's data from the TGC website."""
    res = requests.get(url, headers={"User-Agent": "Requests/2.31.0"})
    if res.status_code >= 400:
        print(res.status_code)
        print(res.text)
        raise requests.exceptions.HTTPError(response=res)
    return parse_article(res.text)


def download_recent_tgc_articles(n: int, dst: Path):
    """Scrapes and downloads up to the N most recent TGC articles in JSON format."""
    article_urls = parse_article_urls(search_tgc(max_posts=n))
    print(f"Found {len(article_urls)} articles")
    os.makedirs(dst, exist_ok=True)
    for i, url in enumerate(article_urls):
        try:
            article = fetch_article(url)
        except Exception as e:
            logging.exception(e)
            print(f"ERROR: Failed to download '{url}'")
            continue
        article_filename = article.title.lower().translate(str.maketrans("", "", string.punctuation)).replace(" ", "_")
        with open(dst / f"{article_filename}.json", "w") as file:
            json.dump(article.to_json(), file, indent=2)
        print(f"[{i+1}/{len(article_urls)}] Saved '{url}' ({len(article.text)} paragraphs)")


if __name__ == "__main__":
    download_recent_tgc_articles(n=1000, dst=Path("./_article_cache"))
