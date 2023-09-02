"""Utilities for searching through TGC articles using AI semantic search methods."""
import argparse
import json
import os
from pathlib import Path

# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
import chromadb.utils.embedding_functions


def initialize_database(src: Path) -> chromadb.Collection:
    # TODO: Implement this!
    client = chromadb.PersistentClient("./_chromadb_cache")

    collection = client.create_collection(
        "tgc-articles",
        embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2", device="cuda")
    )
    # Load each saved TGC article into memory and add it to the DB
    for i, path in enumerate(os.listdir(src)):
        if not (src / path).is_file():
            continue
        with open(src / path) as file:
            article_json = json.load(file)
        collection.add(
            documents=article_json["text"],
            metadatas=[{"article": article_json["url"], "paragraph": i} for i in range(len(article_json["text"]))],
            ids=[f"{article_json['url']}_{i}" for i in range(len(article_json["text"]))]
        )
        print(f"[{i+1}/{len(os.listdir(src))}]Added '{path}'")
    return collection


def print_search_results(results: chromadb.QueryResult):
    for i in range(len(results["ids"][0])):
        print("-" * 40)
        print(f"{i+1}. {results['metadatas'][0][i]}")
        print(f"\tDistance: {results['distances'][0][i]}")
        print(f"\tText: '{results['documents'][0][i]}'")
        print()


if __name__ == "__main__":
    # db = initialize_database(src=Path("./_article_cache"))
    db = chromadb.PersistentClient("./_chromadb_cache").get_collection(
        "tgc-articles",
        embedding_function=chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2", device="cuda")
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("-n", "--num-results", type=int, required=False, default=5)
    args = parser.parse_args()
    results = db.query(query_texts=[args.query], n_results=5)
    print_search_results(results)
