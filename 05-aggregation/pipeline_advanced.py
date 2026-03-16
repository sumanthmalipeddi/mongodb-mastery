"""
Advanced Aggregation Pipeline Stages
=====================================
Learn: $lookup (joins), $unwind, $addFields, $facet, $bucket, $merge, $expr.

Uses sample_mflix database (movies and comments collections).

Usage:
    python pipeline_advanced.py
"""

import os
import sys
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


def main():
    db = get_database()
    movies = db["movies"]

    # =========================================================================
    # $lookup — Join collections (like SQL JOIN)
    # =========================================================================
    print("=" * 60)
    print("$lookup — Join movies with comments")
    print("=" * 60)

    # Find movies with their comment count
    pipeline = [
        {"$match": {"title": {"$regex": "^The Godfather"}}},
        {
            "$lookup": {
                "from": "comments",           # Collection to join
                "localField": "_id",           # Field in movies
                "foreignField": "movie_id",    # Field in comments
                "as": "movie_comments"         # Output array field name
            }
        },
        {
            "$project": {
                "title": 1,
                "year": 1,
                "comment_count": {"$size": "$movie_comments"},
                "sample_comment": {"$arrayElemAt": ["$movie_comments.text", 0]},
                "_id": 0
            }
        }
    ]
    print("\n--- Movies starting with 'The Godfather' + comment counts ---")
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['title']} ({doc.get('year', 'N/A')}) — {doc['comment_count']} comments")
        if doc.get("sample_comment"):
            print(f"    First comment: {doc['sample_comment'][:80]}...")

    # =========================================================================
    # $unwind — Flatten arrays
    # =========================================================================
    print("\n" + "=" * 60)
    print("$unwind — Flatten arrays")
    print("=" * 60)

    # Find the most common genres across all movies
    print("\n--- Most common genres ---")
    pipeline = [
        {"$unwind": "$genres"},       # One doc per genre per movie
        {"$group": {
            "_id": "$genres",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['_id']:>15}: {doc['count']} movies")

    # =========================================================================
    # $addFields — Add computed fields without dropping existing ones
    # =========================================================================
    print("\n" + "=" * 60)
    print("$addFields — Add computed fields")
    print("=" * 60)

    # Add a "popularity_score" based on rating and votes
    print("\n--- Movies with computed popularity score ---")
    pipeline = [
        {"$match": {
            "imdb.rating": {"$type": "double"},
            "imdb.votes": {"$type": "int"},
            "year": {"$gte": 2010}
        }},
        {"$addFields": {
            "popularity_score": {
                "$multiply": [
                    "$imdb.rating",
                    {"$log10": {"$add": ["$imdb.votes", 1]}}
                ]
            }
        }},
        {"$sort": {"popularity_score": -1}},
        {"$limit": 10},
        {"$project": {
            "title": 1, "year": 1,
            "imdb.rating": 1, "imdb.votes": 1,
            "popularity_score": {"$round": ["$popularity_score", 2]},
            "_id": 0
        }}
    ]
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['title'][:35]:<35} Score: {doc['popularity_score']} "
              f"(Rating: {doc['imdb']['rating']}, Votes: {doc['imdb']['votes']})")

    # =========================================================================
    # $facet — Multiple aggregations in one query
    # =========================================================================
    print("\n" + "=" * 60)
    print("$facet — Multiple aggregations in one query")
    print("=" * 60)

    # Get rating distribution AND top genres in a single query
    pipeline = [
        {"$match": {"year": {"$gte": 2000}, "imdb.rating": {"$type": "double"}}},
        {
            "$facet": {
                # Facet 1: Rating distribution
                "rating_distribution": [
                    {"$bucket": {
                        "groupBy": "$imdb.rating",
                        "boundaries": [0, 2, 4, 6, 8, 10.1],
                        "default": "unknown",
                        "output": {"count": {"$sum": 1}}
                    }}
                ],
                # Facet 2: Top 5 genres
                "top_genres": [
                    {"$unwind": "$genres"},
                    {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 5}
                ],
                # Facet 3: Summary stats
                "stats": [
                    {"$group": {
                        "_id": None,
                        "total": {"$sum": 1},
                        "avg_rating": {"$avg": "$imdb.rating"},
                        "avg_runtime": {"$avg": "$runtime"}
                    }}
                ]
            }
        }
    ]

    result = list(movies.aggregate(pipeline))[0]

    print("\n--- Rating Distribution (2000+) ---")
    labels = ["0-2", "2-4", "4-6", "6-8", "8-10"]
    for i, bucket in enumerate(result["rating_distribution"]):
        if i < len(labels):
            bar = "█" * (bucket["count"] // 100)
            print(f"  {labels[i]:>5}: {bucket['count']:>5} {bar}")

    print("\n--- Top 5 Genres (2000+) ---")
    for genre in result["top_genres"]:
        print(f"  {genre['_id']:>12}: {genre['count']}")

    if result["stats"]:
        stats = result["stats"][0]
        print(f"\n--- Summary ---")
        print(f"  Total movies: {stats['total']}")
        print(f"  Avg rating: {stats['avg_rating']:.2f}")
        if stats.get("avg_runtime"):
            print(f"  Avg runtime: {stats['avg_runtime']:.0f} min")

    # =========================================================================
    # $bucket — Group into ranges
    # =========================================================================
    print("\n" + "=" * 60)
    print("$bucket — Group into ranges")
    print("=" * 60)

    # Group movies by runtime ranges
    print("\n--- Movies by runtime range ---")
    pipeline = [
        {"$match": {"runtime": {"$exists": True, "$type": "int"}}},
        {"$bucket": {
            "groupBy": "$runtime",
            "boundaries": [0, 60, 90, 120, 150, 180, 500],
            "default": "other",
            "output": {
                "count": {"$sum": 1},
                "avg_rating": {"$avg": "$imdb.rating"},
                "titles": {"$push": "$title"}
            }
        }}
    ]
    labels = ["< 60m", "60-90m", "90-120m", "120-150m", "150-180m", "180m+"]
    for i, bucket in enumerate(movies.aggregate(pipeline)):
        if i < len(labels):
            avg = f"{bucket['avg_rating']:.1f}" if bucket.get('avg_rating') else "N/A"
            print(f"  {labels[i]:>10}: {bucket['count']:>5} movies (avg rating: {avg})")

    # =========================================================================
    # $expr — Use aggregation expressions in $match
    # =========================================================================
    print("\n" + "=" * 60)
    print("$expr — Aggregation expressions in queries")
    print("=" * 60)

    # Find movies where the number of cast members exceeds the number of genres
    print("\n--- Movies with more cast than genres ---")
    pipeline = [
        {"$match": {
            "cast": {"$exists": True},
            "genres": {"$exists": True},
            "$expr": {
                "$gt": [
                    {"$size": {"$ifNull": ["$cast", []]}},
                    {"$multiply": [{"$size": {"$ifNull": ["$genres", []]}}, 3]}
                ]
            }
        }},
        {"$project": {
            "title": 1,
            "cast_count": {"$size": "$cast"},
            "genre_count": {"$size": "$genres"},
            "_id": 0
        }},
        {"$sort": {"cast_count": -1}},
        {"$limit": 5}
    ]
    for doc in movies.aggregate(pipeline):
        print(f"  {doc['title'][:40]:<40} Cast: {doc['cast_count']} | Genres: {doc['genre_count']}")

    print("\n" + "=" * 60)
    print("Done! Next: real_world_queries.py for practical examples")
    print("=" * 60)


if __name__ == "__main__":
    main()
