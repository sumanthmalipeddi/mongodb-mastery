# 01 — MongoDB Fundamentals

> **Goal:** Understand what MongoDB is, how it differs from SQL databases, and why it matters.

---

## What is MongoDB?

MongoDB is an open-source **document database** (also called a NoSQL database). Instead of storing data in rows and columns like SQL databases, MongoDB stores data as flexible **JSON-like documents** (technically BSON — Binary JSON).

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "age": 29,
  "address": {
    "street": "123 Main St",
    "city": "Portland",
    "state": "OR"
  },
  "hobbies": ["reading", "hiking", "coding"]
}
```

Notice: nested objects, arrays, and flexible structure — all in one document.

---

## Core Concepts

### Documents
The basic unit of data in MongoDB. Similar to a row in SQL, but far more flexible. Documents are stored as BSON (Binary JSON) and can contain nested objects and arrays.

### Collections
A group of documents. Similar to a table in SQL, but collections don't enforce a schema — each document can have different fields.

### Databases
A container for collections. A single MongoDB server can host multiple databases.

### _id Field
Every document has a unique `_id` field (auto-generated as an ObjectId if you don't provide one). This is the primary key.

---

## Why MongoDB?

| Feature | Benefit |
|---------|---------|
| **Flexible Schema** | No migrations needed — add fields anytime |
| **Document Model** | Store related data together, fewer JOINs |
| **Horizontal Scaling** | Built-in sharding for massive datasets |
| **Rich Query Language** | Powerful queries, aggregation framework, full-text search |
| **Developer Experience** | JSON-native, works naturally with JavaScript/Python |
| **Atlas Cloud** | Fully managed, free tier available |

---

## MongoDB vs SQL at a Glance

| SQL Concept | MongoDB Equivalent |
|-------------|-------------------|
| Database | Database |
| Table | Collection |
| Row | Document |
| Column | Field |
| Primary Key | `_id` field |
| JOIN | Embedding or `$lookup` |
| Schema | Flexible (optional validation) |

---

## 📂 Files in This Section

| File | Description |
|------|-------------|
| [concepts.md](concepts.md) | Deep dive: document model, BSON types, MongoDB vs SQL |
| [cheatsheet.md](cheatsheet.md) | Quick reference: SQL → MongoDB query mapping |

---

## 📌 Key Takeaways

1. MongoDB stores data as **flexible JSON-like documents**, not rows and columns
2. **Collections** are like tables, but documents in a collection can have different structures
3. The **document model** lets you store related data together, reducing the need for JOINs
4. Every document has a unique **`_id`** field
5. MongoDB excels at **flexible schemas**, **horizontal scaling**, and **developer productivity**

---

**Next:** [02-setup/](../02-setup/) — Get MongoDB running locally or in the cloud
