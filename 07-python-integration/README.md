# 07 — Python Integration

> **Goal:** Build real applications with PyMongo, including error handling, transactions, and bulk operations.

---

## Libraries Overview

| Library | Language | Type | Best For |
|---------|----------|------|----------|
| **PyMongo** | Python | Synchronous | Scripts, web apps (Flask/Django), data pipelines |
| **Motor** | Python | Asynchronous | FastAPI, Tornado, asyncio applications |
| **Mongoose** | Node.js | ODM | Express/MERN stack applications |

---

## 📂 Files in This Section

| File | Description |
|------|-------------|
| [pymongo_basics.py](pymongo_basics.py) | Connection, CRUD, error handling, ObjectId, cursors |
| [pymongo_advanced.py](pymongo_advanced.py) | Bulk ops, transactions, change streams, GridFS |
| [mongoose_basics.js](mongoose_basics.js) | Node.js Mongoose for MERN learners |

---

## 📌 Key Takeaways

1. **PyMongo** is the official synchronous Python driver — use it for most applications
2. Always handle `ConnectionFailure` and `OperationFailure` errors
3. Use **bulk operations** when inserting/updating many documents
4. **Transactions** provide ACID guarantees for multi-document operations (requires replica set)
5. **Change streams** let you react to real-time database changes

---

**Next:** [08-web-scraper-project/](../08-web-scraper-project/) — Build a complete project
