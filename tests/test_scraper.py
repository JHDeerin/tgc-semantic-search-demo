"""Tests related to searching/scraping TGC articles."""
from datetime import datetime
import json
from pathlib import Path

import pytest
import requests.exceptions

import tgc_semantic_search_demo.scraper


@pytest.fixture()
def example_tgc_search() -> dict:
    with open(Path(__file__).parent / "example_tgc_search.json") as file:
        return json.load(file)


@pytest.fixture()
def example_tgc_article() -> str:
    with open(Path(__file__).parent / "example_tgc_article.html") as file:
        return file.read()


def test_correct_article_urls_extracted_from_search(example_tgc_search):
    article_urls = tgc_semantic_search_demo.scraper.parse_article_urls(example_tgc_search["data"]["html"])

    assert set(article_urls) == set([
        "https://www.thegospelcoalition.org/article/gen-z-not-save-world/",
        "https://www.thegospelcoalition.org/article/faithful-pastors-matter-youth/",
        "https://www.thegospelcoalition.org/article/winner-2023-contest-young-adults/",
        "https://www.thegospelcoalition.org/article/gen-z-table/",
    ])


def test_searching_recent_tgc_articles():
    search_results_html = tgc_semantic_search_demo.scraper.search_tgc(max_posts=5)
    assert len(search_results_html) > 0


def test_parsing_article_content(example_tgc_article):
    article_data = tgc_semantic_search_demo.scraper.parse_article(example_tgc_article)
    expected = tgc_semantic_search_demo.scraper.ArticleData(
        title="Gen Z Will Not Save the World",
        publish_datetime=datetime.fromisoformat("2023-09-01T04:04:17+00:00"),
        author="Callum MacLeod",
        text=[],
        url="https://www.thegospelcoalition.org/article/gen-z-not-save-world/",
    )
    assert article_data.title == expected.title
    assert article_data.publish_datetime == expected.publish_datetime
    assert article_data.author == expected.author
    assert len(article_data.text) > 0
    assert article_data.url == expected.url


def test_fetching_article_content():
    article_data = tgc_semantic_search_demo.scraper.fetch_article("https://www.thegospelcoalition.org/article/gen-z-not-save-world/")
    expected = tgc_semantic_search_demo.scraper.ArticleData(
        title="Gen Z Will Not Save the World",
        publish_datetime=datetime.fromisoformat("2023-09-01T04:04:17+00:00"),
        author="Callum MacLeod",
        text=[],
        url="https://www.thegospelcoalition.org/article/gen-z-not-save-world/",
    )
    assert article_data.title == expected.title
    assert article_data.publish_datetime == expected.publish_datetime
    assert article_data.author == expected.author
    assert len(article_data.text) > 0
    assert article_data.url == expected.url


def test_httperror_raised_by_invalid_article_url():
    with pytest.raises(requests.exceptions.HTTPError):
        tgc_semantic_search_demo.scraper.fetch_article("https://www.thegospelcoalition.org/article/my-fake-article-blok03984tu3")
