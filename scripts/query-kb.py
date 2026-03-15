#!/usr/bin/env python3
"""
Query the Nokia documentation ChromaDB knowledge base.

Usage:
    python3 scripts/query-kb.py --query "BGP configuration SR Linux"
    python3 scripts/query-kb.py --query "cards MDA SROS" --n-results 10
    python3 scripts/query-kb.py --query "containerlab topology" --platform containerlab
"""

import argparse
import json
import sys

import chromadb


def query_kb(db_path: str, collection_name: str, query: str, n_results: int, platform: str = None):
    client = chromadb.PersistentClient(path=db_path)

    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        print(f"ERROR: Collection '{collection_name}' not found. Run ingest first.")
        sys.exit(1)

    where_filter = None
    if platform:
        where_filter = {"platform": platform}

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "id": results["ids"][0][i],
            "distance": results["distances"][0][i],
            "platform": results["metadatas"][0][i].get("platform", ""),
            "category": results["metadatas"][0][i].get("category", ""),
            "source": results["metadatas"][0][i].get("source", ""),
            "text": results["documents"][0][i],
        })

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Nokia docs knowledge base")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--db-path", default="./data/chromadb", help="ChromaDB path")
    parser.add_argument("--collection", default="nokia_docs", help="Collection name")
    parser.add_argument("--n-results", type=int, default=5, help="Number of results")
    parser.add_argument("--platform", choices=["srlinux", "sros", "containerlab"], help="Filter by platform")
    args = parser.parse_args()
    query_kb(args.db_path, args.collection, args.query, args.n_results, args.platform)
