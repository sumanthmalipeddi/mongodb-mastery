"""
Index Performance Benchmark
============================
Demonstrates the dramatic performance difference between queries
with and without indexes.

Creates a test collection with 100K documents, then compares query times.

Usage:
    python performance.py
"""

import os
import sys
import time
import random
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

load_dotenv()

COLLECTION_NAME = "perf_test"
NUM_DOCUMENTS = 100_000


def get_database():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Set MONGODB_URI in your .env file first!")
        sys.exit(1)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("✅ Connected to MongoDB!\n")
        return client["learning_db"]
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def generate_documents(n):
    """Generate n random user documents."""
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
              "Philadelphia", "San Antonio", "San Diego", "Dallas", "Portland"]
    statuses = ["active", "inactive", "pending"]
    departments = ["engineering", "marketing", "sales", "support", "hr"]

    docs = []
    for i in range(n):
        docs.append({
            "user_id": i,
            "name": f"User_{i}",
            "age": random.randint(18, 70),
            "city": random.choice(cities),
            "status": random.choice(statuses),
            "department": random.choice(departments),
            "salary": random.randint(30000, 150000),
            "score": round(random.uniform(0, 100), 2)
        })
    return docs


def time_query(collection, filter_doc, description, projection=None, sort=None):
    """Time a query execution and return duration in ms."""
    start = time.perf_counter()
    cursor = collection.find(filter_doc, projection)
    if sort:
        cursor = cursor.sort(sort)
    results = list(cursor)  # Force execution
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed, len(results)


def main():
    db = get_database()
    collection = db[COLLECTION_NAME]

    # --- Setup: Insert test data ---
    print(f"Setting up: inserting {NUM_DOCUMENTS:,} documents...")
    collection.drop()

    # Insert in batches for speed
    docs = generate_documents(NUM_DOCUMENTS)
    batch_size = 10000
    for i in range(0, len(docs), batch_size):
        collection.insert_many(docs[i:i + batch_size])
    print(f"Inserted {NUM_DOCUMENTS:,} documents.\n")

    # Drop all non-_id indexes to start fresh
    collection.drop_indexes()

    # =========================================================================
    # Test 1: Single Field Query
    # =========================================================================
    print("=" * 60)
    print("Test 1: Single Field Query — find({city: 'Portland'})")
    print("=" * 60)

    # Without index
    ms_no_idx, count = time_query(collection, {"city": "Portland"}, "no index")
    print(f"  Without index: {ms_no_idx:.1f} ms ({count:,} results)")

    # Create index
    collection.create_index("city")
    print("  Created index on 'city'")

    # With index
    ms_idx, count = time_query(collection, {"city": "Portland"}, "with index")
    print(f"  With index:    {ms_idx:.1f} ms ({count:,} results)")
    if ms_no_idx > 0 and ms_idx > 0:
        speedup = ms_no_idx / ms_idx if ms_idx > 0 else float('inf')
        print(f"  Speedup:       {speedup:.1f}x faster")

    collection.drop_indexes()

    # =========================================================================
    # Test 2: Range Query
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Test 2: Range Query — find({salary: {$gte: 100000}})")
    print("=" * 60)

    ms_no_idx, count = time_query(collection, {"salary": {"$gte": 100000}}, "no index")
    print(f"  Without index: {ms_no_idx:.1f} ms ({count:,} results)")

    collection.create_index("salary")
    print("  Created index on 'salary'")

    ms_idx, count = time_query(collection, {"salary": {"$gte": 100000}}, "with index")
    print(f"  With index:    {ms_idx:.1f} ms ({count:,} results)")
    if ms_no_idx > 0 and ms_idx > 0:
        speedup = ms_no_idx / ms_idx if ms_idx > 0 else float('inf')
        print(f"  Speedup:       {speedup:.1f}x faster")

    collection.drop_indexes()

    # =========================================================================
    # Test 3: Compound Query
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Test 3: Compound Query — find({status: 'active', city: 'Portland'})")
    print("=" * 60)

    query = {"status": "active", "city": "Portland"}

    ms_no_idx, count = time_query(collection, query, "no index")
    print(f"  Without index:        {ms_no_idx:.1f} ms ({count:,} results)")

    # Single field index
    collection.create_index("status")
    ms_single, count = time_query(collection, query, "single index")
    print(f"  Single index (status): {ms_single:.1f} ms ({count:,} results)")
    collection.drop_indexes()

    # Compound index
    collection.create_index([("status", 1), ("city", 1)])
    ms_compound, count = time_query(collection, query, "compound index")
    print(f"  Compound index:       {ms_compound:.1f} ms ({count:,} results)")
    if ms_no_idx > 0 and ms_compound > 0:
        speedup = ms_no_idx / ms_compound if ms_compound > 0 else float('inf')
        print(f"  Speedup:              {speedup:.1f}x faster")

    collection.drop_indexes()

    # =========================================================================
    # Test 4: Sort Performance
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Test 4: Sort — find({status: 'active'}).sort('salary', -1).limit(10)")
    print("=" * 60)

    query = {"status": "active"}
    sort_spec = [("salary", -1)]

    ms_no_idx, count = time_query(collection, query, "no index", sort=sort_spec)
    print(f"  Without index: {ms_no_idx:.1f} ms")

    # Index that supports both filter and sort
    collection.create_index([("status", 1), ("salary", -1)])
    ms_idx, count = time_query(collection, query, "with index", sort=sort_spec)
    print(f"  With index:    {ms_idx:.1f} ms")
    if ms_no_idx > 0 and ms_idx > 0:
        speedup = ms_no_idx / ms_idx if ms_idx > 0 else float('inf')
        print(f"  Speedup:       {speedup:.1f}x faster")

    collection.drop_indexes()

    # =========================================================================
    # Test 5: Text Search
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Test 5: Text Index — Full-text search on 'name'")
    print("=" * 60)

    # Regex without text index
    start = time.perf_counter()
    results = list(collection.find({"name": {"$regex": "User_999"}}))
    ms_regex = (time.perf_counter() - start) * 1000
    print(f"  Regex search:  {ms_regex:.1f} ms ({len(results)} results)")

    # Text index
    collection.create_index([("name", "text")])
    start = time.perf_counter()
    results = list(collection.find({"$text": {"$search": "User_999"}}))
    ms_text = (time.perf_counter() - start) * 1000
    print(f"  Text search:   {ms_text:.1f} ms ({len(results)} results)")

    # =========================================================================
    # Summary
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Summary")
    print("=" * 60)
    print(f"  Collection size: {NUM_DOCUMENTS:,} documents")
    print()
    print("  📌 Indexes dramatically speed up reads")
    print("  📌 Compound indexes outperform single-field indexes for multi-condition queries")
    print("  📌 The right index can make a query 10-100x faster")
    print("  📌 Use .explain() to verify — see explain_queries.py")

    # Cleanup
    print(f"\n  Keeping '{COLLECTION_NAME}' collection for explain_queries.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
