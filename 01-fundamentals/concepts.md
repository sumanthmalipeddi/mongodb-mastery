# MongoDB Concepts — Deep Dive

## Document Model vs Relational Model

### Relational (SQL) Approach

In a relational database, you normalize data into separate tables and use JOINs to combine them:

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│   users       │     │   orders          │     │   products    │
├──────────────┤     ├──────────────────┤     ├──────────────┤
│ id (PK)       │◄────│ user_id (FK)      │     │ id (PK)       │
│ name          │     │ product_id (FK)   │────►│ name          │
│ email         │     │ quantity          │     │ price         │
│ created_at    │     │ order_date        │     │ category      │
└──────────────┘     └──────────────────┘     └──────────────┘
```

To get "all orders for user Alice with product details" requires a 3-table JOIN.

### Document (MongoDB) Approach

In MongoDB, you can embed related data directly in the document:

```json
{
  "_id": ObjectId("..."),
  "name": "Alice",
  "email": "alice@example.com",
  "orders": [
    {
      "product": "MongoDB Book",
      "price": 29.99,
      "quantity": 1,
      "order_date": ISODate("2025-01-15")
    },
    {
      "product": "Python Course",
      "price": 49.99,
      "quantity": 1,
      "order_date": ISODate("2025-02-20")
    }
  ]
}
```

One read fetches everything. No JOINs needed.

📌 **Key Insight:** Design your MongoDB schema based on how your application **reads** data, not how the data **relates**.

---

## BSON Data Types

MongoDB stores documents in **BSON** (Binary JSON) — a binary-encoded extension of JSON that supports additional data types.

| Type | Description | Example |
|------|-------------|---------|
| `String` | UTF-8 text | `"hello world"` |
| `Int32` | 32-bit integer | `42` |
| `Int64` (Long) | 64-bit integer | `NumberLong(9999999999)` |
| `Double` | 64-bit floating point | `3.14` |
| `Decimal128` | High-precision decimal | `NumberDecimal("19.99")` |
| `Boolean` | true/false | `true` |
| `ObjectId` | 12-byte unique identifier | `ObjectId("507f1f77bcf86cd799439011")` |
| `Date` | Milliseconds since epoch | `ISODate("2025-01-15T00:00:00Z")` |
| `Timestamp` | Internal MongoDB type | Used for replication |
| `Array` | Ordered list of values | `["a", "b", "c"]` |
| `Object` | Embedded document | `{"street": "123 Main", "city": "Portland"}` |
| `Null` | Null value | `null` |
| `Binary` | Binary data | Used for files, images |
| `Regex` | Regular expression | `/pattern/flags` |
| `MinKey/MaxKey` | Compare lower/higher than all other values | Internal use |

### ObjectId Structure

An ObjectId is 12 bytes, composed of:
```
|  4 bytes  |  5 bytes   |  3 bytes  |
| timestamp | random     | counter   |
```

- **Timestamp**: Seconds since Unix epoch (you can extract the creation time)
- **Random**: Machine/process unique value
- **Counter**: Incrementing value for uniqueness

```python
from bson import ObjectId
oid = ObjectId()
print(oid.generation_time)  # When the document was created
```

---

## When to Use MongoDB vs SQL

### Choose MongoDB When:

- ✅ Your schema changes frequently (rapid prototyping, evolving requirements)
- ✅ You have hierarchical or nested data (user profiles, product catalogs, content management)
- ✅ You need horizontal scaling for large datasets
- ✅ Your read patterns benefit from denormalization (fewer JOINs = faster reads)
- ✅ You work with semi-structured data (logs, IoT sensor data, social media)
- ✅ You want flexible full-text search and geospatial queries built in

### Choose SQL When:

- ✅ You have highly relational data with many-to-many relationships
- ✅ You need complex transactions spanning many tables
- ✅ Data integrity constraints are critical (banking, accounting)
- ✅ Your schema is stable and well-defined
- ✅ You need advanced SQL features (window functions, CTEs, stored procedures)
- ✅ Your team has deep SQL expertise

### Both Work Fine For:

- CRUD applications, REST APIs, microservices, e-commerce, analytics

---

## CAP Theorem and MongoDB

The **CAP theorem** states that a distributed system can only guarantee two of three properties:

| Property | Description |
|----------|-------------|
| **C**onsistency | Every read receives the most recent write |
| **A**vailability | Every request receives a response |
| **P**artition Tolerance | System operates despite network failures |

**MongoDB prioritizes CP (Consistency + Partition Tolerance):**

- In a replica set, writes go to the **primary** node (consistency)
- If the primary fails, an **election** chooses a new primary (partition tolerance)
- During election (~10 seconds), writes are unavailable (sacrifices availability)

You can tune this behavior:
- `readPreference: "secondary"` → Favor availability (may read stale data)
- `writeConcern: { w: "majority" }` → Favor consistency (wait for replication)

---

## Key Terminology Mapping

| SQL Term | MongoDB Term | Notes |
|----------|-------------|-------|
| Database | Database | Same concept |
| Table | Collection | Collections are schema-free |
| Row | Document | Documents are JSON-like (BSON) |
| Column | Field | Fields can vary per document |
| Primary Key | `_id` | Auto-generated ObjectId by default |
| Foreign Key | Reference | Manual reference (ObjectId stored in field) |
| JOIN | `$lookup` | Aggregation pipeline stage |
| INDEX | Index | Similar concept, similar performance impact |
| VIEW | View | MongoDB supports read-only views |
| Transaction | Transaction | Multi-document ACID transactions (v4.0+) |
| Schema | Validation Rules | Optional JSON Schema validation |
| Stored Procedure | — | Use aggregation pipelines or app logic |
| Trigger | Change Streams | Real-time change notifications |
| GROUP BY | `$group` | Aggregation pipeline stage |

---

## Document Size Limits

⚠️ **Maximum document size: 16 MB**

This is a hard limit in MongoDB. If your document might grow beyond 16 MB (e.g., unbounded arrays), you need to restructure your schema.

For files larger than 16 MB, use **GridFS** — MongoDB's specification for storing large files by splitting them into chunks.

---

## 📌 Key Takeaways

1. MongoDB's **document model** stores related data together, reducing the need for JOINs
2. **BSON** extends JSON with types like ObjectId, Date, Decimal128, and Binary
3. **ObjectId** is a 12-byte unique identifier with an embedded timestamp
4. MongoDB fits the **CP** side of the CAP theorem — consistency and partition tolerance
5. Choose MongoDB for **flexible schemas** and **hierarchical data**; choose SQL for **highly relational data** and **complex transactions**
6. Documents have a **16 MB size limit** — design schemas accordingly
7. Think in terms of **access patterns**, not entity relationships

---

**Next:** [cheatsheet.md](cheatsheet.md) — Quick SQL → MongoDB reference
