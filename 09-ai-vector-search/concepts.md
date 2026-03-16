# AI & Vector Search Concepts

---

## What Are Embeddings?

An **embedding** is a list of numbers (a vector) that represents the meaning of text, images, or other data.

**Analogy:** Think of GPS coordinates. "Portland, Oregon" and "Seattle, Washington" are different words, but their GPS coordinates are close together because they're geographically similar. Embeddings do the same for meaning — similar concepts get similar vectors.

```
"MongoDB is a document database"  → [0.12, -0.34, 0.56, 0.78, ...]  (1536 numbers)
"NoSQL databases store documents" → [0.11, -0.32, 0.58, 0.75, ...]  (similar vector!)
"I like pizza"                    → [0.89, 0.45, -0.12, 0.33, ...]  (very different vector)
```

Embeddings are created by AI models (OpenAI, Sentence Transformers, Cohere, etc.) and typically have 256–3072 dimensions.

---

## How Vector Databases Work

A vector database stores embeddings and efficiently finds the most similar ones using **approximate nearest neighbor (ANN)** search.

```
Query: "How do I connect to a database?"
  ↓ (embed the query)
Query vector: [0.15, -0.28, 0.61, ...]
  ↓ (search for similar vectors)
Results:
  1. "MongoDB connection string setup"     (similarity: 0.92)
  2. "Connecting to PostgreSQL"            (similarity: 0.88)
  3. "Database driver configuration"       (similarity: 0.85)
```

Unlike keyword search (`$text`), vector search understands that "connect to a database" is related to "database driver configuration" even though they share few words.

---

## Semantic Search vs Keyword Search

| Feature | Keyword Search (`$text`) | Vector Search |
|---------|-------------------------|---------------|
| Matches | Exact words and stems | Meaning and concepts |
| "car" finds "automobile" | ❌ No | ✅ Yes |
| Handles typos | ❌ No | ✅ Partially |
| Requires training | ❌ No | ✅ Needs embedding model |
| Speed | Very fast | Fast (with ANN index) |
| Setup complexity | Low | Medium |

**Best practice:** Combine both. Use keyword search for exact matches, vector search for semantic understanding.

---

## Distance Metrics

How "similarity" between vectors is measured:

| Metric | Description | Range | Best For |
|--------|-------------|-------|----------|
| **Cosine** | Angle between vectors | -1 to 1 (1 = identical) | Text embeddings (most common) |
| **Euclidean** | Straight-line distance | 0 to ∞ (0 = identical) | When magnitude matters |
| **Dot Product** | Product of magnitudes | -∞ to ∞ (higher = more similar) | Normalized vectors |

📌 **Use cosine similarity** for text search — it's the default and works best with most embedding models.

---

## What is RAG?

**RAG (Retrieval Augmented Generation)** is a pattern that combines search with AI text generation:

```
User question: "What are the best schema design patterns?"
  ↓
Step 1: RETRIEVE — Search your database for relevant documents
  → Found: patterns.md, anti-patterns.md, blog_schema.py
  ↓
Step 2: AUGMENT — Add retrieved content to the LLM prompt
  → "Based on these documents: [content]. Answer the question: ..."
  ↓
Step 3: GENERATE — LLM creates an answer grounded in your data
  → "The key schema design patterns are: embedding for 1:few..."
```

**Why RAG matters:**
- LLMs have a knowledge cutoff — RAG gives them access to your current data
- Reduces hallucination — answers are grounded in real documents
- Works with private data — your company docs, product data, etc.

---

## MongoDB Atlas Vector Search

Atlas Vector Search brings vector capabilities to MongoDB:

- **No separate database** — vectors live alongside your regular data
- **Combined queries** — filter by regular fields AND search by vectors
- **Pre-filtering** — narrow by metadata before running the expensive vector search

```python
# Example: Find quotes similar to "life is beautiful" that are tagged "love"
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": 5,
            "filter": {"tags": "love"}  # Pre-filter!
        }
    }
]
```

---

## MongoDB Atlas vs Dedicated Vector Databases

| Feature | MongoDB Atlas | Pinecone / Weaviate / Qdrant |
|---------|--------------|------------------------------|
| Vector search | ✅ | ✅ |
| Traditional queries | ✅ Full MongoDB | ❌ Limited filtering |
| ACID transactions | ✅ | ❌ |
| Aggregation | ✅ Full pipeline | ❌ |
| One database to manage | ✅ | ❌ Need two systems |
| Cost | Included in Atlas | Separate billing |
| Specialized features | Good | Excellent (purpose-built) |

**Choose MongoDB Atlas** when you already use MongoDB and want to add vector search without architectural complexity.

**Choose a dedicated vector DB** when vector search is your primary use case and you need bleeding-edge features.

---

## 📌 Key Takeaways

1. **Embeddings** convert text into numbers that represent meaning
2. **Vector search** finds semantically similar content, unlike keyword search
3. **RAG** combines search with LLMs to generate grounded answers
4. **Atlas Vector Search** lets you keep vectors in the same database as your app data
5. **Cosine similarity** is the go-to distance metric for text
6. Combine vector search with traditional MongoDB filters for powerful queries
