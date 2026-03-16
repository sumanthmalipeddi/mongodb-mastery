"""
Advanced CRUD Operations — Query Operators & More
==================================================
Learn advanced filtering with comparison, logical, array, and element operators.

This script uses the sample_mflix.movies collection (load sample data in Atlas).

Usage:
    python crud_advanced.py

Prerequisites:
    pip install pymongo python-dotenv dnspython
    Load sample data in Atlas (sample_mflix database)
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure

load_dotenv()


def get_collection():
    """Connect and return the sample_mflix.movies collection."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Set MONGODB_URI in your .env file first!")
        sys.exit(1)

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("✅ Connected to MongoDB!\n")
        db = client["sample_mflix"]

        # Verify the collection exists
        if "movies" not in db.list_collection_names():
            print("⚠️  'movies' collection not found in sample_mflix.")
            print("   Load sample data in Atlas: Cluster → ... → Load Sample Dataset")
            sys.exit(1)

        return db["movies"]
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def main():
    movies = get_collection()
    total = movies.count_documents({})
    print(f"Total movies in collection: {total}\n")

    # =========================================================================
    # COMPARISON OPERATORS
    # =========================================================================

    print("=" * 60)
    print("COMPARISON OPERATORS")
    print("=" * 60)

    # --- $gt (greater than) ---
    print("\n--- $gt: Movies released after 2020 ---")
    count = movies.count_documents({"year": {"$gt": 2020}})
    print(f"Count: {count}")
    for movie in movies.find({"year": {"$gt": 2020}}, {"title": 1, "year": 1, "_id": 0}).limit(5):
        print(f"  {movie['title']} ({movie.get('year', 'N/A')})")

    # --- $gte, $lte (range query — like SQL BETWEEN) ---
    print("\n--- $gte + $lte: Movies from 2000-2005 with IMDb rating >= 8.0 ---")
    cursor = movies.find(
        {
            "year": {"$gte": 2000, "$lte": 2005},
            "imdb.rating": {"$gte": 8.0}   # Dot notation for nested fields!
        },
        {"title": 1, "year": 1, "imdb.rating": 1, "_id": 0}
    ).sort("imdb.rating", DESCENDING).limit(5)

    for movie in cursor:
        rating = movie.get("imdb", {}).get("rating", "N/A")
        print(f"  {movie['title']} ({movie.get('year', 'N/A')}) — IMDb: {rating}")

    # --- $ne (not equal) ---
    print("\n--- $ne: Movies NOT rated 'R' (first 5) ---")
    cursor = movies.find(
        {"rated": {"$ne": "R"}},
        {"title": 1, "rated": 1, "_id": 0}
    ).limit(5)
    for movie in cursor:
        print(f"  {movie['title']} — Rated: {movie.get('rated', 'N/A')}")

    # --- $in (match any value in array) ---
    print("\n--- $in: Movies rated PG or PG-13 (first 5) ---")
    cursor = movies.find(
        {"rated": {"$in": ["PG", "PG-13"]}},
        {"title": 1, "rated": 1, "_id": 0}
    ).limit(5)
    for movie in cursor:
        print(f"  {movie['title']} — Rated: {movie.get('rated', 'N/A')}")

    # --- $nin (not in) ---
    print("\n--- $nin: Movies NOT rated R, PG-13, or PG (first 5) ---")
    count = movies.count_documents({"rated": {"$nin": ["R", "PG-13", "PG"]}})
    print(f"Count: {count}")

    # =========================================================================
    # ELEMENT OPERATORS
    # =========================================================================

    print("\n" + "=" * 60)
    print("ELEMENT OPERATORS")
    print("=" * 60)

    # --- $exists: Check if a field exists ---
    print("\n--- $exists: Movies that have an 'awards' field ---")
    with_awards = movies.count_documents({"awards": {"$exists": True}})
    without_awards = movies.count_documents({"awards": {"$exists": False}})
    print(f"With awards field: {with_awards}")
    print(f"Without awards field: {without_awards}")

    # --- $type: Check field type ---
    print("\n--- $type: Movies where 'year' is a string (not int) ---")
    # Some movies have year as a string like "2010è" in messy data
    string_years = movies.count_documents({"year": {"$type": "string"}})
    int_years = movies.count_documents({"year": {"$type": "int"}})
    print(f"Year as string: {string_years}")
    print(f"Year as int: {int_years}")

    # =========================================================================
    # REGEX OPERATOR
    # =========================================================================

    print("\n" + "=" * 60)
    print("REGEX OPERATOR")
    print("=" * 60)

    # --- $regex: Pattern matching (like SQL LIKE) ---
    print('\n--- $regex: Movies with "Lord" in the title ---')
    cursor = movies.find(
        {"title": {"$regex": "Lord", "$options": "i"}},  # 'i' = case-insensitive
        {"title": 1, "year": 1, "_id": 0}
    ).limit(10)
    for movie in cursor:
        print(f"  {movie['title']} ({movie.get('year', 'N/A')})")

    print('\n--- $regex: Movies starting with "The Matrix" ---')
    cursor = movies.find(
        {"title": {"$regex": "^The Matrix"}},  # ^ = starts with
        {"title": 1, "year": 1, "_id": 0}
    )
    for movie in cursor:
        print(f"  {movie['title']} ({movie.get('year', 'N/A')})")

    # =========================================================================
    # DOT NOTATION — Querying Nested Documents
    # =========================================================================

    print("\n" + "=" * 60)
    print("DOT NOTATION — Nested Document Queries")
    print("=" * 60)

    # The movies collection has nested fields like imdb.rating, imdb.votes
    print("\n--- Dot notation: High-rated movies with many votes ---")
    cursor = movies.find(
        {
            "imdb.rating": {"$gte": 9.0},
            "imdb.votes": {"$gte": 10000}
        },
        {"title": 1, "imdb.rating": 1, "imdb.votes": 1, "_id": 0}
    ).sort("imdb.rating", DESCENDING).limit(10)

    for movie in cursor:
        imdb = movie.get("imdb", {})
        print(f"  {movie['title']} — Rating: {imdb.get('rating')}, Votes: {imdb.get('votes')}")

    # =========================================================================
    # ARRAY QUERIES
    # =========================================================================

    print("\n" + "=" * 60)
    print("ARRAY QUERIES")
    print("=" * 60)

    # --- Simple array match: Contains a value ---
    print('\n--- Array contains "Drama" ---')
    drama_count = movies.count_documents({"genres": "Drama"})
    print(f"Movies with 'Drama' genre: {drama_count}")

    # --- $all: Must contain ALL specified values ---
    print('\n--- $all: Movies that are BOTH "Drama" AND "Romance" ---')
    cursor = movies.find(
        {"genres": {"$all": ["Drama", "Romance"]}},
        {"title": 1, "genres": 1, "_id": 0}
    ).limit(5)
    for movie in cursor:
        print(f"  {movie['title']} — {movie.get('genres', [])}")

    # --- $size: Array with exact length ---
    print("\n--- $size: Movies with exactly 1 genre ---")
    single_genre = movies.count_documents({"genres": {"$size": 1}})
    print(f"Movies with exactly 1 genre: {single_genre}")

    # Show some examples
    cursor = movies.find(
        {"genres": {"$size": 1}},
        {"title": 1, "genres": 1, "_id": 0}
    ).limit(5)
    for movie in cursor:
        print(f"  {movie['title']} — {movie.get('genres', [])}")

    # --- $elemMatch: Match array elements with multiple conditions ---
    # This is useful when you have an array of objects
    print("\n--- $elemMatch example (if applicable) ---")
    # For the movies collection, let's query the cast array
    cursor = movies.find(
        {"cast": {"$elemMatch": {"$regex": "^Robert"}}},
        {"title": 1, "cast": 1, "_id": 0}
    ).limit(3)
    for movie in cursor:
        cast = movie.get("cast", [])
        roberts = [c for c in cast if c.startswith("Robert")]
        print(f"  {movie['title']} — Roberts: {roberts}")

    # =========================================================================
    # SORTING, LIMITING, SKIPPING
    # =========================================================================

    print("\n" + "=" * 60)
    print("SORTING, LIMITING, SKIPPING")
    print("=" * 60)

    # --- Sort ascending ---
    print("\n--- Oldest 5 movies (sort by year ascending) ---")
    cursor = movies.find(
        {"year": {"$type": "int"}},
        {"title": 1, "year": 1, "_id": 0}
    ).sort("year", ASCENDING).limit(5)
    for movie in cursor:
        print(f"  {movie['title']} ({movie['year']})")

    # --- Sort descending ---
    print("\n--- Top 5 highest-rated movies ---")
    cursor = movies.find(
        {"imdb.rating": {"$exists": True, "$ne": ""}},
        {"title": 1, "imdb.rating": 1, "_id": 0}
    ).sort("imdb.rating", DESCENDING).limit(5)
    for movie in cursor:
        print(f"  {movie['title']} — IMDb: {movie.get('imdb', {}).get('rating')}")

    # --- Multi-field sort ---
    print("\n--- Sort by year DESC, then rating DESC (2015+ movies) ---")
    cursor = movies.find(
        {"year": {"$gte": 2015}, "imdb.rating": {"$gte": 8.0}},
        {"title": 1, "year": 1, "imdb.rating": 1, "_id": 0}
    ).sort([("year", DESCENDING), ("imdb.rating", DESCENDING)]).limit(5)
    for movie in cursor:
        print(f"  {movie['title']} ({movie.get('year')}) — {movie.get('imdb', {}).get('rating')}")

    # --- Skip (pagination) ---
    print("\n--- Pagination: Page 2 of results (skip 5, limit 5) ---")
    cursor = movies.find(
        {"year": 2010},
        {"title": 1, "_id": 0}
    ).skip(5).limit(5)
    for movie in cursor:
        print(f"  {movie['title']}")

    # =========================================================================
    # LOGICAL OPERATORS
    # =========================================================================

    print("\n" + "=" * 60)
    print("LOGICAL OPERATORS")
    print("=" * 60)

    # --- $or: Match either condition ---
    print('\n--- $or: Movies rated "G" OR year before 1930 ---')
    count = movies.count_documents({
        "$or": [
            {"rated": "G"},
            {"year": {"$lt": 1930}}
        ]
    })
    print(f"Count: {count}")

    # --- $and: Match both conditions (explicit — usually implicit) ---
    print('\n--- $and: Drama movies with rating > 9.0 ---')
    # Note: You usually don't need $and explicitly because multiple conditions
    # in the same dict are implicitly AND. Use $and when you need multiple
    # conditions on the same field.
    count = movies.count_documents({
        "$and": [
            {"imdb.rating": {"$gt": 9.0}},
            {"genres": "Drama"}
        ]
    })
    print(f"Count: {count}")

    # --- $nor: Match NEITHER condition ---
    print('\n--- $nor: Movies that are neither Drama nor Comedy ---')
    count = movies.count_documents({
        "$nor": [
            {"genres": "Drama"},
            {"genres": "Comedy"}
        ]
    })
    print(f"Count: {count}")

    # =========================================================================
    # DISTINCT
    # =========================================================================

    print("\n" + "=" * 60)
    print("DISTINCT VALUES")
    print("=" * 60)

    # --- distinct: Unique values for a field ---
    print("\n--- All unique ratings ---")
    ratings = movies.distinct("rated")
    print(f"Ratings: {sorted([r for r in ratings if isinstance(r, str)])}")

    print("\n--- Unique genres ---")
    genres = movies.distinct("genres")
    print(f"Genres ({len(genres)}): {sorted(genres)}")

    # --- distinct with filter ---
    print('\n--- Languages used in movies from 2020+ ---')
    languages = movies.distinct("languages", {"year": {"$gte": 2020}})
    print(f"Languages ({len(languages)}): {sorted(languages)[:15]}...")

    print("\n" + "=" * 60)
    print("Done! Try the exercises in exercises.md next.")
    print("=" * 60)


if __name__ == "__main__":
    main()
