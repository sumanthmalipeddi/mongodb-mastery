"""
Quote Analysis Script
=====================
Standalone analysis of scraped quotes using MongoDB aggregation pipelines.

Run scraper.py first to populate the database, then run this script.

Usage:
    python analyze.py
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_NAME = "quotes_db"
COLLECTION_NAME = "quotes"


def get_collection():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Set MONGODB_URI in .env file first!")
        sys.exit(1)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        count = collection.count_documents({})
        if count == 0:
            print("❌ No quotes found! Run scraper.py first.")
            sys.exit(1)
        print(f"✅ Connected — {count} quotes in collection\n")
        return collection
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def print_header(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def author_statistics(collection):
    """Analyze quotes by author."""
    print_header("Author Statistics")

    pipeline = [
        {"$group": {
            "_id": "$author",
            "quote_count": {"$sum": 1},
            "avg_word_count": {"$avg": "$word_count"},
            "min_word_count": {"$min": "$word_count"},
            "max_word_count": {"$max": "$word_count"},
            "all_tags": {"$push": "$tags"}
        }},
        {"$sort": {"quote_count": -1}}
    ]

    print(f"\n  {'Author':<25} {'Quotes':>6} {'Avg Words':>10} {'Range':>12}")
    print(f"  {'-'*25} {'-'*6} {'-'*10} {'-'*12}")

    for doc in collection.aggregate(pipeline):
        name = doc["_id"][:24]
        print(f"  {name:<25} {doc['quote_count']:>6} {doc['avg_word_count']:>10.1f} "
              f"{doc['min_word_count']:>5}-{doc['max_word_count']:<5}")


def tag_analysis(collection):
    """Analyze tag popularity and co-occurrence."""
    print_header("Tag Analysis")

    # Most popular tags
    print("\n  --- Most Popular Tags ---")
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    for doc in collection.aggregate(pipeline):
        bar = "█" * doc["count"]
        print(f"  {doc['_id']:>20}: {doc['count']:>3} {bar}")

    # Tag co-occurrence — which tags appear together most often?
    print("\n  --- Tag Co-occurrence (Top 10 pairs) ---")
    pipeline = [
        {"$match": {"tags.1": {"$exists": True}}},  # Only quotes with 2+ tags
        {"$unwind": "$tags"},
        {"$group": {
            "_id": "$_id",
            "tags": {"$push": "$tags"}
        }},
        # Create tag pairs using $unwind twice
        {"$unwind": "$tags"},
        {"$unwind": "$tags"},
        # We'd need a more complex pipeline for true pairs.
        # Simplified: count tag frequency in multi-tag quotes.
        {"$group": {"_id": "$tags", "co_occurrence": {"$sum": 1}}},
        {"$sort": {"co_occurrence": -1}},
        {"$limit": 10}
    ]
    for doc in collection.aggregate(pipeline):
        print(f"  {doc['_id']:>20}: appears in {doc['co_occurrence']} multi-tag quotes")

    # Tags per quote distribution
    print("\n  --- Tags Per Quote ---")
    pipeline = [
        {"$addFields": {"tag_count": {"$size": "$tags"}}},
        {"$group": {
            "_id": "$tag_count",
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    for doc in collection.aggregate(pipeline):
        bar = "▓" * doc["count"]
        print(f"  {doc['_id']} tags: {doc['count']:>3} quotes {bar}")


def text_analysis(collection):
    """Analyze quote text: length, word frequency."""
    print_header("Text Analysis")

    # Longest and shortest quotes
    print("\n  --- Longest Quotes ---")
    for doc in collection.find({}, {"text": 1, "author": 1, "word_count": 1, "_id": 0}).sort("word_count", -1).limit(3):
        print(f"  [{doc['word_count']} words] {doc['author']}")
        print(f"  \"{doc['text'][:100]}...\"\n")

    print("  --- Shortest Quotes ---")
    for doc in collection.find({}, {"text": 1, "author": 1, "word_count": 1, "_id": 0}).sort("word_count", 1).limit(3):
        print(f"  [{doc['word_count']} words] {doc['author']}")
        print(f"  \"{doc['text']}\"\n")

    # Word count statistics
    pipeline = [
        {"$group": {
            "_id": None,
            "avg_words": {"$avg": "$word_count"},
            "min_words": {"$min": "$word_count"},
            "max_words": {"$max": "$word_count"},
            "total_words": {"$sum": "$word_count"}
        }}
    ]
    stats = list(collection.aggregate(pipeline))
    if stats:
        s = stats[0]
        print(f"  --- Word Count Stats ---")
        print(f"  Average: {s['avg_words']:.1f} words per quote")
        print(f"  Range: {s['min_words']} – {s['max_words']} words")
        print(f"  Total: {s['total_words']} words across all quotes")

    # Word count distribution
    print("\n  --- Word Count Distribution ---")
    pipeline = [
        {"$bucket": {
            "groupBy": "$word_count",
            "boundaries": [0, 5, 10, 15, 20, 25, 30, 50, 100],
            "default": "50+",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    for doc in collection.aggregate(pipeline):
        bar = "█" * doc["count"]
        label = f"{doc['_id']}+" if isinstance(doc["_id"], str) else f"{doc['_id']:>2}"
        print(f"  {label} words: {doc['count']:>3} {bar}")


def text_search_demo(collection):
    """Demonstrate full-text search capabilities."""
    print_header("Full-Text Search Demos")

    search_terms = ["love", "life world", "imagination", "truth"]

    for term in search_terms:
        print(f"\n  --- Search: '{term}' ---")
        try:
            cursor = collection.find(
                {"$text": {"$search": term}},
                {"text": 1, "author": 1, "score": {"$meta": "textScore"}, "_id": 0}
            ).sort([("score", {"$meta": "textScore"})]).limit(3)

            results = list(cursor)
            if results:
                for doc in results:
                    print(f"  [{doc['score']:.1f}] {doc['author']}: \"{doc['text'][:60]}...\"")
            else:
                print(f"  No results for '{term}'")
        except Exception as e:
            print(f"  ⚠️  Text search failed: {e}")
            print(f"  Make sure a text index exists. Run scraper.py first.")
            break


def page_analysis(collection):
    """Analyze data by scrape page."""
    print_header("Page Distribution")

    pipeline = [
        {"$group": {
            "_id": "$page_number",
            "count": {"$sum": 1},
            "unique_authors": {"$addToSet": "$author"}
        }},
        {"$addFields": {"author_count": {"$size": "$unique_authors"}}},
        {"$sort": {"_id": 1}},
        {"$project": {"count": 1, "author_count": 1, "_id": 1}}
    ]

    print(f"\n  {'Page':>6} {'Quotes':>8} {'Authors':>9}")
    print(f"  {'-'*6} {'-'*8} {'-'*9}")
    for doc in collection.aggregate(pipeline):
        print(f"  {doc['_id']:>6} {doc['count']:>8} {doc['author_count']:>9}")


def main():
    collection = get_collection()

    author_statistics(collection)
    tag_analysis(collection)
    text_analysis(collection)
    text_search_demo(collection)
    page_analysis(collection)

    print_header("Analysis Complete!")
    print(f"\n  Analyzed {collection.count_documents({})} quotes")
    print(f"  From {len(collection.distinct('author'))} unique authors")
    print(f"  With {len(collection.distinct('tags'))} unique tags\n")


if __name__ == "__main__":
    main()
