# MongoDB Mastery — From Zero to Production

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

> **This repo will save you 60+ hours of scattered learning.** Everything you need to master MongoDB is right here — structured, hands-on, and in the right order. No courses to buy. No 40-hour YouTube playlists. Just this repo + the official MongoDB docs.

---

## 👋 New Here? Start Here!

**MongoDB** is a NoSQL database that stores data as flexible JSON-like documents instead of rigid tables and rows. It's used by companies like Google, eBay, and Adobe — and it's one of the most in-demand database skills in the industry.

This repo is a **self-paced MongoDB course** organized into numbered folders (`01` through `10`). Each folder teaches one topic with:
- A **README.md** explaining the concept in plain English
- **Python scripts** you can run to see MongoDB in action
- **Exercises** to practice what you learned

Think of it like a textbook where every chapter has working code you can run and experiment with.

### What will you learn?

By the end of this project, you will be able to:
- Understand how MongoDB stores data (documents, not tables!)
- Perform all database operations: Create, Read, Update, Delete
- Design schemas that actually make sense for real apps
- Write powerful queries using the Aggregation Framework
- Optimize performance with indexes
- Build a real project (web scraper) that stores data in MongoDB
- Use MongoDB with AI tools like LangChain for vector search
- Understand production concepts like replication and sharding

### How to use this repo

1. **Set up your environment first** (see Quick Start below)
2. **Follow the folders in order** — `01` → `02` → `03` → and so on
3. **Read the README.md first** in each folder — it explains the "why" before the "how"
4. **Run the Python scripts** — every `.py` file is standalone, just run `python filename.py`
5. **Try the exercises** — each section has practice problems with solutions included
6. **Build the scraper project** (folder `08`) — this ties everything together into a real app

---

## 📋 What's Inside

| # | Section | What you'll learn | Hours |
|---|---------|-------------------|-------|
| 01 | [Fundamentals](01-fundamentals/) | Document model, BSON, MongoDB vs SQL | 3–4 |
| 02 | [Setup](02-setup/) | Atlas free tier & Docker Compose setup | 1–2 |
| 03 | [CRUD Operations](03-crud-operations/) | Insert, find, update, delete + advanced operators | 4–5 |
| 04 | [Schema Design](04-schema-design/) | Embedding vs referencing, patterns & anti-patterns | 3–4 |
| 05 | [Aggregation](05-aggregation/) | Pipeline framework, $lookup, $facet, real-world queries | 6–8 |
| 06 | [Indexing](06-indexing/) | Index types, performance tuning, explain plans | 3–4 |
| 07 | [Python Integration](07-python-integration/) | PyMongo deep dive + Mongoose basics | 4–5 |
| 08 | [Web Scraper Project](08-web-scraper-project/) | Full project: scrape → store → analyze with MongoDB | 5–6 |
| 09 | [AI & Vector Search](09-ai-vector-search/) | Embeddings, RAG pipelines, LangChain integration | 4–5 |
| 10 | [Production](10-production/) | Replication, sharding, security, monitoring | 3–4 |
| — | [Resources](resources/) | Roadmap, cheatsheets, interview prep, certification | 4–5 |
| | | **Total** | **~40–52** |

> Self-paced — go faster or slower based on your experience. Complete beginners should expect closer to 52 hours. If you already know SQL, you can move through the early sections faster.

---

## 📦 What You Need Before Starting

| Requirement | Why | How to get it |
|------------|-----|---------------|
| **Python 3.10+** | All code examples use Python | [python.org/downloads](https://www.python.org/downloads/) |
| **pip** | Installs Python packages | Comes with Python |
| **A text editor** | To read and edit code | [VS Code](https://code.visualstudio.com/) recommended |
| **MongoDB** | The database we're learning! | See Quick Start below — choose Atlas (cloud) or Docker (local) |
| **Node.js 18+** | Only needed for one file | [nodejs.org](https://nodejs.org/) (only for `07-python-integration/mongoose_basics.js`) |

> **No MongoDB experience needed!** Folder `01` starts from absolute zero. Basic Python knowledge (variables, loops, functions) is enough.

### Verify your setup

```bash
python --version    # Should show Python 3.10 or higher
pip --version       # Should show pip is installed
docker --version    # Only if using Docker option
```

> **Tip:** If you have multiple Python versions, use `python3` instead of `python` in all commands.

---

## 🚀 Quick Start

### Step 1: Get the repo

```bash
# If using the template
# Click "Use this template" on GitHub, then clone your copy

# Or clone directly
git clone https://github.com/sumanthmalipeddi/mongodb-mastery.git
cd mongodb-mastery
```

### Step 2: Install Python packages

```bash
pip install -r requirements.txt
```

### Step 3: Set up MongoDB (pick one)

**Option A: MongoDB Atlas (Cloud — free, recommended for beginners)**

1. Create a free account at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Deploy a free M0 cluster
3. Create a database user and whitelist your IP (see [02-setup/atlas-setup.md](02-setup/atlas-setup.md) for detailed steps)
4. Copy your connection string

```bash
cp .env.example .env
# Open .env and paste your Atlas connection string
```

**Option B: Docker (Local — if you prefer running locally)**

```bash
cp .env.example .env
# Edit .env with your preferred credentials, then:
cd 02-setup && docker compose up -d
```

This starts MongoDB on `localhost:27017` and Mongo Express GUI on `localhost:8081`.

### Step 4: Test your connection

```bash
python 02-setup/connect-test.py
```

If you see a success message, you're ready! Head to [01-fundamentals/](01-fundamentals/) and start learning.

---

## 🗺️ Learning Roadmap (12 Weeks)

A suggested schedule if you're studying part-time (~4–5 hours/week):

```
Week 1–2   →  01-fundamentals/ + 02-setup/       (Concepts + Environment)
Week 3     →  03-crud-operations/                 (Core operations)
Week 4     →  04-schema-design/                   (Data modeling)
Week 5–6   →  05-aggregation/                     (Analytics & pipelines)
Week 7     →  06-indexing/                         (Performance)
Week 8     →  07-python-integration/               (Application development)
Week 9     →  08-web-scraper-project/              (Build a real project)
Week 10    →  09-ai-vector-search/                 (AI/ML integration)
Week 11    →  10-production/                       (Deploy & operate)
Week 12    →  resources/                           (Review + certification prep)
```

> Full-time learner? You can finish in 2–3 weeks. See [resources/learning-roadmap.md](resources/learning-roadmap.md) for the detailed week-by-week plan with daily goals.

---

## 🛠️ Featured Project: Web Scraper + MongoDB Analytics

The flagship project in [08-web-scraper-project/](08-web-scraper-project/) ties everything together into a real data pipeline:

1. **Scrape** all 100 quotes from [quotes.toscrape.com](http://quotes.toscrape.com) across 10 pages
2. **Store** structured data in MongoDB with proper schema
3. **Index** fields for fast queries and full-text search
4. **Analyze** data with 10 different MongoDB query patterns
5. **Advanced version** adds pagination handling, rate limiting, and logging

This is the project you'll want to show in your portfolio. It demonstrates CRUD, indexing, aggregation, and text search — all in one script.

> Credit: [quotes.toscrape.com](http://quotes.toscrape.com) is a sandbox site built for scraping practice.

---

## 📚 Official References — The Only Other Resource You Need

This repo teaches you MongoDB hands-on. When you want to go deeper on any topic, these official docs are the gold standard:

| Resource | What it covers | When to use it |
|----------|---------------|----------------|
| [MongoDB Manual](https://www.mongodb.com/docs/manual/) | Complete reference for every feature, operator, and command | Look up specific syntax or behavior |
| [PyMongo Docs](https://pymongo.readthedocs.io/en/stable/) | Python driver API reference | When writing Python + MongoDB code |
| [MongoDB University](https://learn.mongodb.com/) | Free official courses with certificates | After finishing this repo, for certification prep |
| [Aggregation Pipeline Reference](https://www.mongodb.com/docs/manual/reference/operator/aggregation-pipeline/) | Every pipeline stage and expression operator | While working through folder `05` |
| [Atlas Documentation](https://www.mongodb.com/docs/atlas/) | Cloud setup, vector search, monitoring, backups | For folders `02`, `09`, and `10` |
| [MongoDB Blog](https://www.mongodb.com/blog) | Best practices, new features, case studies | To stay current after you finish learning |

> **That's it.** This repo + official docs. No need to buy courses, watch 40-hour playlists, or hop between tutorials. Focus beats volume.

---

## 🤝 Contributing

Contributions are welcome! If you find errors, want to add exercises, or improve explanations:

1. Fork this repository
2. Create a feature branch (`git checkout -b improve-aggregation-notes`)
3. Commit your changes (`git commit -m 'Add $graphLookup examples'`)
4. Push to the branch (`git push origin improve-aggregation-notes`)
5. Open a Pull Request

Please keep the beginner-friendly tone and add comments to all code.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**Happy learning!** Start with [01-fundamentals/](01-fundamentals/) and work your way through. Every folder builds on the last.
