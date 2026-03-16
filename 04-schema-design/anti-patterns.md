# Schema Design Anti-Patterns

Common mistakes in MongoDB schema design and how to fix them.

---

## 1. Massive Arrays (Unbounded Growth)

**The problem:** Storing an ever-growing array in a document.

❌ **Bad:**
```json
{
  "_id": "popular_post",
  "title": "Viral Article",
  "comments": [
    {"user": "user1", "text": "Great!", "date": "2025-01-01"},
    {"user": "user2", "text": "Amazing!", "date": "2025-01-01"},
    // ... 50,000 more comments
  ]
}
```

**Why it's bad:**
- Document approaches the 16 MB limit
- Every write (new comment) rewrites the entire document
- MongoDB must move the document when it outgrows its allocated space
- Reading the post loads ALL comments into memory

✅ **Fix:** Reference comments in a separate collection.
```json
// posts collection
{"_id": "popular_post", "title": "Viral Article", "comment_count": 50002}

// comments collection
{"_id": "...", "post_id": "popular_post", "user": "user1", "text": "Great!", "date": "2025-01-01"}
```

📌 **Rule of thumb:** If an array can grow beyond ~100 items, use a separate collection.

---

## 2. Unnecessary Normalization

**The problem:** Splitting data into many collections like a SQL database.

❌ **Bad:** (treating MongoDB like SQL)
```json
// users collection
{"_id": 1, "name": "Alice", "address_id": 101}

// addresses collection
{"_id": 101, "street": "123 Main St", "city": "Portland", "user_id": 1}

// phones collection
{"_id": 201, "number": "555-0100", "type": "mobile", "user_id": 1}
```

**Why it's bad:**
- Requires multiple queries or `$lookup` to get a user's full profile
- MongoDB's `$lookup` is slower than SQL JOINs (no query planner optimization)
- Adds unnecessary complexity

✅ **Fix:** Embed data that's always read together.
```json
{
  "_id": 1,
  "name": "Alice",
  "address": {"street": "123 Main St", "city": "Portland"},
  "phones": [{"number": "555-0100", "type": "mobile"}]
}
```

---

## 3. Storing Large Binary Data in Documents

**The problem:** Embedding images, videos, or large files directly in documents.

❌ **Bad:**
```json
{
  "_id": "user_1",
  "name": "Alice",
  "profile_picture": BinData(0, "...15MB of image data..."),
  "resume": BinData(0, "...3MB of PDF data...")
}
```

**Why it's bad:**
- Quickly hits the 16 MB document limit
- Every query loads the binary data even if you don't need it
- Wastes memory and network bandwidth

✅ **Fix:** Use GridFS for files > 1 MB, or store files in object storage (S3) and save the URL.
```json
{
  "_id": "user_1",
  "name": "Alice",
  "profile_picture_url": "https://cdn.example.com/avatars/alice.jpg",
  "resume_gridfs_id": ObjectId("...")
}
```

---

## 4. Not Considering Query Patterns

**The problem:** Designing schema based on data relationships without thinking about how it will be queried.

❌ **Bad:** Storing orders separately because "orders and users are different entities."
```json
// Need to show "user profile with recent orders" — requires $lookup every time
// users collection
{"_id": 1, "name": "Alice"}

// orders collection (thousands of queries to join)
{"_id": 101, "user_id": 1, "product": "Book", "total": 29.99}
```

✅ **Fix:** If the app always shows recent orders on the profile page, embed the last N orders:
```json
{
  "_id": 1,
  "name": "Alice",
  "recent_orders": [
    {"product": "Book", "total": 29.99, "date": "2025-01-15"},
    {"product": "Course", "total": 49.99, "date": "2025-02-20"}
  ],
  "order_count": 47
}
// Full order history stays in a separate orders collection
```

---

## 5. Using MongoDB Like a Relational Database

**The problem:** Creating dozens of tiny collections with foreign keys everywhere.

❌ **Bad:**
```
collections: users, user_profiles, user_settings, user_preferences,
             user_addresses, user_phones, user_emails, user_social_links
```

**Why it's bad:**
- 7 `$lookup` operations to build a user profile
- Defeats the purpose of a document database
- More collections = more indexes = more memory usage

✅ **Fix:** Consolidate into one or two collections.
```json
// Single users collection
{
  "_id": 1,
  "name": "Alice",
  "profile": {"bio": "...", "avatar": "..."},
  "settings": {"theme": "dark", "notifications": true},
  "addresses": [...],
  "phones": [...],
  "social_links": {"twitter": "...", "github": "..."}
}
```

---

## 6. Ignoring the 16 MB Document Limit

**The problem:** Not planning for document growth.

❌ **Bad:**
```json
{
  "_id": "chat_room_general",
  "name": "General Chat",
  "messages": [
    // This array will grow to millions of items...
  ]
}
```

✅ **Fix:** Use the bucket pattern or a separate collection.
```json
// Chat messages collection (one doc per message)
{
  "room_id": "general",
  "user": "Alice",
  "text": "Hello!",
  "timestamp": ISODate("2025-01-01T12:00:00Z")
}

// Or bucket pattern (one doc per hour)
{
  "room_id": "general",
  "hour": ISODate("2025-01-01T12:00:00Z"),
  "messages": [
    {"user": "Alice", "text": "Hello!", "ts": ISODate("2025-01-01T12:00:05Z")},
    {"user": "Bob", "text": "Hi!", "ts": ISODate("2025-01-01T12:00:08Z")}
  ]
}
```

---

## 7. Missing Indexes on Referenced Fields

**The problem:** Creating references between collections but not indexing the foreign key fields.

❌ **Bad:**
```python
# Querying comments by post_id without an index — full collection scan
db.comments.find({"post_id": ObjectId("...")})
# This scans EVERY document in the comments collection!
```

✅ **Fix:** Always index fields you query or reference.
```python
db.comments.create_index("post_id")
# Now the query uses the index — orders of magnitude faster
```

📌 **Rule:** If you `$lookup` on a field, or query by a field regularly, index it.

---

## 8. Storing Computed Data Without Updating It

**The problem:** Pre-computing values (good!) but never updating them (bad!).

❌ **Bad:**
```json
{
  "product": "Widget",
  "reviews": [...],
  "avg_rating": 4.5,  // Computed once, never updated when new reviews come in
  "review_count": 100  // Stale — actual count is now 250
}
```

✅ **Fix:** Update computed fields atomically with the data change.
```python
# When adding a review, update the stats in the same operation
db.products.update_one(
    {"_id": product_id},
    {
        "$push": {"reviews": new_review},
        "$inc": {"review_count": 1, "ratings_sum": new_rating},
    }
)
# Recalculate avg in application code or a periodic job
```

---

## Summary

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Massive arrays | 16 MB limit, slow writes | Separate collection |
| Over-normalization | Too many joins | Embed related data |
| Large binaries | Wasted memory | GridFS or external storage |
| Ignoring query patterns | Slow queries | Design for access patterns |
| SQL-style design | Defeats document model | Consolidate collections |
| Ignoring size limits | Document can't grow | Bucket pattern or reference |
| Missing indexes | Collection scans | Index all query/reference fields |
| Stale computed data | Incorrect results | Update atomically |

---

## 📌 Key Takeaways

1. **Unbounded arrays are the #1 anti-pattern** — always ask "can this grow forever?"
2. **Don't normalize like SQL** — embedding is MongoDB's superpower
3. **Index your reference fields** — or `$lookup` will scan the entire collection
4. **Plan for document growth** — think about what the document looks like in 6 months
5. **Query patterns drive schema design** — if you're not sure, start with your most common queries
