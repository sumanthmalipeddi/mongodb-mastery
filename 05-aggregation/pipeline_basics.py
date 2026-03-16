"""
Aggregation Pipeline Basics
============================
Learn the fundamental aggregation stages: $match, $group, $sort, $limit, $project, $count.

Uses the sample_mflix.movies collection.

Usage:
    python pipeline_basics.py
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()


def get_collection():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Set MONGODB_URI in your .env file first!")
        sys.exit(1)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("✅ Connected to MongoDB!\n")
        db = client["sample_mflix"]
        if "movies" not in db.list_collection_names():
            print("⚠️  Load sample data in Atlas first.")
            sys.exit(1)
        return db["movies"]
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def main():
    movies = get_collection()

    # =========================================================================
    # $match — Filter documents (like WHERE)
    # =========================================================================
    print("=" * 60)
    print("$match — Filter documents")
    print("=" * 60)

    # Count movies from 2000 or later with IMDb rating >= 8.0
    pipeline = [
        {"$match": {
            "year": {"$gte": 2000},
            "imdb.rating": {"$gte": 8.0}
        }},
        {"$count": "high_rated_2000s"}
    ]
    result = list(movies.aggregate(pipeline))
    print(f"\nHighly rated movies (2000+): {result[0]['high_rated_2000s']}")

    # =========================================================================
    # $group — Group and aggregate (like GROUP BY)
    # =========================================================================
    print("\n" + "=" * 60)
    print("$group — Group and aggregate")
    print("=" * 60)

    # Count movies by rating category (G, PG, PG-13, R, etc.)
    print("\n--- Movies count by rating ---")
    pipeline = [
        {"$match": {"rated": {"$exists": True, "$ne": ""}}},
        {"$group": {
            "_id": "$rated",        # Group by this field
            "count": {"$sum": 1}    # Count documents in each group
        }},
        {"$sort": {"count": -1}},   # Sort by count descending
        {"$limit": 10}
    ]
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['_id']:>10}: {doc['count']} movies")

    # Average IMDb rating by decade
    print("\n--- Average IMDb rating by decade ---")
    pipeline = [
        {"$match": {"year": {"$type": "int"}, "imdb.rating": {"$type": "double"}}},
        {"$group": {
            "_id": {
                # Compute decade: 1995 → 1990, 2003 → 2000
                "$multiply": [
                    {"$floor": {"$divide": ["$year", 10]}},
                    10
                ]
            },
            "avg_rating": {"$avg": "$imdb.rating"},
            "movie_count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    for doc in movies.aggregate(pipeline):
        decade = int(doc["_id"])
        print(f"  {decade}s: avg {doc['avg_rating']:.2f} ({doc['movie_count']} movies)")

    # =========================================================================
    # $group with multiple accumulators
    # =========================================================================
    print("\n--- Rating stats by genre (top 5 genres by count) ---")
    pipeline = [
        {"$unwind": "$genres"},  # Flatten genres array first
        {"$match": {"imdb.rating": {"$type": "double"}}},
        {"$group": {
            "_id": "$genres",
            "count": {"$sum": 1},
            "avg_rating": {"$avg": "$imdb.rating"},
            "max_rating": {"$max": "$imdb.rating"},
            "min_rating": {"$min": "$imdb.rating"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['_id']:>12}: {doc['count']} movies | "
              f"avg: {doc['avg_rating']:.1f} | "
              f"range: {doc['min_rating']:.1f}-{doc['max_rating']:.1f}")

    # =========================================================================
    # $sort + $limit — Top N queries
    # =========================================================================
    print("\n" + "=" * 60)
    print("$sort + $limit — Top N queries")
    print("=" * 60)

    # Top 10 longest movies
    print("\n--- Top 10 longest movies ---")
    pipeline = [
        {"$match": {"runtime": {"$exists": True, "$type": "int"}}},
        {"$sort": {"runtime": -1}},
        {"$limit": 10},
        {"$project": {"title": 1, "runtime": 1, "year": 1, "_id": 0}}
    ]
    for doc in movies.aggregate(pipeline):
        hours = doc["runtime"] // 60
        mins = doc["runtime"] % 60
        print(f"  {doc['title'][:40]:<40} {hours}h {mins}m ({doc.get('year', 'N/A')})")

    # =========================================================================
    # $project — Reshape documents (like SELECT with computed fields)
    # =========================================================================
    print("\n" + "=" * 60)
    print("$project — Reshape documents")
    print("=" * 60)

    # Create a summary view of movies
    print("\n--- Movie summaries with computed fields ---")
    pipeline = [
        {"$match": {"year": {"$gte": 2015}, "imdb.rating": {"$gte": 8.5}}},
        {"$project": {
            "_id": 0,
            "title": 1,
            "year": 1,
            "rating": "$imdb.rating",           # Rename nested field
            "genre_count": {"$size": {"$ifNull": ["$genres", []]}},  # Count genres
            "has_poster": {"$cond": {            # Conditional field
                "if": {"$ifNull": ["$poster", False]},
                "then": "Yes",
                "else": "No"
            }}
        }},
        {"$sort": {"rating": -1}},
        {"$limit": 10}
    ]
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['title'][:35]:<35} {doc['year']} | "
              f"Rating: {doc['rating']} | "
              f"Genres: {doc['genre_count']} | "
              f"Poster: {doc['has_poster']}")

    # =========================================================================
    # $count — Count results
    # =========================================================================
    print("\n" + "=" * 60)
    print("$count — Count filtered results")
    print("=" * 60)

    # How many movies have all three: Drama, Romance, and Comedy?
    pipeline = [
        {"$match": {"genres": {"$all": ["Drama", "Romance", "Comedy"]}}},
        {"$count": "drama_romance_comedy_count"}
    ]
    result = list(movies.aggregate(pipeline))
    if result:
        print(f"\nMovies that are Drama + Romance + Comedy: {result[0]['drama_romance_comedy_count']}")

    print("\n" + "=" * 60)
    print("Done! Next: pipeline_advanced.py for $lookup, $facet, $bucket")
    print("=" * 60)


if __name__ == "__main__":
    main()
