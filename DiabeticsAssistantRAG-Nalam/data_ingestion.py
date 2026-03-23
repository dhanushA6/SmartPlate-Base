import json
import chromadb
from chromadb.utils import embedding_functions
import os

# 1. Configuration
DATA_FILE = "nalam_data.json"
CHROMA_PATH = "./nalam_chroma_db"
COLLECTION_NAME = "nalam_knowledge"

# Initialize ChromaDB (Persistent)
client = chromadb.PersistentClient(path=CHROMA_PATH)

# A high-quality, free local embedding model
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create or get the collection
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=sentence_transformer_ef
)

def chunk_text(text, chunk_size=1000, overlap=200):
    """Splits long text into smaller overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Move forward by chunk_size - overlap
        start += (chunk_size - overlap)
    return chunks

def process_and_ingest():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    documents = []
    metadatas = []
    ids = []

    print(f"🔄 Processing {len(raw_data)} records...")

    for item in raw_data:
        source_type = item.get("source_type", "unknown")
        base_id = item.get("doc_id")
        title = item.get("title", "No Title")
        content = item.get("content", "")
        
        # Metadata extraction (Keep it simple for now)
        meta = {
            "source": source_type,
            "title": title,
            "url": item.get("metadata", {}).get("url", "N/A")
        }

        # STRATEGY: Differentiate processing based on source
        if source_type == "web":
            # Chunk long articles
            text_chunks = chunk_text(content)
            for i, chunk in enumerate(text_chunks):
                documents.append(chunk)
                metadatas.append(meta)
                ids.append(f"{base_id}_chunk_{i}")
                
        elif source_type == "csv":
            # Keep nutrition rows intact (Atomic)
            documents.append(content)
            metadatas.append(meta)
            ids.append(base_id)

    # Batch insertion (Chroma handles batches well, but safe to do 5000 at a time if huge)
    print(f"🚀 Inserting {len(documents)} vectors into ChromaDB...")
    
    # Simple batching to avoid hitting memory limits on large datasets
    batch_size = 5000
    for i in range(0, len(documents), batch_size):
        batch_end = i + batch_size
        print("Upserting")
        collection.upsert(
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end],
            ids=ids[i:batch_end]
        )
        print(f"   Inserted batch {i} to {batch_end}")

    print(f"✅ Success! Knowledge Base built at '{CHROMA_PATH}'")
    print(f"Total chunks stored: {collection.count()}")

if __name__ == "__main__":
    process_and_ingest()