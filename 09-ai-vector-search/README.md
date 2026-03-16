# 09 — AI & Vector Search

> **Goal:** Understand how MongoDB fits into AI applications — vector search, embeddings, and RAG pipelines.

---

## Why MongoDB for AI?

MongoDB Atlas Vector Search lets you store your application data AND vector embeddings in the same database — no need for a separate vector database. This simplifies architecture and enables combining traditional filters with semantic search.

---

## What's in This Section

| File | Description |
|------|-------------|
| [concepts.md](concepts.md) | Embeddings, vector databases, semantic search, RAG explained |
| [vector_search_setup.md](vector_search_setup.md) | How to set up Atlas Vector Search |
| [rag_basics.py](rag_basics.py) | Simple RAG pipeline with MongoDB |
| [langchain_example.py](langchain_example.py) | LangChain + MongoDB integration |

---

## 📌 Key Takeaways

1. **Vector search** finds semantically similar content, not just keyword matches
2. **MongoDB Atlas Vector Search** combines vector search with traditional database features
3. **RAG** (Retrieval Augmented Generation) grounds LLM responses in your data
4. You don't need a separate vector database — MongoDB handles both structured data and vectors

---

**Next:** [10-production/](../10-production/) — Deploy and operate MongoDB
