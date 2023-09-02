"""Utilities for searching through TGC articles using AI semantic search methods."""
import json
import os
from pathlib import Path

# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb


def initialize_database(src: Path):
    # TODO: Implement this!
    client = chromadb.Client()

    collection = client.create_collection("tgc-articles")
    # Load each saved TGC article into memory and add it to the DB
    for i, path in enumerate(os.listdir(src)[:5]):
        if not (src / path).is_file():
            continue
        with open(src / path) as file:
            article_json = json.load(file)
        collection.add(
            documents=article_json["text"],
            metadatas=[{"article": article_json["url"], "paragraph": i} for i in range(len(article_json["text"]))],
            ids=[f"{article_json['url']}_{i}" for i in range(len(article_json["text"]))]
        )
        print(f"[{i+1}]Added '{path}'")
    return collection


if __name__ == "__main__":
    db = initialize_database(src=Path("./_article_cache"))
    results = db.query(query_texts=["is it okay for christians to work as spies"], n_results=5)
    print(results)
