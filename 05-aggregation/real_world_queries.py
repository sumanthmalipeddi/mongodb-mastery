"""
Real-World Aggregation Queries
===============================
10 practical aggregation examples using sample_mflix.movies.

Usage:
    python real_world_queries.py
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
        return client["sample_mflix"]["movies"]
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def main():
    movies = get_collection()

    # =========================================================================
    # Query 1: Top 10 Highest-Rated Movies of All Time
    # =========================================================================
    print("=" * 60)
    print("Query 1: Top 10 Highest-Rated Movies (50K+ votes)")
    print("=" * 60)
    pipeline = [
        {"$match": {"imdb.rating": {"$type": "double"}, "imdb.votes": {"$gte": 50000}}},
        {"$sort": {"imdb.rating": -1}},
        {"$limit": 10},
        {"$project": {"title": 1, "year": 1, "imdb.rating": 1, "imdb.votes": 1, "_id": 0}}
    ]
    for i, doc in enumerate(movies.aggregate(pipeline), 1):
        print(f"  {i:>2}. {doc['title']} ({doc.get('year', '?')}) "
              f"— {doc['imdb']['rating']} ({doc['imdb']['votes']:,} votes)")

    # =========================================================================
    # Query 2: Average IMDb Rating by Decade
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 2: Average IMDb Rating by Decade")
    print("=" * 60)
    pipeline = [
        {"$match": {"year": {"$type": "int"}, "imdb.rating": {"$type": "double"}}},
        {"$group": {
            "_id": {"$multiply": [{"$floor": {"$divide": ["$year", 10]}}, 10]},
            "avg_rating": {"$avg": "$imdb.rating"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gte": 10}}},
        {"$sort": {"_id": 1}}
    ]
    for doc in movies.aggregate(pipeline):
        bar = "█" * int(doc["avg_rating"] * 3)
        print(f"  {int(doc['_id'])}s: {doc['avg_rating']:.2f} {bar} ({doc['count']} movies)")

    # =========================================================================
    # Query 3: Most Prolific Directors
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 3: Most Prolific Directors (Top 10)")
    print("=" * 60)
    pipeline = [
        {"$unwind": "$directors"},
        {"$group": {
            "_id": "$directors",
            "movie_count": {"$sum": 1},
            "avg_rating": {"$avg": "$imdb.rating"}
        }},
        {"$sort": {"movie_count": -1}},
        {"$limit": 10}
    ]
    for doc in movies.aggregate(pipeline):
        avg = f"{doc['avg_rating']:.1f}" if doc.get("avg_rating") else "N/A"
        print(f"  {doc['_id']:<30} {doc['movie_count']:>3} movies (avg: {avg})")

    # =========================================================================
    # Query 4: Movies with Most Comments
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 4: Movies with Most Comments")
    print("=" * 60)
    pipeline = [
        {"$lookup": {
            "from": "comments",
            "localField": "_id",
            "foreignField": "movie_id",
            "as": "comments"
        }},
        {"$addFields": {"comment_count": {"$size": "$comments"}}},
        {"$match": {"comment_count": {"$gt": 0}}},
        {"$sort": {"comment_count": -1}},
        {"$limit": 10},
        {"$project": {"title": 1, "year": 1, "comment_count": 1, "_id": 0}}
    ]
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['title'][:40]:<40} {doc['comment_count']:>3} comments ({doc.get('year', '?')})")

    # =========================================================================
    # Query 5: Genre Popularity Over Time (2000s vs 2010s)
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 5: Genre Popularity — 2000s vs 2010s")
    print("=" * 60)
    pipeline = [
        {"$match": {"year": {"$gte": 2000, "$lt": 2020}}},
        {"$unwind": "$genres"},
        {"$group": {
            "_id": {
                "genre": "$genres",
                "decade": {"$cond": [{"$lt": ["$year", 2010]}, "2000s", "2010s"]}
            },
            "count": {"$sum": 1}
        }},
        {"$group": {
            "_id": "$_id.genre",
            "decades": {"$push": {"decade": "$_id.decade", "count": "$count"}},
            "total": {"$sum": "$count"}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 8}
    ]
    for doc in movies.aggregate(pipeline):
        decades = {d["decade"]: d["count"] for d in doc["decades"]}
        print(f"  {doc['_id']:>12}: 2000s={decades.get('2000s', 0):>4} | 2010s={decades.get('2010s', 0):>4}")

    # =========================================================================
    # Query 6: Average Runtime by Genre
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 6: Average Runtime by Genre")
    print("=" * 60)
    pipeline = [
        {"$match": {"runtime": {"$exists": True, "$type": "int"}}},
        {"$unwind": "$genres"},
        {"$group": {
            "_id": "$genres",
            "avg_runtime": {"$avg": "$runtime"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gte": 50}}},
        {"$sort": {"avg_runtime": -1}},
        {"$limit": 10}
    ]
    for doc in movies.aggregate(pipeline):
        bar = "▓" * int(doc["avg_runtime"] / 10)
        print(f"  {doc['_id']:>15}: {doc['avg_runtime']:.0f} min {bar}")

    # =========================================================================
    # Query 7: Countries Producing the Most Movies
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 7: Top Movie-Producing Countries")
    print("=" * 60)
    pipeline = [
        {"$unwind": "$countries"},
        {"$group": {
            "_id": "$countries",
            "count": {"$sum": 1},
            "avg_rating": {"$avg": "$imdb.rating"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    for doc in movies.aggregate(pipeline):
        avg = f"{doc['avg_rating']:.1f}" if doc.get("avg_rating") else "N/A"
        print(f"  {doc['_id']:<20} {doc['count']:>5} movies (avg rating: {avg})")

    # =========================================================================
    # Query 8: Movies with Ratings Above Their Genre Average
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 8: Above-Average Movies per Genre (Drama)")
    print("=" * 60)
    # First get the average for Drama
    avg_pipeline = [
        {"$match": {"genres": "Drama", "imdb.rating": {"$type": "double"}}},
        {"$group": {"_id": None, "avg": {"$avg": "$imdb.rating"}}}
    ]
    avg_result = list(movies.aggregate(avg_pipeline))
    if avg_result:
        drama_avg = avg_result[0]["avg"]
        print(f"  Drama average rating: {drama_avg:.2f}")
        pipeline = [
            {"$match": {
                "genres": "Drama",
                "imdb.rating": {"$gt": drama_avg},
                "imdb.votes": {"$gte": 10000},
                "year": {"$gte": 2010}
            }},
            {"$sort": {"imdb.rating": -1}},
            {"$limit": 10},
            {"$project": {"title": 1, "imdb.rating": 1, "year": 1, "_id": 0}}
        ]
        for doc in movies.aggregate(pipeline):
            diff = doc["imdb"]["rating"] - drama_avg
            print(f"  {doc['title'][:35]:<35} {doc['imdb']['rating']} (+{diff:.1f})")

    # =========================================================================
    # Query 9: Word Frequency in Movie Plots
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 9: Common Words in Movie Plots (2010+)")
    print("=" * 60)
    pipeline = [
        {"$match": {"plot": {"$exists": True}, "year": {"$gte": 2010}}},
        {"$project": {"words": {"$split": [{"$toLower": "$plot"}, " "]}}},
        {"$unwind": "$words"},
        {"$match": {"words": {"$regex": "^[a-z]{5,}$"}}},  # 5+ letter words only
        {"$group": {"_id": "$words", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    for doc in movies.aggregate(pipeline):
        bar = "█" * (doc["count"] // 10)
        print(f"  {doc['_id']:>15}: {doc['count']:>4} {bar}")

    # =========================================================================
    # Query 10: Best Year for Each Genre
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Query 10: Best Year for Each Genre (by avg rating)")
    print("=" * 60)
    pipeline = [
        {"$match": {"year": {"$type": "int"}, "imdb.rating": {"$type": "double"}}},
        {"$unwind": "$genres"},
        {"$group": {
            "_id": {"genre": "$genres", "year": "$year"},
            "avg_rating": {"$avg": "$imdb.rating"},
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gte": 5}}},
        {"$sort": {"avg_rating": -1}},
        {"$group": {
            "_id": "$_id.genre",
            "best_year": {"$first": "$_id.year"},
            "best_avg": {"$first": "$avg_rating"},
            "movie_count": {"$first": "$count"}
        }},
        {"$sort": {"best_avg": -1}},
        {"$limit": 10}
    ]
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['_id']:>12}: {doc['best_year']} "
              f"(avg: {doc['best_avg']:.2f}, {doc['movie_count']} movies)")

    print(f"\n{'=' * 60}")
    print("Done! Try the exercises in exercises.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
