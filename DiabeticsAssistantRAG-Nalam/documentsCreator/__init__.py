"""
Isolated module for building standardized JSON documents from raw data.

This package is intentionally decoupled from the main RAG pipeline:
- no embeddings
- no vector databases
- no LangChain pipelines
- no coupling to existing `src/` loaders or ingestion code

All input is read from this package's own `data/raw/` directory,
and all outputs are written under `data/processed/json_documents/`.
"""

