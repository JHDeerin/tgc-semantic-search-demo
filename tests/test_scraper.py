"""Tests related to searching/scraping TGC articles."""
import json
from pathlib import Path

import pytest

import tgc_semantic_search_demo.scraper


@pytest.fixture()
def example_tgc_search() -> dict:
    with open(Path(__file__).parent / "example_tgc_search.json") as file:
        return json.load(file)


def test_correct_article_urls_extracted_from_search(example_tgc_search):
    article_urls = tgc_semantic_search_demo.scraper.get_article_urls(example_tgc_search["data"]["html"])

    assert set(article_urls) == set([
        "https://www.thegospelcoalition.org/article/gen-z-not-save-world/",
        "https://www.thegospelcoalition.org/article/faithful-pastors-matter-youth/",
        "https://www.thegospelcoalition.org/article/winner-2023-contest-young-adults/",
        "https://www.thegospelcoalition.org/article/gen-z-table/",
    ])
