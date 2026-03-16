"""
Social Media Schema — Hybrid Approach
======================================
Demonstrates mixing embedding and referencing in the same schema.

Strategy:
- Embed: author summary in posts (denormalized for fast display)
- Embed: recent likes in posts (bounded subset)
- Reference: full followers list (unbounded, separate collection)
- Reference: comments when they grow large

Usage:
    python social_media_schema.py
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId

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

    # Clean slate
    for col in ["sm_users", "sm_posts", "sm_follows"]:
        db[col].drop()

    users_col = db["sm_users"]
    posts_col = db["sm_posts"]
    follows_col = db["sm_follows"]

    print("Schema: Social Media — Hybrid Approach")
    print("=" * 50)

    # --- Insert Users ---
    print("\n--- Inserting Users ---")
    user_docs = [
        {
            "username": "alice_dev",
            "display_name": "Alice Johnson",
            "bio": "Software engineer. MongoDB enthusiast. Coffee addict.",
            "avatar": "/avatars/alice.jpg",
            "stats": {
                "posts": 0,
                "followers": 0,
                "following": 0
            },
            "joined": datetime(2024, 1, 1)
        },
        {
            "username": "bob_codes",
            "display_name": "Bob Smith",
            "bio": "Full-stack developer. Open source contributor.",
            "avatar": "/avatars/bob.jpg",
            "stats": {
                "posts": 0,
                "followers": 0,
                "following": 0
            },
            "joined": datetime(2024, 3, 15)
        },
        {
            "username": "carol_writes",
            "display_name": "Carol Williams",
            "bio": "Tech writer and educator. Making databases fun.",
            "avatar": "/avatars/carol.jpg",
            "stats": {
                "posts": 0,
                "followers": 0,
                "following": 0
            },
            "joined": datetime(2024, 6, 1)
        }
    ]
    user_result = users_col.insert_many(user_docs)
    alice_id, bob_id, carol_id = user_result.inserted_ids
    print(f"Inserted {len(user_result.inserted_ids)} users")

    # --- Create Follow Relationships (separate collection — unbounded) ---
    print("\n--- Creating Follow Relationships ---")
    follow_docs = [
        {"follower_id": bob_id, "following_id": alice_id, "since": datetime(2024, 4, 1)},
        {"follower_id": carol_id, "following_id": alice_id, "since": datetime(2024, 7, 1)},
        {"follower_id": alice_id, "following_id": bob_id, "since": datetime(2024, 5, 1)},
        {"follower_id": carol_id, "following_id": bob_id, "since": datetime(2024, 8, 1)},
        {"follower_id": alice_id, "following_id": carol_id, "since": datetime(2024, 9, 1)},
    ]
    follows_col.insert_many(follow_docs)
    follows_col.create_index("follower_id")
    follows_col.create_index("following_id")

    # Update follower/following counts
    users_col.update_one({"_id": alice_id}, {"$set": {"stats.followers": 2, "stats.following": 2}})
    users_col.update_one({"_id": bob_id}, {"$set": {"stats.followers": 2, "stats.following": 1}})
    users_col.update_one({"_id": carol_id}, {"$set": {"stats.followers": 1, "stats.following": 2}})
    print(f"Created {len(follow_docs)} follow relationships")

    # --- Insert Posts (with denormalized author info + embedded recent likes) ---
    print("\n--- Inserting Posts ---")
    now = datetime.now()
    post_docs = [
        {
            "author_id": alice_id,
            "author": {  # Denormalized! Copied from user doc for fast display
                "username": "alice_dev",
                "display_name": "Alice Johnson",
                "avatar": "/avatars/alice.jpg"
            },
            "content": "Just deployed my first MongoDB Atlas cluster! The free tier is perfect for learning. 🚀",
            "tags": ["mongodb", "atlas", "learning"],
            "media": [],
            "stats": {
                "likes": 2,
                "comments": 1,
                "shares": 0
            },
            "recent_likes": [  # Only store last 3 likes (bounded!)
                {"user_id": bob_id, "username": "bob_codes"},
                {"user_id": carol_id, "username": "carol_writes"}
            ],
            "created_at": now - timedelta(days=2)
        },
        {
            "author_id": bob_id,
            "author": {
                "username": "bob_codes",
                "display_name": "Bob Smith",
                "avatar": "/avatars/bob.jpg"
            },
            "content": "Schema design tip: embed what you read together, reference what you query independently. #mongodb",
            "tags": ["mongodb", "tips", "schema"],
            "media": [],
            "stats": {
                "likes": 5,
                "comments": 2,
                "shares": 3
            },
            "recent_likes": [
                {"user_id": alice_id, "username": "alice_dev"},
                {"user_id": carol_id, "username": "carol_writes"}
            ],
            "created_at": now - timedelta(days=1)
        },
        {
            "author_id": alice_id,
            "author": {
                "username": "alice_dev",
                "display_name": "Alice Johnson",
                "avatar": "/avatars/alice.jpg"
            },
            "content": "Aggregation pipelines are like Unix pipes for your data. $match | $group | $sort — so elegant!",
            "tags": ["mongodb", "aggregation"],
            "media": [],
            "stats": {
                "likes": 8,
                "comments": 0,
                "shares": 1
            },
            "recent_likes": [
                {"user_id": bob_id, "username": "bob_codes"},
                {"user_id": carol_id, "username": "carol_writes"}
            ],
            "created_at": now - timedelta(hours=6)
        }
    ]
    posts_col.insert_many(post_docs)
    posts_col.create_index("author_id")
    posts_col.create_index("tags")
    posts_col.create_index([("created_at", -1)])

    # Update post counts
    users_col.update_one({"_id": alice_id}, {"$set": {"stats.posts": 2}})
    users_col.update_one({"_id": bob_id}, {"$set": {"stats.posts": 1}})
    print(f"Inserted {len(post_docs)} posts")

    # --- Query 1: User profile ---
    print("\n--- Query 1: User Profile ---")
    alice = users_col.find_one({"username": "alice_dev"})
    print(f"  {alice['display_name']} (@{alice['username']})")
    print(f"  {alice['bio']}")
    print(f"  Posts: {alice['stats']['posts']} | "
          f"Followers: {alice['stats']['followers']} | "
          f"Following: {alice['stats']['following']}")

    # --- Query 2: News feed (posts from people you follow) ---
    print("\n--- Query 2: Alice's News Feed ---")
    # Step 1: Get who Alice follows
    following = follows_col.distinct("following_id", {"follower_id": alice_id})
    # Step 2: Get their recent posts
    feed = posts_col.find(
        {"author_id": {"$in": following}},
        {"author.display_name": 1, "content": 1, "stats.likes": 1, "created_at": 1, "_id": 0}
    ).sort("created_at", -1).limit(10)

    for post in feed:
        print(f"  [{post['author']['display_name']}] {post['content'][:60]}...")
        print(f"    ❤️  {post['stats']['likes']} likes")

    # --- Query 3: Who likes a post? (using embedded recent_likes) ---
    print("\n--- Query 3: Who liked the latest post? ---")
    latest = posts_col.find_one(
        {"author_id": alice_id},
        sort=[("created_at", -1)]
    )
    print(f"  Post: {latest['content'][:50]}...")
    print(f"  Liked by: {', '.join(l['username'] for l in latest['recent_likes'])}")

    # --- Query 4: Trending tags ---
    print("\n--- Query 4: Trending Tags ---")
    pipeline = [
        {"$match": {"created_at": {"$gte": now - timedelta(days=7)}}},
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    for tag in posts_col.aggregate(pipeline):
        print(f"  #{tag['_id']}: {tag['count']} posts")

    # --- Query 5: Most popular users (by follower count) ---
    print("\n--- Query 5: Most Popular Users ---")
    pipeline = [
        {"$group": {"_id": "$following_id", "follower_count": {"$sum": 1}}},
        {"$sort": {"follower_count": -1}},
        {
            "$lookup": {
                "from": "sm_users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {"$project": {"user.display_name": 1, "follower_count": 1, "_id": 0}}
    ]
    for result in follows_col.aggregate(pipeline):
        print(f"  {result['user']['display_name']}: {result['follower_count']} followers")

    print("\n" + "=" * 50)
    print("Key insights (Hybrid Approach):")
    print("  • Author info EMBEDDED in posts (fast display, denormalized)")
    print("  • Recent likes EMBEDDED (bounded to last 3)")
    print("  • Follows in SEPARATE collection (unbounded, queried independently)")
    print("  • Stats pre-computed (follower counts, post counts)")
    print("=" * 50)


if __name__ == "__main__":
    main()
