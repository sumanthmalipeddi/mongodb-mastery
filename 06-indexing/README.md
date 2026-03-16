# 06 — Indexing & Performance

> **Goal:** Understand how indexes work and how to make your queries fast.

---

## Why Indexes Matter

Without an index, MongoDB performs a **collection scan** — it reads every single document to find matches. With an index, MongoDB can jump directly to the matching documents.

**Analogy:** Finding a topic in a textbook.
- Without index: Read every page until you find it (collection scan — COLLSCAN)
- With index: Look up the topic in the back-of-book index, go to that page (index scan — IXSCAN)

---

## Types of Indexes

| Type | Use Case | Example |
|------|----------|---------|
| Single Field | Query on one field | `{name: 1}` |
| Compound | Query on multiple fields | `{name: 1, age: -1}` |
| Multikey | Query array fields | Automatic for array fields |
| Text | Full-text search | `{description: "text"}` |
| Geospatial | Location queries | `{location: "2dsphere"}` |
| TTL | Auto-expire documents | `{createdAt: 1}, expireAfterSeconds: 3600` |
| Unique | Prevent duplicates | `{email: 1}, unique: True` |

---

## 📂 Files in This Section

| File | Description |
|------|-------------|
| [indexing_guide.md](indexing_guide.md) | Detailed guide to all index types |
| [performance.py](performance.py) | Benchmark: query time with vs without indexes |
| [explain_queries.py](explain_queries.py) | Using `.explain()` to analyze query plans |

---

## 📌 Key Takeaways

1. **Indexes speed up reads but slow down writes** (every insert/update must update indexes)
2. Put `$match` early in aggregation pipelines so indexes can be used
3. Use **compound indexes** for queries with multiple filter/sort fields
4. **Field order matters** in compound indexes — follow the ESR rule (Equality, Sort, Range)
5. Use `.explain()` to verify your queries use indexes (IXSCAN, not COLLSCAN)

---

**Next:** [07-python-integration/](../07-python-integration/) — Build applications with PyMongo
