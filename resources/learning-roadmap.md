# 12-Week MongoDB Learning Roadmap

A structured study plan using this repository. Estimated 5-8 hours per week.

---

## Week 1–2: Fundamentals + Setup

**Folders:** `01-fundamentals/`, `02-setup/`

**Objectives:**
- Understand the document model and how it differs from SQL
- Set up MongoDB Atlas (free tier) or Docker
- Run your first connection test

**Tasks:**
- [ ] Read `01-fundamentals/concepts.md` — take notes
- [ ] Study `01-fundamentals/cheatsheet.md` — bookmark this
- [ ] Follow `02-setup/atlas-setup.md` or `02-setup/docker-setup.md`
- [ ] Load sample data in Atlas (sample_mflix)
- [ ] Run `02-setup/connect-test.py` successfully
- [ ] Try 10 basic commands in mongosh or Compass

**Milestone:** You can connect to MongoDB and browse sample data.

**Estimated time:** 4-6 hours total

---

## Week 3: CRUD Operations

**Folder:** `03-crud-operations/`

**Objectives:**
- Master insert, find, update, and delete operations
- Understand query operators and projections
- Practice with the sample_mflix database

**Tasks:**
- [ ] Read `03-crud-operations/README.md`
- [ ] Run and study `crud_basics.py` — modify queries, experiment
- [ ] Run and study `crud_advanced.py` — focus on operators
- [ ] Complete all 15 exercises in `exercises.md`
- [ ] Write 5 of your own queries against sample_mflix

**Milestone:** You can write any CRUD query from memory.

**Estimated time:** 6-8 hours

---

## Week 4: Schema Design

**Folder:** `04-schema-design/`

**Objectives:**
- Understand embedding vs referencing
- Learn common design patterns
- Recognize anti-patterns

**Tasks:**
- [ ] Read `patterns.md` thoroughly
- [ ] Read `anti-patterns.md` — understand each mistake
- [ ] Run all three example scripts (blog, ecommerce, social media)
- [ ] Design a schema for your own project idea (write it out as JSON)
- [ ] Review your design against the anti-patterns checklist

**Milestone:** You can design a MongoDB schema for any application.

**Estimated time:** 5-7 hours

---

## Week 5–6: Aggregation Framework

**Folder:** `05-aggregation/`

**Objectives:**
- Master the aggregation pipeline
- Use `$group`, `$lookup`, `$unwind`, `$facet`
- Write real-world analytical queries

**Tasks:**
- [ ] Read `05-aggregation/README.md`
- [ ] Run `pipeline_basics.py` — understand each stage
- [ ] Run `pipeline_advanced.py` — focus on `$lookup` and `$facet`
- [ ] Study all 10 examples in `real_world_queries.py`
- [ ] Complete all 10 exercises in `exercises.md`
- [ ] Write 3 aggregation queries for your own data

**Milestone:** You can build complex aggregation pipelines.

**Estimated time:** 10-12 hours

---

## Week 7: Indexing & Performance

**Folder:** `06-indexing/`

**Objectives:**
- Understand index types and when to use each
- Analyze queries with `.explain()`
- Measure performance impact of indexes

**Tasks:**
- [ ] Read `indexing_guide.md` — focus on compound indexes and ESR rule
- [ ] Run `performance.py` — observe the speed differences
- [ ] Run `explain_queries.py` — learn to read explain output
- [ ] Add indexes to your own collections and verify with explain
- [ ] Identify and fix COLLSCAN queries in your sample data

**Milestone:** You can identify missing indexes and optimize query performance.

**Estimated time:** 5-7 hours

---

## Week 8: Python Integration

**Folder:** `07-python-integration/`

**Objectives:**
- Build applications with PyMongo
- Handle errors properly
- Use bulk operations and transactions

**Tasks:**
- [ ] Run `pymongo_basics.py` — study connection management and error handling
- [ ] Run `pymongo_advanced.py` — focus on bulk_write and transactions
- [ ] (Optional) Run `mongoose_basics.js` if learning MERN stack
- [ ] Build a small CLI app that uses MongoDB (e.g., a todo list or bookmark manager)

**Milestone:** You can build a production-quality Python + MongoDB application.

**Estimated time:** 6-8 hours

---

## Week 9: Build the Scraper Project

**Folder:** `08-web-scraper-project/`

**Objectives:**
- Build a complete data pipeline from scratch
- Practice everything you've learned
- Create a portfolio-worthy project

**Tasks:**
- [ ] Read the project README
- [ ] Run `scraper.py` — understand each section
- [ ] Run `analyze.py` — study the aggregation queries
- [ ] Run `scraper_advanced.py` with different flags
- [ ] Modify the scraper: add new analysis queries, scrape additional data
- [ ] Write a summary of what you learned

**Milestone:** You have a working project you can show in interviews.

**Estimated time:** 6-8 hours

---

## Week 10: AI & Vector Search

**Folder:** `09-ai-vector-search/`

**Objectives:**
- Understand embeddings and vector search
- Learn the RAG pattern
- Experiment with Atlas Vector Search

**Tasks:**
- [ ] Read `concepts.md` — understand embeddings and semantic search
- [ ] Read `vector_search_setup.md`
- [ ] Run `rag_basics.py` (with or without OpenAI key)
- [ ] (Optional) Set up Atlas Vector Search index and run real vector search
- [ ] (Optional) Run `langchain_example.py` with OpenAI key

**Milestone:** You understand how MongoDB fits into AI applications.

**Estimated time:** 5-7 hours

---

## Week 11: Production Concepts

**Folder:** `10-production/`

**Objectives:**
- Understand replication, sharding, security, and monitoring
- Know what it takes to run MongoDB in production

**Tasks:**
- [ ] Read all four production guides
- [ ] Create a production readiness checklist for a hypothetical app
- [ ] Review Atlas security settings on your free cluster
- [ ] Set up a basic Atlas alert (free tier supports email alerts)

**Milestone:** You can discuss production MongoDB architecture in interviews.

**Estimated time:** 5-6 hours

---

## Week 12: Review + Certification Prep

**Folder:** `resources/`

**Objectives:**
- Review all material
- Prepare for the MongoDB certification exam
- Fill gaps in knowledge

**Tasks:**
- [ ] Review `mongodb-vs-sql-cheatsheet.md` — quiz yourself
- [ ] Answer all 30 `interview-questions.md` without looking
- [ ] Read `certification-guide.md`
- [ ] Take practice tests on MongoDB University
- [ ] Re-run scripts from any section where you feel weak
- [ ] (Optional) Register for the MongoDB Associate Developer exam

**Milestone:** You're ready for interviews and/or the certification exam.

**Estimated time:** 8-10 hours

---

## Total Estimated Time: 70-90 hours over 12 weeks
