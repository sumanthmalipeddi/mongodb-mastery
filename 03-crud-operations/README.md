# 03 — CRUD Operations

> **Goal:** Master the four fundamental database operations — Create, Read, Update, Delete.

---

## CRUD at a Glance

| Operation | PyMongo Method | Description |
|-----------|---------------|-------------|
| **Create** | `insert_one()` | Insert a single document |
| | `insert_many()` | Insert multiple documents |
| **Read** | `find_one()` | Find a single matching document |
| | `find()` | Find all matching documents (returns cursor) |
| | `count_documents()` | Count matching documents |
| | `distinct()` | Get unique values for a field |
| **Update** | `update_one()` | Update first matching document |
| | `update_many()` | Update all matching documents |
| | `replace_one()` | Replace entire document |
| **Delete** | `delete_one()` | Delete first matching document |
| | `delete_many()` | Delete all matching documents |

---

## 📂 Files in This Section

| File | Description |
|------|-------------|
| [crud_basics.py](crud_basics.py) | Basic CRUD operations with clear examples |
| [crud_advanced.py](crud_advanced.py) | Advanced operators: `$gt`, `$in`, `$regex`, dot notation, array queries |
| [exercises.md](exercises.md) | 15 practice exercises with solutions (using sample_mflix) |

---

## How to Run

```bash
# Make sure your .env file has your MongoDB connection string
python 03-crud-operations/crud_basics.py
python 03-crud-operations/crud_advanced.py
```

---

## 📌 Key Takeaways

1. Every document gets an `_id` field automatically if you don't provide one
2. `find()` returns a **cursor**, not a list — iterate over it or call `list()`
3. Always use **update operators** (`$set`, `$inc`) — don't pass a plain dict to `update_one()` or it will replace the document
4. `delete_many({})` deletes ALL documents — be careful!
5. Use **projections** to return only the fields you need

---

**Next:** [04-schema-design/](../04-schema-design/) — Learn how to model your data
