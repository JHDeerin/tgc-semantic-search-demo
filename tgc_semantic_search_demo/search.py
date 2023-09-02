"""Utilities for searching through TGC articles using AI semantic search methods."""
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
import chromadb.utils.embedding_functions


def initialize_database(src: Path, refresh: bool=False) -> chromadb.Collection:
    client = chromadb.PersistentClient("./_chromadb_cache")
    collection = client.get_or_create_collection(
        "tgc-articles",
        embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2", device="cuda")
    )
    if not refresh:
        return collection

    # Load each saved TGC article into memory and add it to the DB
    filepaths = [src / path for path in os.listdir(src) if (src / path).is_file()]
    for i, path in enumerate(filepaths):
        with open(path) as file:
            article_json = json.load(file)
        collection.add(
            documents=article_json["text"],
            metadatas=[
                {
                    "article": article_json["title"],
                    "author": article_json["author"],
                    "date": article_json["publish_datetime"],
                    "url": article_json["url"],
                    "paragraph": i
                }
                for i in range(len(article_json["text"]))
            ],
            ids=[
                f"{article_json['url']}_{i}" for i in range(len(article_json["text"]))
            ]
        )
        print(f"[{i+1}/{len(filepaths)}] Added '{path}'")
    return collection


def print_search_results(results: chromadb.QueryResult):
    for i in range(len(results["ids"][0])):
        print("-" * 40)
        data = results['metadatas'][0][i]
        print(f"{i+1}. {data['article']} ({datetime.fromisoformat(data['date']).date().isoformat()}) ({results['distances'][0][i]:.2f})")
        print(results['documents'][0][i])
        print()


if __name__ == "__main__":
    print("Parsing args")
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("-r", "--refresh", action="store_true")
    parser.add_argument("-n", "--num-results", type=int, required=False, default=5)
    args = parser.parse_args()

    print("Loading DB")
    db = initialize_database(src=Path("./_article_cache"), refresh=args.refresh)
    print("Running search")
    start_time = time.time()
    results = db.query(query_texts=[args.query], n_results=args.num_results)
    print_search_results(results)
    print(f"({time.time() - start_time:.3f} seconds)")
