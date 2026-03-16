# MongoDB Indexing Guide

A comprehensive reference for all MongoDB index types.

---

## How Indexes Work

MongoDB indexes use a **B-tree** data structure. When you create an index on a field, MongoDB builds a sorted structure that maps field values to document locations.

```
Index on "age":
  18 → doc_4, doc_12
  21 → doc_1, doc_7, doc_15
  25 → doc_3
  29 → doc_8, doc_22
  35 → doc_2
```

Without an index, MongoDB scans all documents (**COLLSCAN**). With an index, it does a targeted **IXSCAN**.

---

## 1. Single Field Index

The simplest index type. Index on one field, ascending (1) or descending (-1).

```python
# Create index on "email" ascending
db.users.create_index("email")

# Equivalent to:
db.users.create_index([("email", 1)])

# Descending (for sorting newest-first)
db.users.create_index([("created_at", -1)])
```

**When to use:** Any field you frequently filter or sort by.

📌 For single-field indexes, sort direction (1 vs -1) doesn't matter for queries — MongoDB can traverse the index in either direction.

---

## 2. Compound Index

Index on multiple fields. **Field order matters!**

```python
db.orders.create_index([("status", 1), ("created_at", -1)])
```

This index supports:
- ✅ `find({"status": "active"})` — uses the first field
- ✅ `find({"status": "active"}).sort("created_at", -1)` — uses both fields
- ✅ `find({"status": "active", "created_at": {"$gte": date}})` — uses both
- ❌ `find({"created_at": {"$gte": date}})` — can't use index (wrong prefix)

### The ESR Rule

Order compound index fields by: **Equality → Sort → Range**

```python
# Query: find active users, sort by name, age between 20-30
# Equality: status = "active"
# Sort: name
# Range: age between 20-30

# Optimal index:
db.users.create_index([("status", 1), ("name", 1), ("age", 1)])
```

---

## 3. Multikey Index

Automatically created when you index a field that contains an array.

```python
# Document: {"tags": ["python", "mongodb", "docker"]}
db.posts.create_index("tags")

# Now these are fast:
db.posts.find({"tags": "mongodb"})
db.posts.find({"tags": {"$in": ["python", "docker"]}})
```

📌 MongoDB creates an index entry for **each element** in the array. One document with 10 tags creates 10 index entries.

⚠️ A compound index can have at most **one** multikey (array) field.

---

## 4. Text Index

Enables full-text search with `$text` queries.

```python
# Create a text index on the "description" field
db.products.create_index([("description", "text")])

# Search for words
db.products.find({"$text": {"$search": "mongodb tutorial"}})

# Phrase search (exact match)
db.products.find({"$text": {"$search": '"mongodb tutorial"'}})

# Exclude a word
db.products.find({"$text": {"$search": "mongodb -sql"}})

# Sort by relevance score
db.products.find(
    {"$text": {"$search": "mongodb"}},
    {"score": {"$meta": "textScore"}}
).sort([("score", {"$meta": "textScore"})])
```

📌 Only **one** text index per collection. You can include multiple fields:
```python
db.products.create_index([("title", "text"), ("description", "text")])
```

---

## 5. Geospatial Indexes

### 2dsphere (for Earth-like geometry)

```python
# Document with GeoJSON point
# {"location": {"type": "Point", "coordinates": [-122.68, 45.52]}}

db.places.create_index([("location", "2dsphere")])

# Find places within 1km of a point
db.places.find({
    "location": {
        "$near": {
            "$geometry": {"type": "Point", "coordinates": [-122.68, 45.52]},
            "$maxDistance": 1000  # meters
        }
    }
})
```

### 2d (for flat geometry)

```python
# For legacy coordinate pairs: {"location": [x, y]}
db.places.create_index([("location", "2d")])
```

---

## 6. Hashed Index

Indexes the hash of a field value. Used primarily for hash-based sharding.

```python
db.users.create_index([("user_id", "hashed")])
```

- ✅ Supports equality queries: `find({"user_id": 123})`
- ❌ Does NOT support range queries: `find({"user_id": {"$gt": 100}})`

---

## 7. TTL Index (Time-To-Live)

Automatically deletes documents after a specified time.

```python
# Delete documents 24 hours after their "created_at" field
db.sessions.create_index("created_at", expireAfterSeconds=86400)

# Delete documents at a specific time (set "expires_at" to the exact time)
db.sessions.create_index("expires_at", expireAfterSeconds=0)
```

**Use cases:** Session tokens, temporary data, cache entries, log rotation.

📌 TTL indexes only work on fields containing `datetime` values. The background thread runs every 60 seconds.

---

## 8. Wildcard Index

Index all fields or all fields matching a pattern. Useful for dynamic schemas.

```python
# Index ALL fields in the document
db.data.create_index({"$**": 1})

# Index all fields under "attributes"
db.products.create_index({"attributes.$**": 1})
```

**When to use:** Collections with unpredictable field names (like the attribute pattern).

⚠️ Wildcard indexes can be large and don't replace well-designed compound indexes.

---

## 9. Partial Index

Only index documents that match a filter. Smaller index = less storage and memory.

```python
# Only index active users
db.users.create_index(
    "email",
    partialFilterExpression={"status": "active"}
)
```

⚠️ Queries must include the partial filter condition to use the index.

---

## 10. Sparse Index

Only index documents where the indexed field exists (skips documents without the field).

```python
db.users.create_index("phone", sparse=True)
```

📌 Partial indexes are more flexible — they've largely replaced sparse indexes.

---

## 11. Unique Index

Prevent duplicate values.

```python
db.users.create_index("email", unique=True)

# Compound unique index
db.events.create_index([("user_id", 1), ("event_date", 1)], unique=True)
```

📌 The `_id` field always has a unique index.

---

## Index Intersection

MongoDB can combine two or more indexes to fulfill a query.

```python
# Given these separate indexes:
db.orders.create_index("status")
db.orders.create_index("total")

# MongoDB MAY use index intersection for:
db.orders.find({"status": "active", "total": {"$gt": 100}})
```

📌 A compound index is usually faster than index intersection. But intersection works when you can't predict all query combinations.

---

## Covered Queries

A **covered query** is fulfilled entirely from the index, without reading the actual documents. This is the fastest possible query.

Requirements:
1. All queried fields are in the index
2. All returned fields are in the index
3. No field in the query is an array

```python
# Index on name and email
db.users.create_index([("name", 1), ("email", 1)])

# This is a covered query (only returns indexed fields, excludes _id):
db.users.find({"name": "Alice"}, {"name": 1, "email": 1, "_id": 0})
```

---

## Managing Indexes

```python
# List all indexes
db.users.index_information()

# Drop a specific index
db.users.drop_index("email_1")

# Drop all indexes (except _id)
db.users.drop_indexes()

# Get index size
db.users.stats()["totalIndexSize"]
```

---

## 📌 Key Takeaways

1. **Every query should use an index** — COLLSCAN on large collections is unacceptable
2. **Compound index field order matters** — follow the ESR rule (Equality, Sort, Range)
3. **One text index per collection** — combine fields in a single text index
4. **TTL indexes** auto-clean temporary data — great for sessions and caches
5. **Partial indexes** save space by only indexing relevant documents
6. **Covered queries** are the fastest — they never touch the documents
7. **More indexes = slower writes** — only create indexes you actually use
8. Use `.explain()` to verify your indexes are working (see explain_queries.py)
