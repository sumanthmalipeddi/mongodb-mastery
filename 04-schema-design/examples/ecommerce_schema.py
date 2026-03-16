"""
E-Commerce Schema — Referenced Documents Pattern
=================================================
Demonstrates referencing between collections: products, users, and orders.

This is ideal when:
- Data is accessed independently (browse products without loading orders)
- Relationships are many-to-many
- Documents would be too large with embedding

Usage:
    python ecommerce_schema.py
"""

import os
import sys
from datetime import datetime
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
    db["products"].drop()
    db["users"].drop()
    db["orders"].drop()

    products = db["products"]
    users = db["users"]
    orders = db["orders"]

    print("Schema: E-Commerce with References")
    print("=" * 50)

    # --- Insert Products ---
    print("\n--- Inserting Products ---")
    product_docs = [
        {
            "name": "MongoDB: The Definitive Guide",
            "category": "books",
            "price": 39.99,
            "stock": 150,
            "specs": {
                "pages": 514,
                "publisher": "O'Reilly",
                "edition": "3rd"
            },
            "tags": ["mongodb", "database", "programming"]
        },
        {
            "name": "Mechanical Keyboard",
            "category": "electronics",
            "price": 129.99,
            "stock": 45,
            "specs": {
                "switches": "Cherry MX Blue",
                "layout": "TKL",
                "backlight": "RGB"
            },
            "tags": ["keyboard", "mechanical", "gaming"]
        },
        {
            "name": "Python Crash Course",
            "category": "books",
            "price": 29.99,
            "stock": 200,
            "specs": {
                "pages": 544,
                "publisher": "No Starch Press",
                "edition": "3rd"
            },
            "tags": ["python", "programming", "beginner"]
        }
    ]
    product_result = products.insert_many(product_docs)
    product_ids = product_result.inserted_ids
    print(f"Inserted {len(product_ids)} products")

    # --- Insert Users ---
    print("\n--- Inserting Users ---")
    user_docs = [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "address": {
                "street": "123 Main St",
                "city": "Portland",
                "state": "OR",
                "zip": "97201"
            },
            "created_at": datetime(2024, 6, 15)
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "address": {
                "street": "456 Oak Ave",
                "city": "Seattle",
                "state": "WA",
                "zip": "98101"
            },
            "created_at": datetime(2024, 9, 1)
        }
    ]
    user_result = users.insert_many(user_docs)
    user_ids = user_result.inserted_ids
    print(f"Inserted {len(user_ids)} users")

    # --- Insert Orders (with references to users and products) ---
    print("\n--- Inserting Orders ---")
    order_docs = [
        {
            "user_id": user_ids[0],          # Reference to Alice
            "items": [
                {
                    "product_id": product_ids[0],  # Reference to MongoDB book
                    "name": "MongoDB: The Definitive Guide",  # Denormalized for display
                    "price": 39.99,                            # Price at time of order
                    "quantity": 1
                },
                {
                    "product_id": product_ids[1],  # Reference to keyboard
                    "name": "Mechanical Keyboard",
                    "price": 129.99,
                    "quantity": 1
                }
            ],
            "total": 169.98,
            "status": "delivered",
            "ordered_at": datetime(2025, 1, 10),
            "delivered_at": datetime(2025, 1, 15)
        },
        {
            "user_id": user_ids[1],          # Reference to Bob
            "items": [
                {
                    "product_id": product_ids[2],  # Reference to Python book
                    "name": "Python Crash Course",
                    "price": 29.99,
                    "quantity": 2
                }
            ],
            "total": 59.98,
            "status": "shipped",
            "ordered_at": datetime(2025, 2, 1),
            "delivered_at": None
        }
    ]
    order_result = orders.insert_many(order_docs)
    print(f"Inserted {len(order_result.inserted_ids)} orders")

    # Create indexes on reference fields (critical for $lookup performance!)
    orders.create_index("user_id")
    orders.create_index("items.product_id")
    products.create_index("category")

    # --- Query 1: Get all orders for a user ---
    print("\n--- Query 1: All orders for Alice ---")
    alice_orders = list(orders.find(
        {"user_id": user_ids[0]},
        {"total": 1, "status": 1, "ordered_at": 1, "_id": 0}
    ))
    for order in alice_orders:
        print(f"  ${order['total']} — {order['status']} — {order['ordered_at'].strftime('%Y-%m-%d')}")

    # --- Query 2: $lookup — Join orders with user details ---
    print("\n--- Query 2: $lookup — Orders with user details ---")
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},  # Convert user array to object
        {
            "$project": {
                "user.name": 1,
                "total": 1,
                "status": 1,
                "item_count": {"$size": "$items"},
                "_id": 0
            }
        }
    ]
    for result in orders.aggregate(pipeline):
        print(f"  {result['user']['name']} — ${result['total']} — "
              f"{result['item_count']} items — {result['status']}")

    # --- Query 3: Revenue by product category ---
    print("\n--- Query 3: Revenue analysis ---")
    pipeline = [
        {"$unwind": "$items"},
        {
            "$lookup": {
                "from": "products",
                "localField": "items.product_id",
                "foreignField": "_id",
                "as": "product"
            }
        },
        {"$unwind": "$product"},
        {
            "$group": {
                "_id": "$product.category",
                "revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}},
                "items_sold": {"$sum": "$items.quantity"}
            }
        },
        {"$sort": {"revenue": -1}}
    ]
    for result in orders.aggregate(pipeline):
        print(f"  {result['_id']}: ${result['revenue']:.2f} ({result['items_sold']} items)")

    # --- Query 4: Update stock after order ---
    print("\n--- Query 4: Decrease stock for ordered products ---")
    result = products.update_one(
        {"_id": product_ids[0]},
        {"$inc": {"stock": -1}}
    )
    product = products.find_one({"_id": product_ids[0]})
    print(f"  {product['name']}: stock now {product['stock']}")

    print("\n" + "=" * 50)
    print("Key insight: References keep collections independent.")
    print("Use $lookup when you need to join them.")
    print("Always index your reference fields (user_id, product_id)!")
    print("=" * 50)


if __name__ == "__main__":
    main()
