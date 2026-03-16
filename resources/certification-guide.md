# MongoDB Associate Developer Certification Guide

---

## What is the Certification?

The **MongoDB Associate Developer** certification validates your ability to build applications using MongoDB. It demonstrates proficiency with CRUD operations, data modeling, indexes, aggregation, and the MongoDB drivers.

---

## Exam Details

| Detail | Info |
|--------|------|
| **Exam name** | MongoDB Associate Developer |
| **Format** | Multiple choice and multiple select |
| **Questions** | ~70 questions |
| **Time** | 90 minutes |
| **Passing score** | ~65% (MongoDB doesn't publish exact cutoff) |
| **Cost** | $150 USD |
| **Languages** | Available for Python, Java, JavaScript/Node.js |
| **Proctoring** | Online, proctored |
| **Validity** | 3 years |

---

## Topics Covered

| Topic | Approximate Weight | This Repo |
|-------|-------------------|-----------|
| MongoDB Overview and Document Model | ~8% | `01-fundamentals/` |
| CRUD Operations | ~25% | `03-crud-operations/` |
| Indexes | ~15% | `06-indexing/` |
| Data Modeling | ~12% | `04-schema-design/` |
| Aggregation | ~20% | `05-aggregation/` |
| MongoDB Tools and Tooling | ~5% | `02-setup/` |
| Drivers (PyMongo / Node.js) | ~15% | `07-python-integration/` |

---

## Study Strategy

### Phase 1: Learn (Weeks 1–8)
Follow the 12-week roadmap through folders 01–07. Focus on understanding, not memorization.

### Phase 2: Practice (Weeks 9–10)
- Complete all exercises in this repo
- Build the scraper project (folder 08)
- Practice on [MongoDB University](https://learn.mongodb.com/) courses (free)

### Phase 3: Review (Weeks 11–12)
- Review the SQL→MongoDB cheatsheet
- Answer all 30 interview questions without looking
- Take practice exams on MongoDB University
- Review areas where you scored lowest

---

## Key Areas to Focus On

### CRUD (25% of exam)
- All query operators: `$gt`, `$lt`, `$in`, `$nin`, `$regex`, `$exists`
- Update operators: `$set`, `$unset`, `$inc`, `$push`, `$pull`, `$addToSet`
- Array queries: `$elemMatch`, `$all`, `$size`
- Projection, sorting, limiting, skipping
- `findOneAndUpdate`, `findOneAndDelete`
- Upsert behavior

### Aggregation (20% of exam)
- All major stages: `$match`, `$group`, `$sort`, `$project`, `$limit`, `$skip`
- `$lookup` (join syntax and behavior)
- `$unwind` (including `preserveNullAndEmptyArrays`)
- `$addFields` vs `$project`
- Accumulator operators: `$sum`, `$avg`, `$min`, `$max`, `$push`, `$addToSet`
- `$facet`, `$bucket`

### Indexes (15% of exam)
- Single field, compound, multikey, text, geospatial, TTL, unique
- Compound index field order (ESR rule)
- Covered queries
- `explain()` output interpretation
- When indexes help and when they don't

### Data Modeling (12% of exam)
- Embedding vs referencing (and when to use each)
- One-to-one, one-to-many, many-to-many patterns
- Document size limit (16 MB)
- Anti-patterns (massive arrays, over-normalization)

### Drivers (15% of exam)
- Connection string format and options
- Connection pooling
- Error handling (ConnectionFailure, DuplicateKeyError)
- Cursor behavior
- Write concern and read preference

---

## Practice Resources

1. **MongoDB University** — [learn.mongodb.com](https://learn.mongodb.com/)
   - Free courses aligned with certification topics
   - Practice exams available after completing courses
2. **MongoDB Documentation** — [docs.mongodb.com](https://www.mongodb.com/docs/)
   - The exam tests knowledge found in the official docs
3. **This Repository** — Work through all folders and exercises
4. **MongoDB Playground** — [mongoplayground.net](https://mongoplayground.net/)
   - Practice aggregation pipelines in the browser

---

## Tips for Exam Day

1. **Read questions carefully** — many questions test edge cases and subtle behaviors
2. **Eliminate wrong answers** — multiple-choice is easier with elimination
3. **Watch for "MOST correct"** — some questions have multiple partially correct answers
4. **Time management** — ~75 seconds per question, don't get stuck
5. **Know your driver** — the exam is language-specific (Python, Java, or Node.js)
6. **Aggregation pipeline order matters** — know which stages can use indexes
7. **Index questions are common** — understand compound index prefix, ESR, covered queries
8. **Schema design questions test trade-offs** — there's rarely one "right" answer

---

## How This Repo Maps to Certification

| Certification Topic | Repository Section |
|--------------------|--------------------|
| Document Model & BSON | `01-fundamentals/concepts.md` |
| CRUD Operators | `03-crud-operations/crud_advanced.py` |
| CRUD Exercises | `03-crud-operations/exercises.md` |
| Data Modeling | `04-schema-design/patterns.md`, `anti-patterns.md` |
| Aggregation Stages | `05-aggregation/pipeline_basics.py`, `pipeline_advanced.py` |
| Aggregation Exercises | `05-aggregation/exercises.md` |
| Index Types | `06-indexing/indexing_guide.md` |
| Explain Plans | `06-indexing/explain_queries.py` |
| PyMongo Driver | `07-python-integration/pymongo_basics.py` |
| SQL→MongoDB | `resources/mongodb-vs-sql-cheatsheet.md` |

---

## 📌 Key Takeaways

1. **CRUD + Aggregation = 45%** of the exam — practice these the most
2. **MongoDB University** courses are the best preparation (and free)
3. Work through all exercises in this repo before taking the exam
4. The exam tests practical knowledge — writing queries, not just theory
5. You have 3 years before needing to recertify
