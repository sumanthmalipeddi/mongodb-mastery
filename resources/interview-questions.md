# MongoDB Interview Questions

30 questions with answers, covering all major topics.

---

## Basics (1–5)

### 1. What is MongoDB and how does it differ from SQL databases?
<details>
<summary>Answer</summary>

MongoDB is a document-oriented NoSQL database that stores data in flexible, JSON-like documents (BSON). Key differences from SQL:

- **Schema:** MongoDB is schema-flexible (documents in a collection can have different fields). SQL requires a fixed schema defined upfront.
- **Data model:** MongoDB stores related data together in documents. SQL normalizes data across tables with JOINs.
- **Scaling:** MongoDB is designed for horizontal scaling (sharding). SQL traditionally scales vertically.
- **Transactions:** SQL has had ACID transactions since the beginning. MongoDB added multi-document ACID transactions in version 4.0.
- **Query language:** MongoDB uses JSON-based query syntax. SQL uses the SQL language.
</details>

### 2. What is BSON and how does it differ from JSON?
<details>
<summary>Answer</summary>

BSON (Binary JSON) is the binary-encoded format MongoDB uses to store documents. Differences:

- **Additional types:** BSON supports ObjectId, Date, Decimal128, Binary, Regex — types JSON doesn't have
- **Binary format:** BSON is more efficient for storage and traversal
- **Field ordering:** BSON preserves field order
- **Size info:** BSON includes length prefixes, making it faster to traverse

JSON is used for the query API and display; BSON is used for internal storage.
</details>

### 3. What is an ObjectId? What information does it contain?
<details>
<summary>Answer</summary>

ObjectId is a 12-byte unique identifier used as the default `_id` value. It consists of:
- **4 bytes:** Unix timestamp (seconds since epoch)
- **5 bytes:** Random value unique to the machine/process
- **3 bytes:** Incrementing counter

You can extract the creation timestamp from an ObjectId: `ObjectId("...").getTimestamp()`. ObjectIds are roughly sortable by creation time.
</details>

### 4. What is the maximum document size in MongoDB?
<details>
<summary>Answer</summary>

**16 MB.** This is a hard limit. If you need to store larger data, use **GridFS**, which splits files into 255 KB chunks and stores them across two collections (`fs.files` and `fs.chunks`).

This limit also means you should avoid unbounded arrays in documents — they could cause the document to exceed 16 MB over time.
</details>

### 5. Explain the difference between a database, collection, and document.
<details>
<summary>Answer</summary>

- **Database:** A container for collections. Analogous to a SQL database.
- **Collection:** A group of documents within a database. Analogous to a SQL table, but without a fixed schema.
- **Document:** A single record stored as BSON. Analogous to a SQL row, but can contain nested objects and arrays.

Hierarchy: Server → Database → Collection → Document → Field
</details>

---

## CRUD and Querying (6–10)

### 6. What is the difference between `find()` and `findOne()`?
<details>
<summary>Answer</summary>

- `find()` returns a **cursor** — an iterator over all matching documents. You iterate through it to get results.
- `findOne()` returns a **single document** (the first match) or `null`/`None` if no match.

`find()` is lazy — it doesn't fetch all documents at once. It uses batches (default 101 documents in the first batch, then 16 MB batches).
</details>

### 7. How do you query nested documents in MongoDB?
<details>
<summary>Answer</summary>

Use **dot notation** to query fields within nested documents:

```javascript
// Document: { address: { city: "Portland", state: "OR" } }
db.users.find({ "address.city": "Portland" })

// Nested within arrays of objects:
// Document: { orders: [{ status: "shipped", total: 50 }] }
db.users.find({ "orders.status": "shipped" })
```
</details>

### 8. What operators would you use for array queries?
<details>
<summary>Answer</summary>

- `$in` — Match any value in an array: `{ tags: { $in: ["a", "b"] } }`
- `$all` — Match ALL values: `{ tags: { $all: ["a", "b"] } }`
- `$size` — Match exact array length: `{ tags: { $size: 3 } }`
- `$elemMatch` — Match array elements meeting multiple conditions: `{ results: { $elemMatch: { score: { $gte: 80 }, subject: "math" } } }`
- Simple match — Any element equals: `{ tags: "mongodb" }`
</details>

### 9. What is the difference between `$set` and replacing a document?
<details>
<summary>Answer</summary>

- `$set` updates only the specified fields, leaving others unchanged: `updateOne({_id: 1}, {$set: {name: "Alice"}})`
- `replaceOne` replaces the **entire document** (except `_id`): `replaceOne({_id: 1}, {name: "Alice"})` — all other fields are removed!

Always use `$set` (or other update operators) unless you intentionally want to replace the whole document.
</details>

### 10. How does MongoDB handle concurrent writes to the same document?
<details>
<summary>Answer</summary>

MongoDB uses **document-level locking** (WiredTiger storage engine). Each write acquires an exclusive lock on the document being modified. This means:

- Two writes to **different documents** can happen concurrently
- Two writes to the **same document** are serialized (one waits for the other)
- Atomic update operators (`$set`, `$inc`) are applied atomically at the document level
- For multi-document atomicity, use **transactions** (requires replica set)
</details>

---

## Schema Design (11–15)

### 11. When should you embed vs reference documents?
<details>
<summary>Answer</summary>

**Embed when:**
- Data is always read together (one-to-one or one-to-few)
- The embedded data is bounded (won't grow indefinitely)
- You want atomic updates on the parent + embedded data

**Reference when:**
- Data is accessed independently
- The related data is large or unbounded (one-to-many, one-to-squillions)
- You need to avoid data duplication
- The related data changes frequently and independently

Rule of thumb: Embed what you read together, reference what you query independently.
</details>

### 12. What is the #1 schema design anti-pattern in MongoDB?
<details>
<summary>Answer</summary>

**Unbounded arrays.** Storing an ever-growing array in a document (like all comments on a popular post, or all events for a user). Problems:
- Document approaches the 16 MB limit
- Every write rewrites the entire document
- Reading the document loads all array elements into memory

Fix: Move the array items to a separate collection with a reference back to the parent.
</details>

### 13. Explain the Bucket Pattern.
<details>
<summary>Answer</summary>

The Bucket Pattern groups related time-series data into a single document instead of one document per data point. For example, instead of one document per sensor reading per second, you create one document per sensor per hour containing all readings.

Benefits: Fewer documents, smaller indexes, better cache utilization. MongoDB also has a dedicated time-series collection type that optimizes this automatically.
</details>

### 14. What is denormalization? Is it acceptable in MongoDB?
<details>
<summary>Answer</summary>

Denormalization means duplicating data across documents to avoid joins. In SQL, this is generally avoided. In MongoDB, **denormalization is a core strategy.**

Example: Storing the author's name in every blog post document (instead of just a reference) so you can display posts without joining to the users collection.

Tradeoff: Faster reads, but you must update all copies when the source data changes. Acceptable when the duplicated data changes rarely.
</details>

### 15. How would you model a many-to-many relationship?
<details>
<summary>Answer</summary>

Store an array of references on one or both sides:

```javascript
// Students
{ _id: "s1", name: "Alice", course_ids: ["c1", "c2"] }

// Courses
{ _id: "c1", title: "MongoDB 101", student_ids: ["s1", "s3"] }
```

If both arrays are bounded, store references on both sides. If one side is unbounded, only store references on the bounded side. Use `$lookup` to join when needed.
</details>

---

## Indexing & Performance (16–20)

### 16. What happens if you don't create indexes?
<details>
<summary>Answer</summary>

Without indexes, every query performs a **collection scan (COLLSCAN)** — MongoDB reads every document in the collection to find matches. On a collection with millions of documents, this can take seconds or minutes.

The only index created automatically is `_id`. All other indexes must be created explicitly.
</details>

### 17. Explain the ESR rule for compound indexes.
<details>
<summary>Answer</summary>

The ESR rule determines the optimal field order in a compound index:
- **E**quality fields first (exact match conditions like `status = "active"`)
- **S**ort fields second (fields in the `sort()` clause)
- **R**ange fields last (conditions like `$gt`, `$lt`, `$in`)

This order maximizes the portion of the index MongoDB can use efficiently.
</details>

### 18. What is a covered query?
<details>
<summary>Answer</summary>

A covered query is fulfilled entirely from the index without reading the actual documents. Requirements:
1. All query fields are in the index
2. All projected (returned) fields are in the index
3. `_id` is either in the index or excluded from projection
4. No queried field is an array

Covered queries are the fastest possible queries — they never touch disk for document reads.
</details>

### 19. What are TTL indexes?
<details>
<summary>Answer</summary>

TTL (Time-To-Live) indexes automatically delete documents after a specified time period. Created on a date field:

```javascript
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })
```

Documents are deleted when `createdAt + 3600 seconds` has passed. The background cleanup runs every 60 seconds. Use cases: session tokens, temporary caches, log rotation.
</details>

### 20. How do you analyze query performance?
<details>
<summary>Answer</summary>

Use `.explain()` to see the query execution plan:

```javascript
db.users.find({ age: { $gt: 25 } }).explain("executionStats")
```

Key fields to check:
- `winningPlan.stage`: `IXSCAN` (good) vs `COLLSCAN` (bad)
- `totalDocsExamined`: How many documents MongoDB read
- `totalKeysExamined`: How many index entries scanned
- `nReturned`: How many documents returned
- `executionTimeMillis`: Wall-clock time

Red flag: `totalDocsExamined` >> `nReturned` means the query is scanning too many documents.
</details>

---

## Aggregation (21–23)

### 21. What is the aggregation pipeline?
<details>
<summary>Answer</summary>

The aggregation pipeline processes documents through a series of stages, where each stage transforms the data:

`Documents → $match → $group → $sort → $limit → Results`

Common stages: `$match` (filter), `$group` (aggregate), `$sort`, `$limit`, `$project` (reshape), `$lookup` (join), `$unwind` (flatten arrays), `$facet` (parallel pipelines).

Pipeline order matters: `$match` should come early to reduce data volume before expensive stages.
</details>

### 22. What is the difference between `$lookup` and embedding?
<details>
<summary>Answer</summary>

- **Embedding:** Related data is stored directly in the document. Reading is fast (single document read), but updates to shared data require updating all copies.
- **`$lookup`:** Performs a left outer join at query time. Data stays normalized (no duplication), but requires an additional lookup for each query.

`$lookup` is slower than embedding for reads. Use embedding for frequently accessed related data; use `$lookup` for data that's occasionally joined or too large to embed.
</details>

### 23. Explain the `$facet` stage.
<details>
<summary>Answer</summary>

`$facet` runs multiple aggregation pipelines in parallel on the same input documents. Each sub-pipeline produces its own results.

```javascript
{ $facet: {
    "priceStats": [{ $group: { _id: null, avg: { $avg: "$price" } } }],
    "topCategories": [{ $group: { _id: "$category", count: { $sum: 1 } } }, { $sort: { count: -1 } }, { $limit: 5 }],
    "totalCount": [{ $count: "total" }]
}}
```

Use case: Dashboard queries where you need multiple aggregations from the same data set in a single round trip.
</details>

---

## Replication & Sharding (24–26)

### 24. What is a replica set? Why use one?
<details>
<summary>Answer</summary>

A replica set is a group of MongoDB servers maintaining identical copies of data. It provides:
1. **High availability:** If the primary fails, a secondary is automatically elected as the new primary (~10 seconds)
2. **Data redundancy:** Multiple copies prevent data loss
3. **Read scaling:** Distribute reads across secondaries

A replica set has one primary (accepts writes) and one or more secondaries (replicate from primary). Atlas clusters are always replica sets.
</details>

### 25. How do you choose a shard key?
<details>
<summary>Answer</summary>

A good shard key should have:
- **High cardinality:** Many unique values for even distribution
- **Low frequency:** No single value dominates
- **Non-monotonic:** Not always increasing (like timestamps — creates a hot shard)
- **Query isolation:** Common queries include the shard key (so they go to one shard)

Bad shard keys: boolean fields, low-cardinality enums, monotonically increasing values (timestamps, auto-increment IDs).

Good shard keys: hashed user_id, compound keys like `{region: 1, user_id: 1}`.

⚠️ The shard key cannot be changed after sharding — choose carefully.
</details>

### 26. What is the difference between replication and sharding?
<details>
<summary>Answer</summary>

- **Replication:** Every member has a complete copy of all data. Purpose: availability and redundancy.
- **Sharding:** Each shard holds a different subset of data. Purpose: horizontal scaling.

In production, you typically use both: each shard is itself a replica set.

Replication = same data on multiple servers. Sharding = different data on different servers.
</details>

---

## Transactions & Consistency (27–28)

### 27. Does MongoDB support ACID transactions?
<details>
<summary>Answer</summary>

Yes, since version 4.0. MongoDB supports multi-document ACID transactions across multiple operations, collections, and databases. Transactions require a replica set.

Single-document operations have always been atomic in MongoDB. Multi-document transactions add atomicity across multiple documents.

```python
with client.start_session() as session:
    with session.start_transaction():
        collection1.insert_one(doc1, session=session)
        collection2.update_one(filter, update, session=session)
        # Commits atomically at end of with block
```

Best practice: Design your schema to minimize the need for multi-document transactions.
</details>

### 28. What are write concern and read concern?
<details>
<summary>Answer</summary>

**Write concern** controls how many replica set members must acknowledge a write:
- `w: 1` — Primary only (default, fast)
- `w: "majority"` — Majority of members (durable, recommended for important data)
- `w: 0` — No acknowledgment (fire-and-forget, fastest but risky)

**Read concern** controls the consistency of data returned:
- `local` — Most recent data on the queried member (default)
- `majority` — Only data acknowledged by a majority (consistent)
- `linearizable` — Strongest guarantee, reflects all successful majority writes

Together, `w: "majority"` + read concern `"majority"` provides the strongest consistency guarantees.
</details>

---

## Atlas & Production (29–30)

### 29. What is MongoDB Atlas?
<details>
<summary>Answer</summary>

MongoDB Atlas is the fully managed cloud database service by MongoDB, Inc. It provides:
- Automated deployment, scaling, and patching
- Built-in replication (every cluster is a replica set)
- Automated backups with point-in-time recovery
- Monitoring, alerting, and performance advisor
- Global clusters with zone sharding
- Atlas Vector Search for AI applications
- Free tier (M0) with 512 MB storage

Atlas runs on AWS, GCP, and Azure.
</details>

### 30. What would you check if MongoDB queries suddenly become slow?
<details>
<summary>Answer</summary>

Systematic debugging approach:

1. **Check explain plans:** Are queries using indexes? Look for COLLSCAN.
2. **Check Atlas Performance Advisor:** Are there suggested missing indexes?
3. **Check server metrics:** CPU, memory, disk I/O, connections
4. **Check replication lag:** Are secondaries falling behind?
5. **Check for lock contention:** `db.currentOp()` for long-running operations
6. **Check for schema issues:** Documents too large? Unbounded arrays?
7. **Check connection pooling:** Too many connections? Pool exhaustion?
8. **Check recent changes:** New code? New query patterns? Data growth?
9. **Check the profiler:** `db.system.profile.find().sort({ts: -1})` for slow queries
10. **Check disk space:** Full disks cause MongoDB to crash

Most common cause: missing index on a query that used to be fast because the collection was small.
</details>
