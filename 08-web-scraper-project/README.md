# 08 — Web Scraper Project

> **Goal:** Build a complete data pipeline — scrape, store, index, and analyze data with MongoDB.

---

## What You'll Build

A web scraper that:
1. Scrapes all 100 quotes from [quotes.toscrape.com](http://quotes.toscrape.com) (10 pages)
2. Stores structured data in MongoDB with proper schema
3. Creates indexes for fast queries and full-text search
4. Runs 10 different MongoDB query demonstrations
5. Analyzes the data with aggregation pipelines

---

## Document Schema

```json
{
  "text": "The world as we have created it is a process of our thinking...",
  "author": "Albert Einstein",
  "tags": ["change", "deep-thoughts", "thinking", "world"],
  "page_number": 1,
  "source_url": "http://quotes.toscrape.com/page/1/",
  "scraped_at": ISODate("2025-01-15T10:30:00Z"),
  "word_count": 16
}
```

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your .env file
cp ../.env.example ../.env
# Edit ../.env with your MongoDB connection string

# 3. Run the scraper (scrapes + stores + queries)
python scraper.py

# 4. Run the advanced scraper (with logging, rate limiting, retries)
python scraper_advanced.py

# 5. Run standalone analysis on the scraped data
python analyze.py
```

---

## 📂 Files

| File | Description |
|------|-------------|
| [requirements.txt](requirements.txt) | Python dependencies |
| [scraper.py](scraper.py) | Main scraper: scrape → store → index → query |
| [scraper_advanced.py](scraper_advanced.py) | Enhanced: logging, retries, rate limiting, deduplication |
| [analyze.py](analyze.py) | Standalone analysis: aggregations, text search, stats |

---

## 📌 Key Takeaways

1. **Schema design matters** — structure your scraped data for the queries you'll run
2. **Indexes** enable fast text search and field queries
3. **Aggregation pipelines** turn raw data into insights
4. Always add **rate limiting** and **error handling** in production scrapers
5. **`scraped_at` timestamps** let you track when data was collected

---

Credit: [quotes.toscrape.com](http://quotes.toscrape.com) is a sandbox site designed for scraping practice.
