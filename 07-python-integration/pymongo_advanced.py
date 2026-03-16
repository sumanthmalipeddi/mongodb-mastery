"""
PyMongo Advanced — Bulk Ops, Transactions, Change Streams, GridFS
==================================================================
Production-grade patterns for building robust MongoDB applications.

Usage:
    python pymongo_advanced.py

Note: Transactions require a replica set (Atlas has this by default;
      standalone Docker does not).
"""

import os
import sys
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne, ReplaceOne
from pymongo.errors import (
    ConnectionFailure, BulkWriteError, OperationFailure
)

load_dotenv()


def get_client():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Set MONGODB_URI in your .env file first!")
        sys.exit(1)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("✅ Connected to MongoDB!\n")
        return client
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def demo_bulk_operations(db):
    """
    Bulk operations let you send multiple write operations in a single
    network round-trip. Much faster than individual operations.
    """
    print("=" * 60)
    print("BULK OPERATIONS")
    print("=" * 60)

    collection = db["bulk_demo"]
    collection.drop()

    # --- Insert many (simple bulk) ---
    print("\n--- insert_many (simple bulk) ---")
    docs = [{"item": f"item_{i}", "qty": i * 10, "status": "new"} for i in range(100)]
    start = time.perf_counter()
    collection.insert_many(docs)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  Inserted 100 docs in {elapsed:.1f} ms")

    # --- bulk_write (mixed operations) ---
    print("\n--- bulk_write (mixed operations in one call) ---")
    operations = [
        InsertOne({"item": "item_new", "qty": 500, "status": "new"}),
        UpdateOne({"item": "item_1"}, {"$set": {"status": "updated"}}),
        UpdateOne({"item": "item_2"}, {"$inc": {"qty": 100}}),
        ReplaceOne({"item": "item_3"}, {"item": "item_3", "qty": 999, "status": "replaced"}),
        DeleteOne({"item": "item_99"}),
    ]

    result = collection.bulk_write(operations)
    print(f"  Inserted: {result.inserted_count}")
    print(f"  Updated:  {result.modified_count}")
    print(f"  Deleted:  {result.deleted_count}")

    # --- Unordered bulk write (continues on error) ---
    print("\n--- Unordered bulk write (continues on error) ---")
    collection.create_index("item", unique=True)

    operations = [
        InsertOne({"item": "unique_1", "qty": 1}),
        InsertOne({"item": "unique_1", "qty": 2}),  # Duplicate — will fail
        InsertOne({"item": "unique_2", "qty": 3}),   # Still executes
    ]

    try:
        result = collection.bulk_write(operations, ordered=False)
    except BulkWriteError as e:
        print(f"  Bulk write errors: {len(e.details.get('writeErrors', []))}")
        print(f"  Successful inserts: {e.details.get('nInserted', 0)}")

    collection.drop()


def demo_transactions(client, db):
    """
    Multi-document ACID transactions.
    Requires a replica set (Atlas has this; standalone Docker does not).
    """
    print(f"\n{'=' * 60}")
    print("TRANSACTIONS (Multi-Document ACID)")
    print("=" * 60)

    accounts = db["accounts"]
    accounts.drop()

    # Create two accounts
    accounts.insert_many([
        {"name": "Alice", "balance": 1000.00},
        {"name": "Bob", "balance": 500.00},
    ])

    print("\n--- Transfer $200 from Alice to Bob (atomic) ---")
    print(f"  Before: Alice={accounts.find_one({'name': 'Alice'})['balance']}, "
          f"Bob={accounts.find_one({'name': 'Bob'})['balance']}")

    # Start a session for the transaction
    try:
        with client.start_session() as session:
            with session.start_transaction():
                # Debit Alice
                accounts.update_one(
                    {"name": "Alice"},
                    {"$inc": {"balance": -200}},
                    session=session
                )
                # Credit Bob
                accounts.update_one(
                    {"name": "Bob"},
                    {"$inc": {"balance": 200}},
                    session=session
                )
                # Transaction commits here (at end of with block)

        print(f"  After:  Alice={accounts.find_one({'name': 'Alice'})['balance']}, "
              f"Bob={accounts.find_one({'name': 'Bob'})['balance']}")
        print("  ✅ Transaction committed successfully")

    except OperationFailure as e:
        if "transaction" in str(e).lower():
            print("  ⚠️  Transactions require a replica set.")
            print("     Atlas: Works out of the box")
            print("     Docker: Standalone doesn't support transactions")
        else:
            print(f"  ❌ Transaction failed: {e}")

    accounts.drop()


def demo_change_streams(db):
    """
    Change streams let you watch for real-time changes to a collection.
    Requires a replica set.
    """
    print(f"\n{'=' * 60}")
    print("CHANGE STREAMS (Real-time Updates)")
    print("=" * 60)

    collection = db["stream_demo"]
    collection.drop()

    print("\n  Change streams watch for real-time database changes.")
    print("  Useful for: triggers, notifications, data sync, event-driven architectures.\n")

    print("  Example usage (conceptual — streams are blocking):")
    print("""
    # Watch for all changes on a collection
    with collection.watch() as stream:
        for change in stream:
            print(change["operationType"])  # insert, update, delete, replace
            print(change["fullDocument"])    # The changed document

    # Watch with filters (only inserts)
    pipeline = [{"$match": {"operationType": "insert"}}]
    with collection.watch(pipeline) as stream:
        for change in stream:
            print(f"New document: {change['fullDocument']}")
    """)

    # Quick non-blocking demonstration
    try:
        with collection.watch(max_await_time_ms=100) as stream:
            # Insert a document to trigger a change
            collection.insert_one({"test": "change_stream", "ts": datetime.now(timezone.utc)})

            # Try to read the change event
            change = stream.try_next()
            if change:
                print(f"  Captured change event: {change['operationType']}")
                print(f"  Document: {change.get('fullDocument', {}).get('test')}")
            else:
                print("  (Change stream requires replica set to capture events)")
    except OperationFailure:
        print("  ⚠️  Change streams require a replica set (Atlas or Docker replica set)")

    collection.drop()


def demo_gridfs(db):
    """
    GridFS stores files larger than 16 MB by splitting them into chunks.
    """
    import gridfs

    print(f"\n{'=' * 60}")
    print("GridFS (Large File Storage)")
    print("=" * 60)

    fs = gridfs.GridFS(db)

    # Store a file
    print("\n--- Storing a file in GridFS ---")
    content = b"This is a sample file content. " * 100  # Simulate file data
    file_id = fs.put(
        content,
        filename="sample_document.txt",
        content_type="text/plain",
        metadata={"author": "Alice", "category": "demo"}
    )
    print(f"  Stored file with ID: {file_id}")
    print(f"  File size: {len(content)} bytes")

    # Retrieve the file
    print("\n--- Retrieving the file ---")
    retrieved = fs.get(file_id)
    print(f"  Filename: {retrieved.filename}")
    print(f"  Content type: {retrieved.content_type}")
    print(f"  Size: {retrieved.length} bytes")
    print(f"  Upload date: {retrieved.upload_date}")
    print(f"  Metadata: {retrieved.metadata}")
    print(f"  First 50 bytes: {retrieved.read(50)}")

    # List all files
    print("\n--- List all GridFS files ---")
    for grid_file in fs.find():
        print(f"  {grid_file.filename} ({grid_file.length} bytes)")

    # Delete the file
    fs.delete(file_id)
    print("\n  Deleted test file")

    # Clean up GridFS collections
    db["fs.files"].drop()
    db["fs.chunks"].drop()


def main():
    client = get_client()
    db = client["learning_db"]

    demo_bulk_operations(db)
    demo_transactions(client, db)
    demo_change_streams(db)
    demo_gridfs(db)

    print(f"\n{'=' * 60}")
    print("Done! Key takeaways:")
    print("  • bulk_write() for batching mixed operations")
    print("  • Transactions for multi-document ACID (needs replica set)")
    print("  • Change streams for real-time reactivity")
    print("  • GridFS for files > 16 MB")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
