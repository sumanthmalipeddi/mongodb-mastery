"""
CRUD Basics — MongoDB with PyMongo
===================================
Learn the four fundamental operations: Create, Read, Update, Delete.

This script uses a 'learning_db' database with a 'users' collection
so it won't interfere with sample data.

Usage:
    python crud_basics.py

Prerequisites:
    pip install pymongo python-dotenv dnspython
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from bson import ObjectId

load_dotenv()


def get_database():
    """Connect to MongoDB and return the learning database."""
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
    collection = db["users"]

    # Clean up from previous runs
    collection.drop()
    print("Starting with a fresh 'users' collection.\n")

    # =========================================================================
    # CREATE — Inserting Documents
    # =========================================================================

    print("=" * 60)
    print("CREATE OPERATIONS")
    print("=" * 60)

    # --- insert_one: Insert a single document ---
    print("\n--- insert_one ---")
    result = collection.insert_one({
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "age": 29,
        "city": "Portland",
        "hobbies": ["reading", "hiking", "coding"],
        "joined": datetime(2024, 1, 15)
    })
    # insert_one returns an InsertOneResult with the generated _id
    print(f"Inserted document with _id: {result.inserted_id}")

    # --- insert_many: Insert multiple documents at once ---
    print("\n--- insert_many ---")
    users = [
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "age": 34,
            "city": "Seattle",
            "hobbies": ["gaming", "cooking"],
            "joined": datetime(2024, 3, 20)
        },
        {
            "name": "Carol Williams",
            "email": "carol@example.com",
            "age": 27,
            "city": "Portland",
            "hobbies": ["painting", "yoga", "reading"],
            "joined": datetime(2024, 5, 10)
        },
        {
            "name": "David Lee",
            "email": "david@example.com",
            "age": 42,
            "city": "San Francisco",
            "hobbies": ["photography", "travel"],
            "joined": datetime(2024, 7, 1)
        },
        {
            "name": "Eve Chen",
            "email": "eve@example.com",
            "age": 31,
            "city": "Seattle",
            "hobbies": ["coding", "music", "hiking"],
            "joined": datetime(2024, 8, 15)
        }
    ]
    result = collection.insert_many(users)
    print(f"Inserted {len(result.inserted_ids)} documents")
    print(f"IDs: {result.inserted_ids}")

    # =========================================================================
    # READ — Querying Documents
    # =========================================================================

    print("\n" + "=" * 60)
    print("READ OPERATIONS")
    print("=" * 60)

    # --- find_one: Get a single document ---
    print("\n--- find_one ---")
    user = collection.find_one({"name": "Alice Johnson"})
    print(f"Found: {user['name']}, age {user['age']}, city: {user['city']}")

    # --- find_one with no match returns None ---
    print("\n--- find_one (no match) ---")
    user = collection.find_one({"name": "Nobody"})
    print(f"Result: {user}")  # None

    # --- find: Get multiple documents ---
    print("\n--- find (all users in Portland) ---")
    cursor = collection.find({"city": "Portland"})
    # A cursor is an iterator — loop through it
    for user in cursor:
        print(f"  {user['name']} - {user['city']}")

    # --- find with projection: Only return specific fields ---
    print("\n--- find with projection (name and age only) ---")
    # 1 = include field, 0 = exclude field
    # _id is included by default; set to 0 to exclude
    cursor = collection.find(
        {},  # empty filter = match all
        {"name": 1, "age": 1, "_id": 0}
    )
    for user in cursor:
        print(f"  {user}")

    # --- count_documents ---
    print("\n--- count_documents ---")
    total = collection.count_documents({})
    portland_count = collection.count_documents({"city": "Portland"})
    print(f"Total users: {total}")
    print(f"Users in Portland: {portland_count}")

    # --- distinct: Get unique values ---
    print("\n--- distinct ---")
    cities = collection.distinct("city")
    print(f"Unique cities: {cities}")

    # =========================================================================
    # UPDATE — Modifying Documents
    # =========================================================================

    print("\n" + "=" * 60)
    print("UPDATE OPERATIONS")
    print("=" * 60)

    # --- update_one with $set: Update specific fields ---
    print("\n--- update_one with $set ---")
    result = collection.update_one(
        {"name": "Alice Johnson"},       # filter: which document
        {"$set": {"age": 30, "city": "Austin"}}  # update: what to change
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

    # Verify the update
    alice = collection.find_one({"name": "Alice Johnson"})
    print(f"Alice is now {alice['age']} years old, living in {alice['city']}")

    # --- update_one with $inc: Increment a value ---
    print("\n--- update_one with $inc ---")
    result = collection.update_one(
        {"name": "Bob Smith"},
        {"$inc": {"age": 1}}  # Increment age by 1
    )
    bob = collection.find_one({"name": "Bob Smith"})
    print(f"Bob's age after increment: {bob['age']}")

    # --- update_one with $push: Add to an array ---
    print("\n--- update_one with $push ---")
    result = collection.update_one(
        {"name": "Bob Smith"},
        {"$push": {"hobbies": "running"}}
    )
    bob = collection.find_one({"name": "Bob Smith"})
    print(f"Bob's hobbies: {bob['hobbies']}")

    # --- update_many: Update all matching documents ---
    print("\n--- update_many ---")
    result = collection.update_many(
        {"city": "Seattle"},
        {"$set": {"region": "Pacific Northwest"}}
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

    # --- replace_one: Replace the entire document ---
    print("\n--- replace_one ---")
    # ⚠️ This replaces everything except _id
    result = collection.replace_one(
        {"name": "David Lee"},
        {
            "name": "David Lee",
            "email": "david.lee@newmail.com",
            "age": 43,
            "city": "Los Angeles",
            "hobbies": ["surfing", "photography"],
            "joined": datetime(2024, 7, 1),
            "status": "active"
        }
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

    # --- upsert: Insert if not found, update if found ---
    print("\n--- upsert (insert or update) ---")
    result = collection.update_one(
        {"name": "Frank Garcia"},      # This person doesn't exist
        {"$set": {
            "name": "Frank Garcia",
            "email": "frank@example.com",
            "age": 28,
            "city": "Miami"
        }},
        upsert=True  # Create the document if it doesn't exist
    )
    print(f"Matched: {result.matched_count}, Upserted ID: {result.upserted_id}")

    # =========================================================================
    # DELETE — Removing Documents
    # =========================================================================

    print("\n" + "=" * 60)
    print("DELETE OPERATIONS")
    print("=" * 60)

    # --- delete_one: Remove a single document ---
    print("\n--- delete_one ---")
    result = collection.delete_one({"name": "Frank Garcia"})
    print(f"Deleted: {result.deleted_count} document(s)")

    # --- delete_many: Remove multiple documents ---
    print("\n--- delete_many ---")
    result = collection.delete_many({"city": "Seattle"})
    print(f"Deleted: {result.deleted_count} document(s) from Seattle")

    # --- Final count ---
    print(f"\nRemaining documents: {collection.count_documents({})}")
    print("\nAll remaining users:")
    for user in collection.find({}, {"name": 1, "city": 1, "_id": 0}):
        print(f"  {user['name']} - {user['city']}")

    # =========================================================================
    # CLEANUP
    # =========================================================================
    print("\n" + "=" * 60)
    print("Done! The 'users' collection in 'learning_db' still has data.")
    print("Run this script again to start fresh (it drops the collection).")
    print("=" * 60)


if __name__ == "__main__":
    main()
