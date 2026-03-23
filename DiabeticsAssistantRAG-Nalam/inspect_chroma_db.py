import os
import json
import numpy as np
from datetime import datetime
import chromadb


# ============================================================
# 🔧 CONFIGURATION (EDIT ONLY THIS)
# ============================================================
CHROMA_DB_PATH = "./nalam_chroma_db"   # <-- Put your path here
OUTPUT_JSON = "chromadb_inspection.json"
BATCH_SIZE = 1000
# ============================================================


def compute_embedding_stats(all_embeddings):
    """
    Compute statistics for embeddings safely.
    """
    if all_embeddings is None or len(all_embeddings) == 0:
        return {
            "embedding_dimension": None,
            "num_embeddings": 0,
            "norm_mean": None,
            "norm_min": None,
            "norm_max": None,
        }

    embeddings = np.array(all_embeddings)
    norms = np.linalg.norm(embeddings, axis=1)

    return {
        "embedding_dimension": int(embeddings.shape[1]),
        "num_embeddings": int(embeddings.shape[0]),
        "norm_mean": float(np.mean(norms)),
        "norm_min": float(np.min(norms)),
        "norm_max": float(np.max(norms)),
    }


def inspect_collection(client, collection_name):
    print("\n" + "=" * 70)
    print(f"Inspecting Collection: {collection_name}")
    print("=" * 70)

    collection = client.get_collection(collection_name)
    total_docs = collection.count()

    print(f"Total Documents: {total_docs}")

    all_embeddings = []
    metadata_keys = set()
    sample_documents = []

    total_characters = 0
    chunk_lengths = []

    # Batch fetching (safe for large collections)
    for offset in range(0, total_docs, BATCH_SIZE):
        results = collection.get(
            include=["embeddings", "metadatas", "documents"],
            limit=BATCH_SIZE,
            offset=offset
        )

        embeddings = results.get("embeddings", [])
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        # Safe embedding check
        if embeddings is not None and len(embeddings) > 0:
            all_embeddings.extend(list(embeddings))

        # Metadata analysis
        for meta in metadatas:
            if meta is not None:
                metadata_keys.update(meta.keys())

        # Document statistics
        for doc in documents:
            if doc is not None:
                length = len(doc)
                total_characters += length
                chunk_lengths.append(length)

        # Collect up to 3 sample documents
        if len(sample_documents) < 3:
            needed = 3 - len(sample_documents)
            sample_documents.extend(documents[:needed])

    # Embedding statistics
    embedding_stats = compute_embedding_stats(all_embeddings)

    # Chunk statistics
    if len(chunk_lengths) > 0:
        chunk_stats = {
            "avg_chunk_length": float(np.mean(chunk_lengths)),
            "min_chunk_length": int(np.min(chunk_lengths)),
            "max_chunk_length": int(np.max(chunk_lengths)),
            "total_characters": int(total_characters),
        }
    else:
        chunk_stats = {
            "avg_chunk_length": None,
            "min_chunk_length": None,
            "max_chunk_length": None,
            "total_characters": 0,
        }

    # Print to terminal
    print("\nEmbedding Statistics:")
    for k, v in embedding_stats.items():
        print(f"  {k}: {v}")

    print("\nChunk Statistics:")
    for k, v in chunk_stats.items():
        print(f"  {k}: {v}")

    print("\nMetadata Keys:")
    print(list(metadata_keys))

    print("\nSample Documents (first 300 chars):")
    for i, doc in enumerate(sample_documents):
        print(f"\n--- Sample {i+1} ---")
        if doc:
            print(doc[:300])
        else:
            print("Empty document")

    return {
        "collection_name": collection_name,
        "total_documents": total_docs,
        "embedding_stats": embedding_stats,
        "chunk_stats": chunk_stats,
        "metadata_keys": list(metadata_keys),
        "sample_documents": sample_documents,
    }


def main():
    if not os.path.exists(CHROMA_DB_PATH):
        print("ERROR: Path does not exist.")
        return

    print("Connecting to ChromaDB...")
    print(f"Database Path: {CHROMA_DB_PATH}")

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    collections = client.list_collections()
    print(f"\nTotal Collections Found: {len(collections)}")

    full_stats = {
        "inspection_time": datetime.now().isoformat(),
        "database_path": CHROMA_DB_PATH,
        "num_collections": len(collections),
        "collections": []
    }

    for col in collections:
        stats = inspect_collection(client, col.name)
        full_stats["collections"].append(stats)

    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(full_stats, f, indent=4)

    print("\n" + "=" * 70)
    print("Inspection Complete")
    print(f"Results saved to: {OUTPUT_JSON}")
    print("=" * 70)


if __name__ == "__main__":
    main()