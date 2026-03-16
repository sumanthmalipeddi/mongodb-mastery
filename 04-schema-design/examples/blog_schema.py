"""
Blog Schema — Embedded Comments Pattern
========================================
Demonstrates embedding related data (comments) directly in blog post documents.

This is ideal when:
- Comments are always read with the post
- Each post has a bounded number of comments (< 100)
- You want atomic updates (add comment + update count in one operation)

Usage:
    python blog_schema.py
"""

import os
import sys
from datetime import datetime
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
        return client["learning_db"]
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def main():
    db = get_database()
    posts = db["blog_posts"]

    # Clean slate
    posts.drop()
    print("Schema: Blog with Embedded Comments")
    print("=" * 50)

    # --- Insert blog posts with embedded comments ---
    sample_posts = [
        {
            "title": "Getting Started with MongoDB",
            "slug": "getting-started-mongodb",
            "author": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "avatar": "/avatars/alice.jpg"
            },
            "content": "MongoDB is a document database that stores data in flexible, JSON-like documents...",
            "tags": ["mongodb", "tutorial", "nosql", "beginner"],
            "status": "published",
            "published_at": datetime(2025, 1, 15),
            "views": 1250,
            "comments": [
                {
                    "author": "Bob Smith",
                    "text": "Great introduction! Very clear explanations.",
                    "date": datetime(2025, 1, 16),
                    "likes": 12
                },
                {
                    "author": "Carol Williams",
                    "text": "This helped me understand the document model. Thanks!",
                    "date": datetime(2025, 1, 17),
                    "likes": 8
                },
                {
                    "author": "David Lee",
                    "text": "Could you write a follow-up on aggregation?",
                    "date": datetime(2025, 1, 20),
                    "likes": 15
                }
            ],
            "comment_count": 3
        },
        {
            "title": "Schema Design Patterns in MongoDB",
            "slug": "schema-design-patterns",
            "author": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "avatar": "/avatars/alice.jpg"
            },
            "content": "Choosing the right schema is the most important decision in MongoDB...",
            "tags": ["mongodb", "schema", "advanced", "patterns"],
            "status": "published",
            "published_at": datetime(2025, 2, 1),
            "views": 890,
            "comments": [
                {
                    "author": "Eve Chen",
                    "text": "The bucket pattern explanation was exactly what I needed!",
                    "date": datetime(2025, 2, 3),
                    "likes": 20
                }
            ],
            "comment_count": 1
        },
        {
            "title": "MongoDB Aggregation Deep Dive",
            "slug": "aggregation-deep-dive",
            "author": {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "avatar": "/avatars/bob.jpg"
            },
            "content": "The aggregation framework is MongoDB's most powerful feature...",
            "tags": ["mongodb", "aggregation", "advanced"],
            "status": "draft",
            "published_at": None,
            "views": 0,
            "comments": [],
            "comment_count": 0
        }
    ]

    result = posts.insert_many(sample_posts)
    print(f"Inserted {len(result.inserted_ids)} blog posts\n")

    # --- Query 1: Get a post with all its comments (single read!) ---
    print("--- Query 1: Get post with comments (single read) ---")
    post = posts.find_one(
        {"slug": "getting-started-mongodb"},
        {"title": 1, "comments": 1, "comment_count": 1, "_id": 0}
    )
    print(f"Post: {post['title']} ({post['comment_count']} comments)")
    for comment in post["comments"]:
        print(f"  💬 {comment['author']}: {comment['text'][:50]}...")

    # --- Query 2: Add a new comment (atomic operation) ---
    print("\n--- Query 2: Add a new comment ---")
    new_comment = {
        "author": "Frank Garcia",
        "text": "Just what I was looking for! Bookmarked.",
        "date": datetime.now(),
        "likes": 0
    }
    result = posts.update_one(
        {"slug": "getting-started-mongodb"},
        {
            "$push": {"comments": new_comment},
            "$inc": {"comment_count": 1}
        }
    )
    print(f"Added comment. Modified: {result.modified_count}")
    updated = posts.find_one({"slug": "getting-started-mongodb"})
    print(f"Comment count now: {updated['comment_count']}")

    # --- Query 3: Find posts by tag ---
    print("\n--- Query 3: Find all posts tagged 'advanced' ---")
    cursor = posts.find(
        {"tags": "advanced"},
        {"title": 1, "tags": 1, "_id": 0}
    )
    for post in cursor:
        print(f"  {post['title']} — tags: {post['tags']}")

    # --- Query 4: Find published posts sorted by views ---
    print("\n--- Query 4: Published posts by popularity ---")
    cursor = posts.find(
        {"status": "published"},
        {"title": 1, "views": 1, "_id": 0}
    ).sort("views", -1)
    for post in cursor:
        print(f"  {post['title']} — {post['views']} views")

    # --- Query 5: Find posts with highly-liked comments ---
    print("\n--- Query 5: Posts with comments that have 15+ likes ---")
    cursor = posts.find(
        {"comments.likes": {"$gte": 15}},
        {"title": 1, "comments.$": 1, "_id": 0}
    )
    for post in cursor:
        comment = post["comments"][0]
        print(f"  {post['title']} — {comment['author']}: {comment['likes']} likes")

    # --- Aggregation: Most popular tags ---
    print("\n--- Aggregation: Most popular tags ---")
    pipeline = [
        {"$match": {"status": "published"}},
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    for result in posts.aggregate(pipeline):
        print(f"  #{result['_id']}: {result['count']} posts")

    print("\n" + "=" * 50)
    print("Key insight: One read fetches the post AND all comments.")
    print("No joins needed! This is the power of embedding.")
    print("=" * 50)


if __name__ == "__main__":
    main()
