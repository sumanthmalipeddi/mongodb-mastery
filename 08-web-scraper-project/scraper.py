"""
Web Scraper + MongoDB Project
==============================
A complete data pipeline that demonstrates web scraping, MongoDB storage,
indexing, and querying.

What this script does:
    1. Connects to MongoDB Atlas (or local Docker)
    2. Scrapes ALL pages from http://quotes.toscrape.com (~100 quotes, 10 pages)
    3. Parses each quote: text, author, tags
    4. Stores structured documents in MongoDB
    5. Creates indexes (single field, array, full-text)
    6. Runs 10 demo queries showcasing different MongoDB features

Data source: http://quotes.toscrape.com (sandbox site for scraping practice)

Usage:
    pip install -r requirements.txt
    python scraper.py
"""

import os
import sys
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import ConnectionFailure, BulkWriteError

# Load .env from project root or current directory
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

BASE_URL = "http://quotes.toscrape.com"
DB_NAME = "quotes_db"
COLLECTION_NAME = "quotes"


# =========================================================================
# Step 1: Connect to MongoDB
# =========================================================================

def connect_to_mongodb():
    """Connect to MongoDB and return the collection."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ MONGODB_URI not found in .env file!")
        print("   Create a .env file with: MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/")
        sys.exit(1)

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("✅ Connected to MongoDB!")
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        return client, collection
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("   Check your connection string and network access settings.")
        sys.exit(1)


# =========================================================================
# Step 2: Scrape quotes from all pages
# =========================================================================

def scrape_all_quotes():
    """Scrape all quotes from quotes.toscrape.com, following pagination."""
    all_quotes = []
    page_number = 1
    url = f"{BASE_URL}/page/1/"

    print(f"\n📥 Scraping quotes from {BASE_URL}...")

    while url:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"   ⚠️  Failed to fetch {url}: {e}")
            break

        soup = BeautifulSoup(response.text, "lxml")

        # Parse each quote on the page
        quote_divs = soup.find_all("div", class_="quote")
        page_count = 0

        for quote_div in quote_divs:
            # Extract text (remove surrounding quotes)
            text = quote_div.find("span", class_="text").get_text()
            # Remove the Unicode curly quotes
            text = text.strip("\u201c\u201d")

            # Extract author
            author = quote_div.find("small", class_="author").get_text()

            # Extract tags
            tags = [tag.get_text() for tag in quote_div.find_all("a", class_="tag")]

            # Build the document
            quote_doc = {
                "text": text,
                "author": author,
                "tags": tags,
                "page_number": page_number,
                "source_url": url,
                "scraped_at": datetime.now(timezone.utc),
                "word_count": len(text.split())
            }
            all_quotes.append(quote_doc)
            page_count += 1

        print(f"   Page {page_number}: {page_count} quotes scraped")

        # Check for next page
        next_button = soup.find("li", class_="next")
        if next_button:
            next_link = next_button.find("a")["href"]
            url = BASE_URL + next_link
            page_number += 1
            time.sleep(0.5)  # Be polite — don't hammer the server
        else:
            url = None  # No more pages

    print(f"\n   Total quotes scraped: {len(all_quotes)}")
    return all_quotes


# =========================================================================
# Step 3: Store in MongoDB
# =========================================================================

def store_quotes(collection, quotes):
    """Insert all quotes into MongoDB."""
    print(f"\n💾 Storing {len(quotes)} quotes in MongoDB...")

    # Drop existing data for a clean run
    collection.drop()

    try:
        result = collection.insert_many(quotes)
        print(f"   Inserted {len(result.inserted_ids)} documents")
    except BulkWriteError as e:
        print(f"   ⚠️  Bulk write error: {e.details}")


# =========================================================================
# Step 4: Create indexes
# =========================================================================

def create_indexes(collection):
    """Create indexes for fast queries and full-text search."""
    print("\n🔑 Creating indexes...")

    # Single field index on author (for filtering by author)
    collection.create_index("author")
    print("   Created index: author")

    # Multikey index on tags (each tag gets an index entry)
    collection.create_index("tags")
    print("   Created index: tags")

    # Full-text index on text field (for $text search)
    collection.create_index([("text", TEXT)])
    print("   Created text index: text")

    # Compound index for page_number + author
    collection.create_index([("page_number", ASCENDING), ("author", ASCENDING)])
    print("   Created compound index: page_number + author")

    print(f"   Total indexes: {len(collection.index_information())}")


# =========================================================================
# Step 5: Run 10 demo queries
# =========================================================================

def run_demo_queries(collection):
    """Run 10 queries demonstrating different MongoDB features."""

    print("\n" + "=" * 60)
    print("DEMO QUERIES")
    print("=" * 60)

    # --- Query 1: findOne ---
    print("\n=== Query 1: find_one — Get a single quote ===")
    quote = collection.find_one()
    print(f"   \"{quote['text'][:80]}...\"")
    print(f"   — {quote['author']}")

    # --- Query 2: find with filter ---
    print("\n=== Query 2: find — All quotes by Albert Einstein ===")
    cursor = collection.find({"author": "Albert Einstein"})
    einstein_quotes = list(cursor)
    print(f"   Found {len(einstein_quotes)} quotes:")
    for q in einstein_quotes:
        print(f"   • \"{q['text'][:70]}...\"")

    # --- Query 3: find with projection ---
    print("\n=== Query 3: find with projection — Authors and word counts only ===")
    cursor = collection.find(
        {},
        {"author": 1, "word_count": 1, "_id": 0}
    ).limit(5)
    for q in cursor:
        print(f"   {q['author']}: {q['word_count']} words")

    # --- Query 4: countDocuments ---
    print("\n=== Query 4: countDocuments — Stats ===")
    total = collection.count_documents({})
    tagged_inspirational = collection.count_documents({"tags": "inspirational"})
    long_quotes = collection.count_documents({"word_count": {"$gte": 15}})
    print(f"   Total quotes: {total}")
    print(f"   Tagged 'inspirational': {tagged_inspirational}")
    print(f"   Long quotes (15+ words): {long_quotes}")

    # --- Query 5: Full-text search ---
    print("\n=== Query 5: Full-text search — Quotes about 'world' ===")
    cursor = collection.find(
        {"$text": {"$search": "world"}},
        {"text": 1, "author": 1, "score": {"$meta": "textScore"}, "_id": 0}
    ).sort([("score", {"$meta": "textScore"})]).limit(5)
    for q in cursor:
        print(f"   [{q['score']:.1f}] \"{q['text'][:60]}...\" — {q['author']}")

    # --- Query 6: sort + limit ---
    print("\n=== Query 6: sort + limit — Longest quotes ===")
    cursor = collection.find(
        {},
        {"text": 1, "author": 1, "word_count": 1, "_id": 0}
    ).sort("word_count", -1).limit(5)
    for q in cursor:
        print(f"   {q['word_count']} words — {q['author']}: \"{q['text'][:50]}...\"")

    # --- Query 7: update_many ---
    print("\n=== Query 7: update_many — Add 'classic' flag to Einstein quotes ===")
    result = collection.update_many(
        {"author": "Albert Einstein"},
        {"$set": {"classic": True, "updated_at": datetime.now(timezone.utc)}}
    )
    print(f"   Matched: {result.matched_count}, Modified: {result.modified_count}")

    # Verify
    classic_count = collection.count_documents({"classic": True})
    print(f"   Quotes marked as classic: {classic_count}")

    # --- Query 8: aggregate — Top authors by quote count ---
    print("\n=== Query 8: Aggregation — Top 5 authors by quote count ===")
    pipeline = [
        {"$group": {
            "_id": "$author",
            "quote_count": {"$sum": 1},
            "avg_word_count": {"$avg": "$word_count"}
        }},
        {"$sort": {"quote_count": -1}},
        {"$limit": 5}
    ]
    for result in collection.aggregate(pipeline):
        print(f"   {result['_id']}: {result['quote_count']} quotes "
              f"(avg {result['avg_word_count']:.0f} words)")

    # --- Query 9: aggregate — Most popular tags ($unwind) ---
    print("\n=== Query 9: Aggregation — Top 10 most popular tags ===")
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    for result in collection.aggregate(pipeline):
        bar = "█" * result["count"]
        print(f"   {result['_id']:>20}: {result['count']:>2} {bar}")

    # --- Query 10: Complex query combining multiple conditions ---
    print("\n=== Query 10: Complex query — Inspirational quotes, 10+ words, sorted ===")
    cursor = collection.find(
        {
            "tags": "inspirational",
            "word_count": {"$gte": 10},
            "author": {"$ne": "Albert Einstein"}  # Exclude Einstein
        },
        {"text": 1, "author": 1, "word_count": 1, "tags": 1, "_id": 0}
    ).sort("word_count", -1).limit(5)

    for q in cursor:
        print(f"   [{q['word_count']} words] {q['author']}")
        print(f"   \"{q['text'][:70]}...\"")
        print(f"   Tags: {', '.join(q['tags'])}\n")


# =========================================================================
# Main
# =========================================================================

def main():
    print("=" * 60)
    print("Web Scraper + MongoDB Project")
    print("=" * 60)

    # Step 1: Connect
    client, collection = connect_to_mongodb()

    # Step 2: Scrape
    quotes = scrape_all_quotes()

    if not quotes:
        print("❌ No quotes scraped. Check your internet connection.")
        client.close()
        sys.exit(1)

    # Step 3: Store
    store_quotes(collection, quotes)

    # Step 4: Index
    create_indexes(collection)

    # Step 5: Query
    run_demo_queries(collection)

    # Done
    print("\n" + "=" * 60)
    print("✅ Project complete!")
    print(f"   Database: {DB_NAME}")
    print(f"   Collection: {COLLECTION_NAME}")
    print(f"   Documents: {collection.count_documents({})}")
    print("   Run 'python analyze.py' for more analysis.")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
