"""
PyMongo Basics — Building Applications with MongoDB
====================================================
Covers: connection management, CRUD with error handling, ObjectId,
datetime handling, cursors, and common patterns.

Usage:
    python pymongo_basics.py
"""

import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import (
    ConnectionFailure,
    OperationFailure,
    DuplicateKeyError,
    ServerSelectionTimeoutError
)
from bson import ObjectId

load_dotenv()


# =========================================================================
# CONNECTION MANAGEMENT
# =========================================================================

def get_client():
    """
    Create a MongoClient with production-ready settings.

    MongoClient manages a connection pool internally.
    Create ONE client and reuse it throughout your application.
    """
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Set MONGODB_URI in your .env file first!")
        sys.exit(1)

    try:
        client = MongoClient(
            uri,
            # Connection pool settings
            maxPoolSize=50,              # Max connections in pool (default: 100)
            minPoolSize=5,               # Min idle connections to keep
            # Timeout settings
            serverSelectionTimeoutMS=5000,  # How long to find a server
            connectTimeoutMS=10000,         # How long to establish connection
            socketTimeoutMS=30000,          # How long to wait for a response
            # Retry settings
            retryWrites=True,            # Auto-retry failed writes (default: True)
            retryReads=True,             # Auto-retry failed reads (default: True)
        )

        # Verify connection
        client.admin.command("ping")
        print("✅ Connected to MongoDB!")
        print(f"   Server: {client.address}")
        return client

    except ServerSelectionTimeoutError:
        print("❌ Could not connect — server not found or IP not whitelisted")
        sys.exit(1)
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def main():
    client = get_client()
    db = client["learning_db"]
    collection = db["pymongo_demo"]

    # Fresh start
    collection.drop()
    print()

    # =========================================================================
    # WORKING WITH ObjectId
    # =========================================================================
    print("=" * 60)
    print("Working with ObjectId")
    print("=" * 60)

    # Generate a new ObjectId
    new_id = ObjectId()
    print(f"\n  New ObjectId: {new_id}")
    print(f"  As string:   {str(new_id)}")
    print(f"  Created at:  {new_id.generation_time}")

    # Convert string back to ObjectId
    id_string = "507f1f77bcf86cd799439011"
    obj_id = ObjectId(id_string)
    print(f"  From string: {obj_id}")

    # Check if a string is a valid ObjectId
    print(f"  Is valid ObjectId ('abc123'): {ObjectId.is_valid('abc123')}")
    print(f"  Is valid ObjectId ('{id_string}'): {ObjectId.is_valid(id_string)}")

    # =========================================================================
    # INSERT WITH ERROR HANDLING
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Insert with Error Handling")
    print("=" * 60)

    # Create a unique index to demonstrate DuplicateKeyError
    collection.create_index("email", unique=True)

    doc = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "age": 29,
        "registered_at": datetime.now(timezone.utc),  # Always use UTC!
        "preferences": {
            "theme": "dark",
            "notifications": True
        },
        "tags": ["premium", "early-adopter"]
    }

    # First insert succeeds
    result = collection.insert_one(doc)
    print(f"\n  Inserted: {result.inserted_id}")

    # Second insert with same email fails (unique constraint)
    try:
        collection.insert_one({"name": "Alice Duplicate", "email": "alice@example.com"})
    except DuplicateKeyError as e:
        print(f"  DuplicateKeyError caught: email already exists")

    # =========================================================================
    # FIND WITH ERROR HANDLING AND CURSORS
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Find — Cursors and Conversion")
    print("=" * 60)

    # Insert more data
    more_users = [
        {"name": "Bob Smith", "email": "bob@example.com", "age": 34, "registered_at": datetime.now(timezone.utc)},
        {"name": "Carol Williams", "email": "carol@example.com", "age": 27, "registered_at": datetime.now(timezone.utc)},
        {"name": "David Lee", "email": "david@example.com", "age": 42, "registered_at": datetime.now(timezone.utc)},
        {"name": "Eve Chen", "email": "eve@example.com", "age": 31, "registered_at": datetime.now(timezone.utc)},
    ]
    collection.insert_many(more_users)

    # find() returns a Cursor — it's lazy (doesn't fetch all at once)
    print("\n  --- Iterating a cursor ---")
    cursor = collection.find({"age": {"$gte": 30}}).sort("age", ASCENDING)

    for doc in cursor:
        print(f"  {doc['name']}, age {doc['age']}")

    # Convert cursor to list (loads everything into memory)
    print("\n  --- Converting to list ---")
    all_users = list(collection.find({}, {"name": 1, "email": 1, "_id": 0}))
    print(f"  Got {len(all_users)} users as a list")
    print(f"  First: {all_users[0]}")

    # find_one returns None if no match (not an exception)
    print("\n  --- find_one with no match ---")
    result = collection.find_one({"name": "Nobody"})
    if result is None:
        print("  No document found — result is None (not an error)")

    # =========================================================================
    # UPDATE WITH ERROR HANDLING
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Update Patterns")
    print("=" * 60)

    # update_one — returns UpdateResult
    print("\n  --- update_one ---")
    result = collection.update_one(
        {"email": "alice@example.com"},
        {
            "$set": {"age": 30, "updated_at": datetime.now(timezone.utc)},
            "$push": {"tags": "verified"}
        }
    )
    print(f"  Matched: {result.matched_count}, Modified: {result.modified_count}")

    # find_one_and_update — returns the document (before or after update)
    print("\n  --- find_one_and_update (returns updated doc) ---")
    from pymongo import ReturnDocument
    updated_doc = collection.find_one_and_update(
        {"email": "bob@example.com"},
        {"$inc": {"age": 1}},
        return_document=ReturnDocument.AFTER  # Return the document AFTER the update
    )
    print(f"  Bob's new age: {updated_doc['age']}")

    # =========================================================================
    # DELETE WITH CONFIRMATION
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Delete Patterns")
    print("=" * 60)

    # Check before deleting
    count_before = collection.count_documents({"age": {"$lt": 28}})
    print(f"\n  Documents matching age < 28: {count_before}")

    if count_before > 0:
        result = collection.delete_many({"age": {"$lt": 28}})
        print(f"  Deleted: {result.deleted_count}")
    else:
        print("  Nothing to delete")

    # find_one_and_delete — returns the deleted document
    print("\n  --- find_one_and_delete ---")
    deleted = collection.find_one_and_delete({"email": "david@example.com"})
    if deleted:
        print(f"  Deleted: {deleted['name']} ({deleted['email']})")

    # =========================================================================
    # DATETIME HANDLING
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("DateTime Best Practices")
    print("=" * 60)

    print("""
  📌 Always store dates in UTC:
     datetime.now(timezone.utc)  ← GOOD
     datetime.now()              ← BAD (local timezone, ambiguous)

  📌 MongoDB stores dates as milliseconds since epoch (ISODate)

  📌 When reading, PyMongo returns timezone-naive datetime objects.
     They represent UTC time.
""")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    remaining = collection.count_documents({})
    print(f"{'=' * 60}")
    print(f"Done! {remaining} documents remaining in collection.")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
