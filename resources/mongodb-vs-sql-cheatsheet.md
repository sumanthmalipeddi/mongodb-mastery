# MongoDB vs SQL — Complete Cheatsheet

---

## SELECT → find

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `SELECT * FROM users` | `db.users.find()` | `db.users.find()` |
| `SELECT name, email FROM users` | `db.users.find({}, {name:1, email:1, _id:0})` | `db.users.find({}, {"name":1, "email":1, "_id":0})` |
| `SELECT * FROM users WHERE age = 25` | `db.users.find({age: 25})` | `db.users.find({"age": 25})` |
| `SELECT * FROM users WHERE age != 25` | `db.users.find({age: {$ne: 25}})` | `db.users.find({"age": {"$ne": 25}})` |
| `SELECT * FROM users WHERE age > 25` | `db.users.find({age: {$gt: 25}})` | `db.users.find({"age": {"$gt": 25}})` |
| `SELECT * FROM users WHERE age >= 25` | `db.users.find({age: {$gte: 25}})` | `db.users.find({"age": {"$gte": 25}})` |
| `SELECT * FROM users WHERE age < 25` | `db.users.find({age: {$lt: 25}})` | `db.users.find({"age": {"$lt": 25}})` |
| `SELECT * FROM users WHERE age <= 25` | `db.users.find({age: {$lte: 25}})` | `db.users.find({"age": {"$lte": 25}})` |
| `SELECT * FROM users WHERE name LIKE '%alice%'` | `db.users.find({name: /alice/i})` | `db.users.find({"name": {"$regex": "alice", "$options": "i"}})` |
| `SELECT * FROM users WHERE name LIKE 'A%'` | `db.users.find({name: /^A/})` | `db.users.find({"name": {"$regex": "^A"}})` |
| `SELECT * FROM users WHERE age IN (25, 30, 35)` | `db.users.find({age: {$in: [25,30,35]}})` | `db.users.find({"age": {"$in": [25,30,35]}})` |
| `SELECT * FROM users WHERE age NOT IN (25, 30)` | `db.users.find({age: {$nin: [25,30]}})` | `db.users.find({"age": {"$nin": [25,30]}})` |
| `SELECT * FROM users WHERE age BETWEEN 20 AND 30` | `db.users.find({age: {$gte:20, $lte:30}})` | `db.users.find({"age": {"$gte":20, "$lte":30}})` |
| `SELECT * FROM users WHERE email IS NULL` | `db.users.find({email: null})` | `db.users.find({"email": None})` |
| `SELECT * FROM users WHERE email IS NOT NULL` | `db.users.find({email: {$ne: null}})` | `db.users.find({"email": {"$ne": None}})` |

---

## WHERE — AND / OR / NOT

| SQL | MongoDB Shell |
|-----|--------------|
| `WHERE a = 1 AND b = 2` | `{a: 1, b: 2}` |
| `WHERE a = 1 OR b = 2` | `{$or: [{a: 1}, {b: 2}]}` |
| `WHERE NOT (a > 5)` | `{a: {$not: {$gt: 5}}}` |
| `WHERE a = 1 AND (b = 2 OR c = 3)` | `{a: 1, $or: [{b: 2}, {c: 3}]}` |

---

## INSERT → insertOne / insertMany

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `INSERT INTO users (name, age) VALUES ('Alice', 25)` | `db.users.insertOne({name:"Alice", age:25})` | `db.users.insert_one({"name":"Alice", "age":25})` |
| `INSERT INTO users VALUES ('Bob',30),('Carol',28)` | `db.users.insertMany([{name:"Bob",age:30},{name:"Carol",age:28}])` | `db.users.insert_many([{"name":"Bob","age":30},{"name":"Carol","age":28}])` |

---

## UPDATE → updateOne / updateMany

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `UPDATE users SET age=26 WHERE name='Alice'` | `db.users.updateOne({name:"Alice"},{$set:{age:26}})` | `db.users.update_one({"name":"Alice"},{"$set":{"age":26}})` |
| `UPDATE users SET age=age+1` | `db.users.updateMany({},{$inc:{age:1}})` | `db.users.update_many({},{"$inc":{"age":1}})` |
| `UPDATE users SET status='active' WHERE age>18` | `db.users.updateMany({age:{$gt:18}},{$set:{status:"active"}})` | `db.users.update_many({"age":{"$gt":18}},{"$set":{"status":"active"}})` |

---

## DELETE → deleteOne / deleteMany

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `DELETE FROM users WHERE name='Alice'` | `db.users.deleteOne({name:"Alice"})` | `db.users.delete_one({"name":"Alice"})` |
| `DELETE FROM users WHERE age<18` | `db.users.deleteMany({age:{$lt:18}})` | `db.users.delete_many({"age":{"$lt":18}})` |
| `DELETE FROM users` | `db.users.deleteMany({})` | `db.users.delete_many({})` |
| `DROP TABLE users` | `db.users.drop()` | `db.users.drop()` |
| `TRUNCATE TABLE users` | `db.users.deleteMany({})` | `db.users.delete_many({})` |

---

## ORDER BY → sort

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `ORDER BY age ASC` | `.sort({age: 1})` | `.sort("age", 1)` |
| `ORDER BY age DESC` | `.sort({age: -1})` | `.sort("age", -1)` |
| `ORDER BY name ASC, age DESC` | `.sort({name:1, age:-1})` | `.sort([("name",1),("age",-1)])` |

---

## LIMIT / OFFSET → limit / skip

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `LIMIT 10` | `.limit(10)` | `.limit(10)` |
| `LIMIT 10 OFFSET 20` | `.skip(20).limit(10)` | `.skip(20).limit(10)` |

---

## COUNT / DISTINCT

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `SELECT COUNT(*) FROM users` | `db.users.countDocuments()` | `db.users.count_documents({})` |
| `SELECT COUNT(*) FROM users WHERE age>25` | `db.users.countDocuments({age:{$gt:25}})` | `db.users.count_documents({"age":{"$gt":25}})` |
| `SELECT DISTINCT name FROM users` | `db.users.distinct("name")` | `db.users.distinct("name")` |
| `SELECT DISTINCT name FROM users WHERE age>25` | `db.users.distinct("name",{age:{$gt:25}})` | `db.users.distinct("name",{"age":{"$gt":25}})` |

---

## JOIN → $lookup

**SQL:**
```sql
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u._id = o.user_id
WHERE o.total > 100
```

**MongoDB:**
```javascript
db.users.aggregate([
  { $lookup: { from: "orders", localField: "_id", foreignField: "user_id", as: "orders" } },
  { $unwind: "$orders" },
  { $match: { "orders.total": { $gt: 100 } } },
  { $project: { name: 1, "orders.total": 1 } }
])
```

---

## GROUP BY → $group

**SQL:**
```sql
SELECT department, COUNT(*) as count, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING count > 5
ORDER BY avg_salary DESC
```

**MongoDB:**
```javascript
db.employees.aggregate([
  { $group: { _id: "$department", count: { $sum: 1 }, avg_salary: { $avg: "$salary" } } },
  { $match: { count: { $gt: 5 } } },
  { $sort: { avg_salary: -1 } }
])
```

---

## CREATE TABLE → (implicit)

| SQL | MongoDB |
|-----|---------|
| `CREATE TABLE users (...)` | Collections are created on first insert |
| `ALTER TABLE users ADD column` | Just insert documents with the new field |
| `ALTER TABLE users DROP column` | `db.users.updateMany({}, {$unset: {column: ""}})` |

---

## CREATE INDEX → createIndex

| SQL | MongoDB Shell | PyMongo |
|-----|--------------|---------|
| `CREATE INDEX idx ON users(email)` | `db.users.createIndex({email:1})` | `db.users.create_index("email")` |
| `CREATE UNIQUE INDEX ON users(email)` | `db.users.createIndex({email:1},{unique:true})` | `db.users.create_index("email", unique=True)` |
| `CREATE INDEX ON users(name, age)` | `db.users.createIndex({name:1, age:-1})` | `db.users.create_index([("name",1),("age",-1)])` |
| `DROP INDEX idx ON users` | `db.users.dropIndex("email_1")` | `db.users.drop_index("email_1")` |

---

## Subqueries → Aggregation Pipeline

**SQL:**
```sql
SELECT * FROM users
WHERE age > (SELECT AVG(age) FROM users)
```

**MongoDB:**
```javascript
// Two-step approach:
const avgAge = db.users.aggregate([
  { $group: { _id: null, avg: { $avg: "$age" } } }
]).next().avg;

db.users.find({ age: { $gt: avgAge } });
```

---

## Aggregation Accumulators

| SQL | MongoDB `$group` Accumulator |
|-----|------------------------------|
| `COUNT(*)` | `{ $sum: 1 }` |
| `SUM(amount)` | `{ $sum: "$amount" }` |
| `AVG(price)` | `{ $avg: "$price" }` |
| `MIN(age)` | `{ $min: "$age" }` |
| `MAX(age)` | `{ $max: "$age" }` |
| `GROUP_CONCAT(name)` | `{ $push: "$name" }` |
| — | `{ $addToSet: "$tag" }` (unique values) |
| `FIRST(name)` | `{ $first: "$name" }` |
| `LAST(name)` | `{ $last: "$name" }` |
