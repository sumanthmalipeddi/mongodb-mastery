# SQL → MongoDB Cheatsheet

Quick reference for translating SQL queries to MongoDB shell commands and PyMongo.

---

## CREATE / INSERT

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `CREATE TABLE users (id INT, name VARCHAR(50), age INT)` | Collections are created implicitly on first insert | Collections are created implicitly |
| `INSERT INTO users (name, age) VALUES ('Alice', 25)` | `db.users.insertOne({name: "Alice", age: 25})` | `db.users.insert_one({"name": "Alice", "age": 25})` |
| `INSERT INTO users VALUES ('Bob', 30), ('Carol', 28)` | `db.users.insertMany([{name: "Bob", age: 30}, {name: "Carol", age: 28}])` | `db.users.insert_many([{"name": "Bob", "age": 30}, {"name": "Carol", "age": 28}])` |

---

## SELECT / FIND

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `SELECT * FROM users` | `db.users.find()` | `db.users.find()` |
| `SELECT name, age FROM users` | `db.users.find({}, {name: 1, age: 1})` | `db.users.find({}, {"name": 1, "age": 1})` |
| `SELECT * FROM users WHERE age = 25` | `db.users.find({age: 25})` | `db.users.find({"age": 25})` |
| `SELECT * FROM users WHERE age > 25` | `db.users.find({age: {$gt: 25}})` | `db.users.find({"age": {"$gt": 25}})` |
| `SELECT * FROM users WHERE age >= 25` | `db.users.find({age: {$gte: 25}})` | `db.users.find({"age": {"$gte": 25}})` |
| `SELECT * FROM users WHERE age < 30` | `db.users.find({age: {$lt: 30}})` | `db.users.find({"age": {"$lt": 30}})` |
| `SELECT * FROM users WHERE age != 25` | `db.users.find({age: {$ne: 25}})` | `db.users.find({"age": {"$ne": 25}})` |
| `SELECT * FROM users WHERE name LIKE 'Al%'` | `db.users.find({name: /^Al/})` | `db.users.find({"name": {"$regex": "^Al"}})` |
| `SELECT * FROM users WHERE age IN (25, 30)` | `db.users.find({age: {$in: [25, 30]}})` | `db.users.find({"age": {"$in": [25, 30]}})` |
| `SELECT * FROM users WHERE age BETWEEN 25 AND 30` | `db.users.find({age: {$gte: 25, $lte: 30}})` | `db.users.find({"age": {"$gte": 25, "$lte": 30}})` |
| `SELECT * FROM users WHERE email IS NULL` | `db.users.find({email: null})` | `db.users.find({"email": None})` |
| `SELECT * FROM users WHERE email IS NOT NULL` | `db.users.find({email: {$ne: null}})` | `db.users.find({"email": {"$ne": None}})` |
| `SELECT DISTINCT(name) FROM users` | `db.users.distinct("name")` | `db.users.distinct("name")` |
| `SELECT * FROM users LIMIT 5` | `db.users.find().limit(5)` | `db.users.find().limit(5)` |
| `SELECT * FROM users LIMIT 5 OFFSET 10` | `db.users.find().skip(10).limit(5)` | `db.users.find().skip(10).limit(5)` |
| `SELECT COUNT(*) FROM users` | `db.users.countDocuments()` | `db.users.count_documents({})` |
| `SELECT COUNT(*) FROM users WHERE age > 25` | `db.users.countDocuments({age: {$gt: 25}})` | `db.users.count_documents({"age": {"$gt": 25}})` |

---

## AND / OR / NOT

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `WHERE age > 25 AND name = 'Alice'` | `{age: {$gt: 25}, name: "Alice"}` | `{"age": {"$gt": 25}, "name": "Alice"}` |
| `WHERE age > 25 OR name = 'Alice'` | `{$or: [{age: {$gt: 25}}, {name: "Alice"}]}` | `{"$or": [{"age": {"$gt": 25}}, {"name": "Alice"}]}` |
| `WHERE NOT (age > 25)` | `{age: {$not: {$gt: 25}}}` | `{"age": {"$not": {"$gt": 25}}}` |

---

## ORDER BY / SORT

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `ORDER BY age ASC` | `.sort({age: 1})` | `.sort("age", 1)` |
| `ORDER BY age DESC` | `.sort({age: -1})` | `.sort("age", -1)` |
| `ORDER BY name ASC, age DESC` | `.sort({name: 1, age: -1})` | `.sort([("name", 1), ("age", -1)])` |

---

## UPDATE

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `UPDATE users SET age = 26 WHERE name = 'Alice'` | `db.users.updateOne({name: "Alice"}, {$set: {age: 26}})` | `db.users.update_one({"name": "Alice"}, {"$set": {"age": 26}})` |
| `UPDATE users SET age = age + 1 WHERE age > 25` | `db.users.updateMany({age: {$gt: 25}}, {$inc: {age: 1}})` | `db.users.update_many({"age": {"$gt": 25}}, {"$inc": {"age": 1}})` |

### Update Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `$set` | Set field value | `{$set: {age: 26}}` |
| `$unset` | Remove field | `{$unset: {age: ""}}` |
| `$inc` | Increment by value | `{$inc: {age: 1}}` |
| `$mul` | Multiply by value | `{$mul: {price: 1.1}}` |
| `$rename` | Rename field | `{$rename: {nm: "name"}}` |
| `$push` | Add to array | `{$push: {tags: "new"}}` |
| `$pull` | Remove from array | `{$pull: {tags: "old"}}` |
| `$addToSet` | Add to array (no duplicates) | `{$addToSet: {tags: "unique"}}` |

---

## DELETE

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `DELETE FROM users WHERE name = 'Alice'` | `db.users.deleteOne({name: "Alice"})` | `db.users.delete_one({"name": "Alice"})` |
| `DELETE FROM users WHERE age < 18` | `db.users.deleteMany({age: {$lt: 18}})` | `db.users.delete_many({"age": {"$lt": 18}})` |
| `DELETE FROM users` (all rows) | `db.users.deleteMany({})` | `db.users.delete_many({})` |
| `DROP TABLE users` | `db.users.drop()` | `db.users.drop()` |

---

## JOIN → $lookup

**SQL:**
```sql
SELECT u.name, o.product
FROM users u
JOIN orders o ON u.id = o.user_id
```

**MongoDB Aggregation:**
```javascript
db.users.aggregate([
  {
    $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "user_id",
      as: "orders"
    }
  }
])
```

**PyMongo:**
```python
db.users.aggregate([
    {
        "$lookup": {
            "from": "orders",
            "localField": "_id",
            "foreignField": "user_id",
            "as": "orders"
        }
    }
])
```

---

## GROUP BY → $group

**SQL:**
```sql
SELECT author, COUNT(*) as count
FROM books
GROUP BY author
HAVING count > 5
ORDER BY count DESC
```

**MongoDB:**
```javascript
db.books.aggregate([
  { $group: { _id: "$author", count: { $sum: 1 } } },
  { $match: { count: { $gt: 5 } } },
  { $sort: { count: -1 } }
])
```

---

## INDEX

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `CREATE INDEX idx_name ON users(name)` | `db.users.createIndex({name: 1})` | `db.users.create_index("name")` |
| `CREATE INDEX idx_comp ON users(name, age)` | `db.users.createIndex({name: 1, age: -1})` | `db.users.create_index([("name", 1), ("age", -1)])` |
| `CREATE UNIQUE INDEX ON users(email)` | `db.users.createIndex({email: 1}, {unique: true})` | `db.users.create_index("email", unique=True)` |
| `DROP INDEX idx_name ON users` | `db.users.dropIndex("name_1")` | `db.users.drop_index("name_1")` |

---

## Comparison Operators Quick Reference

| SQL | MongoDB |
|-----|---------|
| `=` | `{field: value}` or `$eq` |
| `!=` | `$ne` |
| `>` | `$gt` |
| `>=` | `$gte` |
| `<` | `$lt` |
| `<=` | `$lte` |
| `IN` | `$in` |
| `NOT IN` | `$nin` |
| `LIKE` | `$regex` |
| `IS NULL` | `{field: null}` |
| `EXISTS` | `$exists` |

---

## 📌 Key Takeaways

1. Most SQL operations have a direct MongoDB equivalent
2. MongoDB uses **operators** (`$gt`, `$set`, `$in`) instead of SQL keywords
3. **Aggregation pipeline** replaces GROUP BY, HAVING, and subqueries
4. **`$lookup`** is MongoDB's JOIN — but embedding data is often preferred
5. PyMongo syntax mirrors the shell but uses Python dicts and snake_case method names
