#!/usr/bin/env python3
"""
Nokia Documentation Ingestion Pipeline

Fetches Nokia SR Linux and SR OS documentation (HTML pages and PDFs),
chunks them, and stores embeddings in ChromaDB.

Usage:
    python3 ingest/ingest.py --output-dir ./data/chromadb
    python3 ingest/ingest.py --sources ingest/sources.yaml --output-dir ./data/chromadb
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

import chromadb
import html2text
import requests
import yaml
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Optional PDF support
try:
    from pypdf import PdfReader
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


def load_sources(sources_file: str) -> dict:
    with open(sources_file) as f:
        return yaml.safe_load(f)


def fetch_html(url: str) -> str:
    """Fetch an HTML page and convert to plain text."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove nav, header, footer elements
    for tag in soup.find_all(["nav", "header", "footer", "script", "style"]):
        tag.decompose()

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0
    return converter.handle(str(soup))


def fetch_pdf(url_or_path: str) -> str:
    """Read a PDF from URL or local path and extract text."""
    if not HAS_PDF:
        print(f"  SKIP (pypdf not installed): {url_or_path}")
        return ""

    if url_or_path.startswith("http"):
        resp = requests.get(url_or_path, timeout=60)
        resp.raise_for_status()
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name
        reader = PdfReader(tmp_path)
        os.unlink(tmp_path)
    else:
        reader = PdfReader(url_or_path)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        text += "\n\n"
    return text


def chunk_text(text: str, source: str, metadata: dict) -> list[dict]:
    """Split text into chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_text(text)
    results = []
    for i, chunk in enumerate(chunks):
        doc_id = hashlib.md5(f"{source}:{i}".encode()).hexdigest()
        results.append({
            "id": doc_id,
            "text": chunk,
            "metadata": {
                **metadata,
                "source": source,
                "chunk_index": i,
            },
        })
    return results


def ingest(sources_file: str, output_dir: str):
    """Main ingestion pipeline."""
    sources = load_sources(sources_file)
    all_chunks = []

    for entry in sources.get("sources", []):
        url = entry["url"]
        doc_type = entry.get("type", "html")
        platform = entry.get("platform", "unknown")
        category = entry.get("category", "general")

        print(f"Fetching [{platform}/{category}] {url}")

        try:
            if doc_type == "pdf":
                text = fetch_pdf(url)
            else:
                text = fetch_html(url)

            if not text.strip():
                print(f"  WARN: empty content from {url}")
                continue

            metadata = {
                "platform": platform,
                "category": category,
                "doc_type": doc_type,
            }
            chunks = chunk_text(text, url, metadata)
            all_chunks.extend(chunks)
            print(f"  -> {len(chunks)} chunks")

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    if not all_chunks:
        print("No chunks to ingest. Check your sources.")
        sys.exit(1)

    # Store in ChromaDB
    print(f"\nStoring {len(all_chunks)} chunks in ChromaDB at {output_dir}")
    client = chromadb.PersistentClient(path=output_dir)
    collection = client.get_or_create_collection(
        name="nokia_docs",
        metadata={"description": "Nokia SR Linux and SR OS documentation"},
    )

    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
        )
        print(f"  Upserted batch {i // batch_size + 1}/{(len(all_chunks) + batch_size - 1) // batch_size}")

    print(f"\nDone. Collection '{collection.name}' has {collection.count()} documents.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Nokia docs into ChromaDB")
    parser.add_argument("--sources", default="ingest/sources.yaml", help="Sources YAML file")
    parser.add_argument("--output-dir", default="./data/chromadb", help="ChromaDB storage path")
    args = parser.parse_args()
    ingest(args.sources, args.output_dir)
