# 05 — Aggregation Framework

> **Goal:** Master MongoDB's most powerful feature — the aggregation pipeline.

---

## What is Aggregation?

The aggregation framework processes documents through a **pipeline** of stages. Each stage transforms the data and passes the result to the next stage.

```
Documents → [$match] → [$group] → [$sort] → [$limit] → Results
```

Think of it like Unix pipes: `cat data | grep pattern | sort | head -10`

---

## Common Pipeline Stages

| Stage | Description | SQL Equivalent |
|-------|-------------|----------------|
| `$match` | Filter documents | `WHERE` |
| `$group` | Group and aggregate | `GROUP BY` |
| `$sort` | Sort results | `ORDER BY` |
| `$limit` | Limit results | `LIMIT` |
| `$skip` | Skip results | `OFFSET` |
| `$project` | Reshape documents (include/exclude/compute fields) | `SELECT` |
| `$count` | Count documents | `COUNT(*)` |
| `$lookup` | Join with another collection | `JOIN` |
| `$unwind` | Deconstruct an array field | — |
| `$addFields` | Add new computed fields | — |
| `$facet` | Run multiple pipelines in parallel | — |
| `$bucket` | Group into ranges | — |
| `$merge` / `$out` | Write results to a collection | `INSERT INTO ... SELECT` |

---

## 📂 Files in This Section

| File | Description |
|------|-------------|
| [pipeline_basics.py](pipeline_basics.py) | `$match`, `$group`, `$sort`, `$limit`, `$project`, `$count` |
| [pipeline_advanced.py](pipeline_advanced.py) | `$lookup`, `$unwind`, `$addFields`, `$facet`, `$bucket` |
| [real_world_queries.py](real_world_queries.py) | 10 real-world aggregation examples |
| [exercises.md](exercises.md) | 10 aggregation challenges with solutions |

---

## 📌 Key Takeaways

1. **Pipelines are ordered** — put `$match` early to filter data before expensive stages
2. **`$group` is the workhorse** — supports `$sum`, `$avg`, `$min`, `$max`, `$push`, `$first`
3. **`$lookup` is MongoDB's JOIN** — but design your schema to minimize its use
4. **`$unwind`** flattens arrays so you can group by array elements
5. **`$facet`** runs multiple aggregations in a single pass — great for dashboards

---

**Next:** [06-indexing/](../06-indexing/) — Make your queries fast
