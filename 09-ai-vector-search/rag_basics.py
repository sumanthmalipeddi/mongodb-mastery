"""
RAG Basics — Retrieval Augmented Generation with MongoDB
=========================================================
A simple RAG pipeline: embed quotes → store vectors → semantic search.

This script demonstrates the RAG pattern using MongoDB Atlas Vector Search.

Modes:
    - With OPENAI_API_KEY: Uses OpenAI embeddings (best quality)
    - Without: Uses a simple mock embedding (for learning the pipeline)

Usage:
    pip install pymongo python-dotenv openai
    python rag_basics.py

Prerequisites:
    - Run scraper.py first to populate the quotes collection
    - (Optional) Set OPENAI_API_KEY in .env for real embeddings
    - Create a vector search index in Atlas (see vector_search_setup.md)
"""

import os
import sys
import hashlib
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_NAME = "quotes_db"
COLLECTION_NAME = "quotes_vectors"
EMBEDDING_DIM = 1536  # OpenAI text-embedding-3-small dimensions


# =========================================================================
# Embedding Functions
# =========================================================================

def get_openai_embedding(text):
    """Generate embedding using OpenAI API."""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except ImportError:
        return None
    except Exception as e:
        print(f"  OpenAI error: {e}")
        return None


def get_mock_embedding(text, dim=384):
    """
    Generate a deterministic mock embedding from text.
    NOT suitable for real semantic search — only for learning the pipeline.
    Uses hashing to create a consistent vector for the same text.
    """
    # Create a deterministic hash-based vector
    embedding = []
    for i in range(dim):
        hash_input = f"{text}_{i}".encode()
        hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
        # Normalize to [-1, 1] range
        val = (hash_val % 10000) / 5000.0 - 1.0
        embedding.append(round(val, 6))
    return embedding


def get_embedding(text, use_openai=False):
    """Get embedding using the configured method."""
    if use_openai:
        embedding = get_openai_embedding(text)
        if embedding:
            return embedding
        print("  Falling back to mock embeddings")
    return get_mock_embedding(text)


# =========================================================================
# Database Setup
# =========================================================================

def connect():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Set MONGODB_URI in .env file first!")
        sys.exit(1)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


# =========================================================================
# RAG Pipeline
# =========================================================================

def main():
    print("=" * 60)
    print("RAG Pipeline — Retrieval Augmented Generation")
    print("=" * 60)

    # Check for OpenAI API key
    use_openai = bool(os.getenv("OPENAI_API_KEY"))
    if use_openai:
        print("\n✅ OpenAI API key found — using real embeddings")
        dim = EMBEDDING_DIM
    else:
        print("\n⚠️  No OPENAI_API_KEY — using mock embeddings (for learning)")
        print("   Set OPENAI_API_KEY in .env for real semantic search")
        dim = 384

    # Connect
    client = connect()
    db = client[DB_NAME]
    source_collection = db["quotes"]
    vector_collection = db[COLLECTION_NAME]

    # Check source data exists
    source_count = source_collection.count_documents({})
    if source_count == 0:
        print("\n❌ No quotes found! Run scraper.py first.")
        client.close()
        sys.exit(1)

    print(f"\n📊 Source collection: {source_count} quotes")

    # =========================================================================
    # Step 1: Generate Embeddings and Store
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Step 1: Generate Embeddings + Store in MongoDB")
    print("=" * 60)

    # Drop and recreate for clean demo
    vector_collection.drop()

    quotes = list(source_collection.find({}, {"text": 1, "author": 1, "tags": 1}))
    print(f"\n  Generating embeddings for {len(quotes)} quotes...")

    docs_to_insert = []
    for i, quote in enumerate(quotes):
        # Create embedding from the quote text
        embedding = get_embedding(quote["text"], use_openai)

        doc = {
            "text": quote["text"],
            "author": quote["author"],
            "tags": quote.get("tags", []),
            "embedding": embedding
        }
        docs_to_insert.append(doc)

        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(quotes)} quotes...")

    vector_collection.insert_many(docs_to_insert)
    print(f"  ✅ Stored {len(docs_to_insert)} documents with embeddings")
    print(f"  Each embedding has {dim} dimensions")

    # =========================================================================
    # Step 2: Semantic Search (using $vectorSearch or fallback)
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Step 2: Semantic Search")
    print("=" * 60)

    # Test queries
    test_queries = [
        "What is the meaning of life?",
        "How to be creative and imaginative",
        "Love and friendship",
        "Dealing with failure and mistakes",
    ]

    for query_text in test_queries:
        print(f"\n  🔍 Query: \"{query_text}\"")

        query_vector = get_embedding(query_text, use_openai)

        # Try Atlas Vector Search first ($vectorSearch stage)
        try:
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_vector,
                        "numCandidates": 50,
                        "limit": 3
                    }
                },
                {
                    "$project": {
                        "text": 1,
                        "author": 1,
                        "score": {"$meta": "vectorSearchScore"},
                        "_id": 0
                    }
                }
            ]
            results = list(vector_collection.aggregate(pipeline))

            if results:
                for r in results:
                    print(f"    [{r.get('score', 0):.3f}] {r['author']}: \"{r['text'][:60]}...\"")
                continue

        except OperationFailure:
            pass  # Vector search index not configured — use fallback

        # Fallback: manual cosine similarity (works without Atlas Vector Search index)
        # This is slow but demonstrates the concept
        print("    (Using manual similarity — create a vector index for production)")

        all_docs = list(vector_collection.find({}, {"text": 1, "author": 1, "embedding": 1}))

        # Compute cosine similarity manually
        def cosine_sim(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x ** 2 for x in a) ** 0.5
            norm_b = sum(x ** 2 for x in b) ** 0.5
            if norm_a == 0 or norm_b == 0:
                return 0
            return dot / (norm_a * norm_b)

        scored = []
        for doc in all_docs:
            score = cosine_sim(query_vector, doc["embedding"])
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)

        for score, doc in scored[:3]:
            print(f"    [{score:.3f}] {doc['author']}: \"{doc['text'][:60]}...\"")

    # =========================================================================
    # Step 3: RAG — Combine Search with Generation
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Step 3: RAG — Retrieval Augmented Generation")
    print("=" * 60)

    print("""
  In a full RAG pipeline, you would:

  1. RETRIEVE: Search for relevant quotes using vector search (Step 2)
  2. AUGMENT: Build a prompt with the retrieved quotes as context
  3. GENERATE: Send to an LLM (GPT-4, Claude, etc.) for a grounded answer

  Example prompt:
  ┌─────────────────────────────────────────────────┐
  │ Based on these quotes:                          │
  │ 1. "The world as we have..." — Einstein         │
  │ 2. "Life is what happens..." — Lennon           │
  │ 3. "In three words..." — Einstein               │
  │                                                 │
  │ Question: What do famous people say about life? │
  │                                                 │
  │ Please answer based only on the quotes above.   │
  └─────────────────────────────────────────────────┘

  This grounds the LLM's response in your actual data,
  reducing hallucination and keeping answers relevant.
    """)

    if use_openai:
        print("  💡 You have an OpenAI key — try extending this script to call GPT!")

    # =========================================================================
    # Cleanup
    # =========================================================================
    print("=" * 60)
    print("Done!")
    print(f"  Vectors stored in: {DB_NAME}.{COLLECTION_NAME}")
    print(f"  Documents: {vector_collection.count_documents({})}")
    print(f"  To enable real vector search, create an Atlas Vector Search index")
    print(f"  (see vector_search_setup.md)")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
