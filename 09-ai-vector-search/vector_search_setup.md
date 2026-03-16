# Setting Up Atlas Vector Search

Step-by-step guide to enabling vector search on your MongoDB Atlas cluster.

---

## Prerequisites

- MongoDB Atlas M0 (free tier) or higher
- A collection with vector embeddings stored as arrays of numbers

---

## Step 1: Create a Vector Search Index

1. Go to your Atlas cluster → **Atlas Search** tab
2. Click **"Create Search Index"**
3. Select **"JSON Editor"** (for vector search)
4. Select your database and collection
5. Use the following index definition:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "author"
    },
    {
      "type": "filter",
      "path": "tags"
    }
  ]
}
```

6. Name the index `vector_index`
7. Click **"Create Search Index"**

---

## Index Configuration Options

### numDimensions
Must match your embedding model's output:

| Model | Dimensions |
|-------|-----------|
| OpenAI text-embedding-3-small | 1536 |
| OpenAI text-embedding-3-large | 3072 |
| Sentence Transformers (all-MiniLM-L6-v2) | 384 |
| Cohere embed-english-v3.0 | 1024 |

### similarity
| Metric | When to Use |
|--------|-------------|
| `cosine` | Text embeddings (most common) |
| `euclidean` | When vector magnitude matters |
| `dotProduct` | Normalized vectors only |

### Filter Fields
Add `filter` type fields for any field you want to pre-filter on. Pre-filtering narrows candidates before the vector search runs, improving speed and relevance.

---

## Step 2: Query with $vectorSearch

```python
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",      # Index name
            "path": "embedding",           # Field containing vectors
            "queryVector": [0.1, 0.2, ...],  # Your query vector
            "numCandidates": 100,          # How many candidates to consider
            "limit": 5,                    # How many results to return
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

results = collection.aggregate(pipeline)
```

### With Pre-Filtering

```python
{
    "$vectorSearch": {
        "index": "vector_index",
        "path": "embedding",
        "queryVector": query_vector,
        "numCandidates": 100,
        "limit": 5,
        "filter": {
            "author": {"$eq": "Albert Einstein"}
        }
    }
}
```

---

## Step 3: Tune numCandidates

`numCandidates` controls the accuracy-speed tradeoff:

- **Higher** (200+): More accurate, slower
- **Lower** (50): Faster, may miss good matches
- **Rule of thumb**: Set to 10–20x your `limit`

---

## Limitations

- Free tier (M0) supports vector search with some restrictions on index count
- Maximum vector dimensions: 4096
- Each vector search index can have one vector field
- Pre-filter fields must be declared in the index definition

---

## 📌 Key Takeaways

1. Create vector search indexes through the Atlas UI or API (not `createIndex`)
2. `numDimensions` must match your embedding model exactly
3. Use `cosine` similarity for text embeddings
4. Add `filter` fields to the index for pre-filtering capabilities
5. Set `numCandidates` to 10-20x your `limit` for good accuracy
