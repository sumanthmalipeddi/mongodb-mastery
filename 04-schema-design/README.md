# 04 — Schema Design

> **Goal:** Learn how to model data in MongoDB — the most important skill for building performant applications.

---

## The Golden Rule

> **Design your schema based on how your application queries data, not how the data relates.**

In SQL, you normalize first and worry about queries later. In MongoDB, you start with your queries and design the schema to serve them efficiently.

---

## Embedding vs Referencing

| Strategy | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **Embed** | Data is read together, 1:1 or 1:few | Single read, no joins, atomic updates | Document can grow large, data duplication |
| **Reference** | Data is read independently, 1:many or many:many | Smaller documents, no duplication | Requires `$lookup` (join), multiple reads |

### Decision Flowchart

```
Do you always read this data together?
  ├── YES → Is the nested data bounded (won't grow forever)?
  │           ├── YES → EMBED ✅
  │           └── NO  → REFERENCE (or hybrid)
  └── NO  → REFERENCE ✅
```

---

## 📂 Files in This Section

| File | Description |
|------|-------------|
| [patterns.md](patterns.md) | Common patterns: one-to-many, polymorphic, bucket, etc. |
| [anti-patterns.md](anti-patterns.md) | What NOT to do and how to fix it |
| [examples/blog_schema.py](examples/blog_schema.py) | Blog with embedded comments |
| [examples/ecommerce_schema.py](examples/ecommerce_schema.py) | E-commerce with references |
| [examples/social_media_schema.py](examples/social_media_schema.py) | Social media hybrid approach |

---

## 📌 Key Takeaways

1. **No one-size-fits-all** — schema design depends on your access patterns
2. **Embed** when data is read together and bounded in size
3. **Reference** when data is read independently or grows unboundedly
4. **16 MB document limit** — plan for growth
5. **Denormalization is OK** — MongoDB trades storage for read performance
6. The best schema is the one that makes your most common queries fastest

---

**Next:** [05-aggregation/](../05-aggregation/) — Analyze your data with pipelines
