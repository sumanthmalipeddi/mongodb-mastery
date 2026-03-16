# Schema Design Patterns

Common patterns for modeling data in MongoDB, with JSON examples and guidance.

---

## 1. One-to-One (Embedded)

Embed the related data directly in the document.

```json
{
  "_id": ObjectId("..."),
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "profile": {
    "bio": "Software engineer from Portland",
    "avatar_url": "/images/alice.jpg",
    "website": "https://alice.dev"
  }
}
```

**When to use:** The related data is always accessed with the parent document.

---

## 2. One-to-Few (Embedded Array)

Embed a small, bounded array of related items.

```json
{
  "_id": ObjectId("..."),
  "name": "Alice Johnson",
  "addresses": [
    {"type": "home", "street": "123 Main St", "city": "Portland", "state": "OR"},
    {"type": "work", "street": "456 Tech Ave", "city": "Portland", "state": "OR"}
  ]
}
```

**When to use:** The array is small (< 50 items) and won't grow unboundedly. A person has a few addresses, a product has a few variants.

---

## 3. One-to-Many (Referenced)

Store the child's `_id` in the parent, or the parent's `_id` in each child.

**Option A: Array of references in parent**
```json
// Product document
{
  "_id": ObjectId("prod_1"),
  "name": "MongoDB Book",
  "review_ids": [ObjectId("rev_1"), ObjectId("rev_2"), ObjectId("rev_3")]
}

// Review documents (separate collection)
{
  "_id": ObjectId("rev_1"),
  "product_id": ObjectId("prod_1"),
  "rating": 5,
  "text": "Great book!"
}
```

**Option B: Parent reference in child (preferred for many items)**
```json
// Product
{"_id": ObjectId("prod_1"), "name": "MongoDB Book"}

// Reviews — each points back to its product
{"_id": ObjectId("rev_1"), "product_id": ObjectId("prod_1"), "rating": 5, "text": "Great!"}
{"_id": ObjectId("rev_2"), "product_id": ObjectId("prod_1"), "rating": 4, "text": "Good."}
```

**When to use:** Hundreds or thousands of related items. Reviews, comments, log entries.

---

## 4. One-to-Squillions (Parent Reference Only)

When the "many" side is massive (millions), only store the parent reference in each child. Never store an array of child IDs in the parent.

```json
// Host (parent)
{"_id": ObjectId("host_1"), "hostname": "web-server-01", "ip": "10.0.0.1"}

// Log entries (children) — millions per host
{"_id": ObjectId("..."), "host_id": ObjectId("host_1"), "timestamp": ISODate("..."), "message": "Request received", "level": "info"}
```

**When to use:** Logging, IoT sensor data, analytics events. The parent would exceed 16 MB if it held all child IDs.

---

## 5. Many-to-Many (Array of References)

Both sides hold an array of references to the other.

```json
// Students
{
  "_id": ObjectId("student_1"),
  "name": "Alice",
  "course_ids": [ObjectId("course_1"), ObjectId("course_2")]
}

// Courses
{
  "_id": ObjectId("course_1"),
  "title": "MongoDB 101",
  "student_ids": [ObjectId("student_1"), ObjectId("student_3")]
}
```

**When to use:** Both sides are bounded and you query from both directions. Students ↔ Courses, Users ↔ Roles, Tags ↔ Articles.

📌 If one side is unbounded, only store the reference on the bounded side.

---

## 6. Polymorphic Pattern

Store different types of documents in the same collection, with a `type` field.

```json
// All in a "vehicles" collection
{"type": "car", "make": "Toyota", "model": "Camry", "doors": 4, "trunk_size": "large"}
{"type": "truck", "make": "Ford", "model": "F-150", "payload_tons": 1.5, "bed_length": "6.5ft"}
{"type": "motorcycle", "make": "Harley", "model": "Sportster", "engine_cc": 883}
```

**When to use:** Items share some fields but have type-specific fields. Product catalogs, notification systems, content management (articles, videos, podcasts in one collection).

---

## 7. Bucket Pattern

Group related time-series data into "buckets" instead of one document per event.

**Without bucketing (bad for time-series):**
```json
{"sensor_id": "temp_01", "value": 72.5, "timestamp": ISODate("2025-01-01T00:00:00Z")}
{"sensor_id": "temp_01", "value": 72.8, "timestamp": ISODate("2025-01-01T00:01:00Z")}
// ... millions of documents
```

**With bucketing (much better):**
```json
{
  "sensor_id": "temp_01",
  "date": ISODate("2025-01-01"),
  "readings_count": 1440,
  "readings": [
    {"value": 72.5, "timestamp": ISODate("2025-01-01T00:00:00Z")},
    {"value": 72.8, "timestamp": ISODate("2025-01-01T00:01:00Z")}
    // ... all readings for that day
  ],
  "summary": {
    "avg": 73.2,
    "min": 68.1,
    "max": 79.5
  }
}
```

**When to use:** Time-series data, IoT sensors, financial tick data. Reduces document count and index size dramatically.

📌 MongoDB also has a dedicated [time-series collection type](https://www.mongodb.com/docs/manual/core/timeseries-collections/) optimized for this.

---

## 8. Attribute Pattern

When you have many similar fields with different names, store them as key-value pairs in an array.

**Without attribute pattern (hard to index):**
```json
{
  "product": "T-Shirt",
  "color": "blue",
  "size": "L",
  "material": "cotton",
  "sleeve_length": "short",
  "neckline": "crew"
}
```

**With attribute pattern (easy to index and query):**
```json
{
  "product": "T-Shirt",
  "attributes": [
    {"k": "color", "v": "blue"},
    {"k": "size", "v": "L"},
    {"k": "material", "v": "cotton"},
    {"k": "sleeve_length", "v": "short"},
    {"k": "neckline", "v": "crew"}
  ]
}
```

**When to use:** Product catalogs with varying attributes, metadata-heavy documents. One index on `attributes.k` + `attributes.v` covers all attribute queries.

---

## 9. Computed Pattern

Pre-compute values that are expensive to calculate at query time.

```json
{
  "_id": ObjectId("..."),
  "title": "MongoDB Mastery",
  "ratings": [5, 4, 5, 3, 5, 4, 5],
  "ratings_count": 7,
  "ratings_sum": 31,
  "ratings_avg": 4.43
}
```

Update on each new rating:
```javascript
db.products.updateOne(
  { _id: productId },
  {
    $push: { ratings: newRating },
    $inc: { ratings_count: 1, ratings_sum: newRating },
    // Recalculate average in application code or use $set
  }
)
```

**When to use:** Dashboards, leaderboards, any frequently-read aggregated value. Trade write complexity for read performance.

---

## Summary Table

| Pattern | Use Case | Key Benefit |
|---------|----------|-------------|
| One-to-One | Profile data | Single read |
| One-to-Few | Addresses, phone numbers | No joins |
| One-to-Many | Products → Reviews | Scalable |
| One-to-Squillions | Host → Logs | Unbounded growth |
| Many-to-Many | Students ↔ Courses | Query from both sides |
| Polymorphic | Mixed content types | Flexible schema |
| Bucket | Time-series data | Fewer documents |
| Attribute | Varying attributes | Single index covers all |
| Computed | Aggregated stats | Fast reads |

---

## 📌 Key Takeaways

1. **Start with your queries** — the right pattern depends on access patterns
2. **Embed for reads, reference for writes** — embedding is fast to read, referencing avoids duplication
3. **Bounded vs unbounded** — the most critical question for array-based patterns
4. **Combine patterns** — real schemas often mix several patterns
5. **Denormalization is a feature** — it's OK to duplicate data for read performance
