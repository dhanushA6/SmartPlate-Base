"""
Isolated JSON document builder (Deep Crawl Enabled)

Reads from:

    data/raw/web/urls.txt
    data/raw/pdf/*.pdf
    data/raw/csv/*.csv
    data/raw/text/*.txt
    data/raw/json/*.json

Writes to:

    data/processed/json_documents/<output_filename>.json

Keeps a registry:

    data/processed/processed_sources.json
"""

import argparse
import csv
import json
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from loaders.web_loader import crawl_website
from loaders.txt_loader import load_txt
from loaders.pdf_loader import load_pdf
from loaders.csv_loader import load_csv_rows
from loaders.json_loader import load_json_sections


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

MODULE_DIR = Path(__file__).resolve().parent

RAW_DIR = MODULE_DIR / "data" / "raw"
WEB_URLS_FILE = RAW_DIR / "web" / "urls.txt"
PDF_DIR = RAW_DIR / "pdf"
CSV_DIR = RAW_DIR / "csv"
TXT_DIR = RAW_DIR / "text"
JSON_DIR = RAW_DIR / "json"

PROCESSED_DIR = MODULE_DIR / "data" / "processed"
JSON_OUTPUT_DIR = PROCESSED_DIR / "json_documents"
REGISTRY_FILE = PROCESSED_DIR / "processed_sources.json"

JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def now_iso_utc() -> str:
    return datetime.utcnow().isoformat() + "Z"


def generate_doc_id() -> str:
    return str(uuid.uuid4())


def load_existing_documents(path: Path) -> List[Dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_json(path: Path, data: Any) -> None:
    temp_path = path.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    temp_path.replace(path)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def load_registry() -> Set[str]:
    if not REGISTRY_FILE.exists():
        return set()

    with REGISTRY_FILE.open("r", encoding="utf-8") as f:
        return set(json.load(f))


def save_registry(registry: Set[str]) -> None:
    atomic_write_json(REGISTRY_FILE, sorted(list(registry)))


# ---------------------------------------------------------------------------
# WEB (Deep Crawl)
# ---------------------------------------------------------------------------

def process_web_urls(registry: Set[str]) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    if not WEB_URLS_FILE.exists():
        print("[web] urls.txt not found, skipping.")
        return docs

    with WEB_URLS_FILE.open("r", encoding="utf-8") as f:
        urls = set()

        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # sanitize JSON-style formatting
            line = line.strip('"').strip("'").rstrip(",")

            if not line.startswith(("http://", "https://")):
                print(f"[INVALID URL FORMAT] {line}")
                continue

            urls.add(line)

    for base_url in urls:

        if base_url in registry:
            print(f"[SKIP DOMAIN] {base_url}")
            continue

        print(f"[DEEP CRAWL START] {base_url}")

        try:
            pages = crawl_website(
                start_url=base_url,
                max_pages=120,
                max_depth=2,
                delay=0.8
            )
        except Exception as e:
            print(f"[CRAWL FAILED] {base_url} -> {e}")
            continue

        for page in pages:
            doc = {
                "doc_id": generate_doc_id(),
                "source_type": "web",
                "title": clean_text(page["title"]),
                "content": clean_text(page["content"])
            }

            docs.append(doc)

        registry.add(base_url)

    return docs


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def process_pdfs(registry: Set[str]) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    if not PDF_DIR.exists():
        return docs

    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        source_id = str(pdf_path)

        if source_id in registry:
            print(f"[SKIP pdf] {pdf_path.name}")
            continue

        try:
            pdf_doc = load_pdf(pdf_path)
        except Exception as exc:
            print(f"[pdf] Failed {pdf_path}: {exc}", file=sys.stderr)
            continue

        content = clean_text(pdf_doc["content"])
        if not content:
            continue

        docs.append({
            "doc_id": generate_doc_id(),
            "source_type": "pdf",
            "title": clean_text(pdf_doc["title"]),
            "content": content
        })

        registry.add(source_id)

    return docs


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def process_csvs(registry: Set[str]) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    if not CSV_DIR.exists():
        return docs

    for csv_path in sorted(CSV_DIR.glob("*.csv")):
        source_id = str(csv_path)

        if source_id in registry:
            print(f"[SKIP csv] {csv_path.name}")
            continue

        try:
            rows = load_csv_rows(csv_path)

        except Exception as exc:
            print(f"[csv] Failed {csv_path}: {exc}", file=sys.stderr)
            continue

        for idx, row in enumerate(rows, start=1):
            content = " ; ".join(f"{k}: {v}" for k, v in row.items())
            content = clean_text(content)

            if not content:
                continue

            title = row.get("title") or f"{csv_path.stem} [row {idx}]"

            docs.append({
                "doc_id": generate_doc_id(),
                "source_type": "csv",
                "title": clean_text(title),
                "content": content
            })

        registry.add(source_id)

    return docs


# ---------------------------------------------------------------------------
# TXT
# ---------------------------------------------------------------------------

def process_txts(registry: Set[str]) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    if not TXT_DIR.exists():
        return docs

    for txt_path in sorted(TXT_DIR.glob("*.txt")):
        source_id = str(txt_path)

        if source_id in registry:
            print(f"[SKIP txt] {txt_path.name}")
            continue

        try:
            txt_doc = load_txt(txt_path)
        except Exception as exc:
            print(f"[txt] Failed {txt_path}: {exc}", file=sys.stderr)
            continue

        content = clean_text(txt_doc["content"])
        if not content:
            continue

        docs.append({
            "doc_id": generate_doc_id(),
            "source_type": "txt",
            "title": clean_text(txt_doc["title"]),
            "content": content
        })

        registry.add(source_id)

    return docs


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------


def process_jsons(registry: Set[str]) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    if not JSON_DIR.exists():
        return docs

    for json_path in sorted(JSON_DIR.glob("*.json")):
        source_id = str(json_path)

        if source_id in registry:
            print(f"[SKIP json] {json_path.name}")
            continue

        try:
            sections = load_json_sections(json_path)
        except Exception as exc:
            print(f"[json] Failed {json_path}: {exc}", file=sys.stderr)
            continue

        for section in sections:
            content = clean_text(section.get("content", ""))
            if not content:
                continue

            title = clean_text(section.get("title") or json_path.stem)

            docs.append({
                "doc_id": generate_doc_id(),
                "source_type": "json",
                "title": title,
                "content": content,
            })

        registry.add(source_id)

    return docs


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_documents(output_filename: str) -> Path:
    output_path = JSON_OUTPUT_DIR / output_filename

    registry = load_registry()
    existing_docs = load_existing_documents(output_path)

    web_docs = process_web_urls(registry)
    pdf_docs = process_pdfs(registry)
    csv_docs = process_csvs(registry)
    txt_docs = process_txts(registry)
    json_docs = process_jsons(registry)

    new_docs = web_docs + pdf_docs + csv_docs + txt_docs + json_docs

    if not new_docs:
        print("No new documents generated.")
        return output_path

    all_docs = existing_docs + new_docs

    atomic_write_json(output_path, all_docs)
    save_registry(registry)

    print(f"Existing documents: {len(existing_docs)}")
    print(f"New documents added: {len(new_docs)}")
    print(f"Total documents: {len(all_docs)}")

    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build standardized JSON documents (Deep Crawl Enabled)."
    )
    parser.add_argument(
        "--output-filename",
        "-o",
        default="standard_documents.json",
        help="Output filename inside data/processed/json_documents/",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    build_documents(args.output_filename)


if __name__ == "__main__":
    main()
