"""
Understanding Query Explain Plans
===================================
Learn to use .explain() to analyze how MongoDB executes queries.

Uses the sample_mflix.movies collection.

Usage:
    python explain_queries.py
"""

import os
import sys
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()


def get_database():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Set MONGODB_URI in your .env file first!")
        sys.exit(1)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("✅ Connected to MongoDB!\n")
        return client["sample_mflix"]
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def print_explain_summary(explain_result):
    """Extract and print key metrics from an explain result."""

    # Navigate the explain output structure
    if "queryPlanner" in explain_result:
        planner = explain_result["queryPlanner"]
        winning_plan = planner.get("winningPlan", {})

        # Determine scan type
        stage = winning_plan.get("stage", "")
        input_stage = winning_plan.get("inputStage", {})

        if stage == "COLLSCAN":
            print(f"  Scan Type:     COLLSCAN ⚠️  (full collection scan)")
        elif stage == "IXSCAN":
            print(f"  Scan Type:     IXSCAN ✅ (index scan)")
            print(f"  Index Used:    {input_stage.get('indexName', 'N/A') if input_stage else winning_plan.get('indexName', 'N/A')}")
        elif stage == "FETCH":
            inner = input_stage
            if inner.get("stage") == "IXSCAN":
                print(f"  Scan Type:     IXSCAN → FETCH ✅")
                print(f"  Index Used:    {inner.get('indexName', 'N/A')}")
            else:
                print(f"  Scan Type:     {stage} → {inner.get('stage', 'N/A')}")
        else:
            print(f"  Scan Type:     {stage}")

    # Execution stats (available with "executionStats" verbosity)
    if "executionStats" in explain_result:
        stats = explain_result["executionStats"]
        print(f"  Docs Examined: {stats.get('totalDocsExamined', 'N/A'):,}")
        print(f"  Keys Examined: {stats.get('totalKeysExamined', 'N/A'):,}")
        print(f"  Docs Returned: {stats.get('nReturned', 'N/A'):,}")
        print(f"  Exec Time:     {stats.get('executionTimeMillis', 'N/A')} ms")

        # Efficiency ratio
        returned = stats.get("nReturned", 0)
        examined = stats.get("totalDocsExamined", 0)
        if examined > 0 and returned > 0:
            ratio = examined / returned
            if ratio > 10:
                print(f"  Efficiency:    {ratio:.0f}:1 (examined:returned) ⚠️  Could be better")
            else:
                print(f"  Efficiency:    {ratio:.1f}:1 (examined:returned) ✅")


def main():
    db = get_database()
    movies = db["movies"]

    # =========================================================================
    # Example 1: Query WITHOUT index (COLLSCAN)
    # =========================================================================
    print("=" * 60)
    print("Example 1: Query WITHOUT a specific index")
    print("  Query: find({rated: 'PG-13', year: {$gte: 2010}})")
    print("=" * 60)

    # Use the command interface for explain with verbosity
    explain = db.command(
        "explain",
        {
            "find": "movies",
            "filter": {"rated": "PG-13", "year": {"$gte": 2010}}
        },
        verbosity="executionStats"
    )
    print_explain_summary(explain)

    # =========================================================================
    # Example 2: Create an index and compare
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Example 2: SAME query WITH compound index")
    print("  Index: {rated: 1, year: 1}")
    print("=" * 60)

    # Create the index
    index_name = movies.create_index([("rated", 1), ("year", 1)])
    print(f"  Created index: {index_name}")

    explain = db.command(
        "explain",
        {
            "find": "movies",
            "filter": {"rated": "PG-13", "year": {"$gte": 2010}}
        },
        verbosity="executionStats"
    )
    print_explain_summary(explain)

    # Clean up
    movies.drop_index(index_name)

    # =========================================================================
    # Example 3: Sort without index vs with index
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Example 3: Sorting — with and without index")
    print("  Query: find({}).sort({imdb.rating: -1}).limit(10)")
    print("=" * 60)

    # Without index
    print("\n  --- Without index ---")
    explain = db.command(
        "explain",
        {
            "find": "movies",
            "filter": {},
            "sort": {"imdb.rating": -1},
            "limit": 10
        },
        verbosity="executionStats"
    )
    print_explain_summary(explain)

    # With index
    index_name = movies.create_index([("imdb.rating", -1)])
    print(f"\n  --- With index: {index_name} ---")
    explain = db.command(
        "explain",
        {
            "find": "movies",
            "filter": {},
            "sort": {"imdb.rating": -1},
            "limit": 10
        },
        verbosity="executionStats"
    )
    print_explain_summary(explain)
    movies.drop_index(index_name)

    # =========================================================================
    # Example 4: Covered Query
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Example 4: Covered Query (index-only, no doc fetch)")
    print("  Query: find({rated: 'R'}, {rated:1, year:1, _id:0})")
    print("=" * 60)

    index_name = movies.create_index([("rated", 1), ("year", 1)])

    explain = db.command(
        "explain",
        {
            "find": "movies",
            "filter": {"rated": "R"},
            "projection": {"rated": 1, "year": 1, "_id": 0}
        },
        verbosity="executionStats"
    )
    print_explain_summary(explain)

    stats = explain.get("executionStats", {})
    docs_examined = stats.get("totalDocsExamined", -1)
    if docs_examined == 0:
        print("  🎯 COVERED QUERY! Zero documents examined — served entirely from index.")
    movies.drop_index(index_name)

    # =========================================================================
    # Example 5: Aggregation Pipeline Explain
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Example 5: Aggregation Pipeline Explain")
    print("  Pipeline: $match → $group → $sort")
    print("=" * 60)

    explain = db.command(
        "explain",
        {
            "aggregate": "movies",
            "pipeline": [
                {"$match": {"year": {"$gte": 2000}}},
                {"$group": {"_id": "$rated", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ],
            "cursor": {}
        },
        verbosity="executionStats"
    )

    # Aggregation explain has a different structure
    if "stages" in explain:
        for stage in explain["stages"]:
            stage_name = list(stage.keys())[0] if stage else "unknown"
            print(f"  Stage: {stage_name}")
    elif "queryPlanner" in explain:
        print_explain_summary(explain)

    # =========================================================================
    # Summary
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("How to Read Explain Output")
    print("=" * 60)
    print("""
  Key fields to check:

  queryPlanner.winningPlan.stage:
    COLLSCAN  → No index used (bad for large collections)
    IXSCAN    → Index scan (good)
    FETCH     → Retrieved documents after index scan (normal)
    SORT      → In-memory sort (bad if sorting large results)

  executionStats:
    totalDocsExamined  → How many docs MongoDB read
    totalKeysExamined  → How many index entries scanned
    nReturned          → How many docs returned to client
    executionTimeMillis → Wall-clock time

  Red flags:
    ⚠️ COLLSCAN on a collection with > 1000 docs
    ⚠️ totalDocsExamined >> nReturned (scanning too many docs)
    ⚠️ In-memory SORT on large result sets
""")


if __name__ == "__main__":
    main()
