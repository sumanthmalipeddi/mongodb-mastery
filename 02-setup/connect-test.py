"""
MongoDB Connection Test Script
==============================
Tests your MongoDB connection (Atlas or Docker) and prints basic info.

Usage:
    1. Copy .env.example to .env and add your connection string
    2. Run: python connect-test.py

What this script does:
    - Loads connection string from .env
    - Connects to MongoDB
    - Pings the server
    - Lists all databases
    - Shows server version info
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError

# Load environment variables from .env file
load_dotenv()


def test_connection():
    """Test MongoDB connection and print server info."""

    # Get connection string from environment
    uri = os.getenv("MONGODB_URI")

    if not uri:
        print("❌ ERROR: MONGODB_URI not found in .env file")
        print()
        print("Fix: Create a .env file with your connection string:")
        print('  MONGODB_URI=mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/')
        print()
        print("Or for Docker:")
        print('  MONGODB_URI=mongodb://admin:secret123@localhost:27017/')
        sys.exit(1)

    print("=" * 50)
    print("MongoDB Connection Test")
    print("=" * 50)
    print()

    # --- Step 1: Connect ---
    print("1. Connecting to MongoDB...")
    try:
        # serverSelectionTimeoutMS: how long to wait before giving up
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)

        # --- Step 2: Ping ---
        print("2. Pinging server...")
        client.admin.command("ping")
        print("   ✅ Ping successful!")
        print()

        # --- Step 3: Server Info ---
        print("3. Server Information:")
        server_info = client.server_info()
        print(f"   MongoDB version: {server_info.get('version', 'unknown')}")
        print()

        # --- Step 4: List Databases ---
        print("4. Available Databases:")
        db_list = client.list_database_names()
        for db_name in sorted(db_list):
            # Get collection count for each database
            db = client[db_name]
            collections = db.list_collection_names()
            print(f"   📁 {db_name} ({len(collections)} collections)")
        print()

        # --- Step 5: Check for sample_mflix ---
        if "sample_mflix" in db_list:
            print("5. sample_mflix database found! ✅")
            mflix = client["sample_mflix"]
            collections = mflix.list_collection_names()
            print(f"   Collections: {', '.join(sorted(collections))}")

            # Count documents in movies collection
            if "movies" in collections:
                count = mflix.movies.count_documents({})
                print(f"   Movies collection: {count} documents")
        else:
            print("5. sample_mflix database NOT found ⚠️")
            print("   If using Atlas: Load sample data from the Atlas UI")
            print("   (Cluster → ... → Load Sample Dataset)")

        print()
        print("=" * 50)
        print("✅ Connection successful! You're ready to go.")
        print("=" * 50)

        client.close()

    except ConfigurationError as e:
        print(f"   ❌ Configuration error: {e}")
        print()
        print("   Common fixes:")
        print("   - Install dnspython: pip install dnspython")
        print("   - Check your connection string format")
        sys.exit(1)

    except ServerSelectionTimeoutError:
        print("   ❌ Connection timed out!")
        print()
        print("   Common fixes:")
        print("   - Atlas: Check Network Access — is your IP whitelisted?")
        print("   - Docker: Is the container running? (docker ps)")
        print("   - VPN: Try disconnecting your VPN")
        sys.exit(1)

    except ConnectionFailure as e:
        print(f"   ❌ Connection failed: {e}")
        print()
        print("   Common fixes:")
        print("   - Check username/password in your connection string")
        print("   - Atlas: Verify the cluster is active (not paused)")
        print("   - Docker: Run 'docker compose up -d' first")
        sys.exit(1)

    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
