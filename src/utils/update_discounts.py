import sqlite3
import json
import asyncio
import aiosqlite
import sys
import os

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

async def add_discount_column_if_not_exists():
    """Add discount column to items table if it doesn't exist"""
    async with aiosqlite.connect("database.db") as db:
        # Check if discount column exists
        cursor = await db.execute("PRAGMA table_info(items)")
        columns = await cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'discount' not in column_names:
            print("Adding discount column to items table...")
            await db.execute("ALTER TABLE items ADD COLUMN discount REAL")
            await db.commit()
            print("Discount column added successfully")
        else:
            print("Discount column already exists")

async def update_item_discount(item_id, discount_value):
    """Update the discount for a specific item"""
    await database.fetch("UPDATE items SET discount = ? WHERE id = ?", discount_value, item_id)
    print(f"Updated item {item_id} with discount: {discount_value}")

async def process_catalog_response(offers_data):
    """Process the catalog response and update discounts in the database"""
    for offer in offers_data:
        item_id = offer.get('id', None)
        discount = offer.get('discount', 0)
        
        if item_id is not None:
            # Check if item exists in database
            result = await database.fetch("SELECT id FROM items WHERE id = ?", item_id)
            if result:
                await update_item_discount(item_id, discount)
            else:
                print(f"Item {item_id} not found in database")

async def main():
    # Add the discount column if it doesn't exist
    await add_discount_column_if_not_exists()
    
    # Sample data - replace with actual API response
    sample_offer = {
        "id": 2133,
        "name": "\u041a\u043e\u0444\u0435 \u0432 \u0431\u0430\u043d\u043a\u0430\u0445 \"Green Coffee Fizz\"",
        "price": 540,
        "discount": None,
        "weight": 1380,
        "type": None,
        "is_coffee_or_tea": False,
        "max_quantity": 669,
        "image": "https:\/\/coffee-static.storage.yandexcloud.net\/files\/shares\/data\/_newpack10\/cans\/green_coffee_lemonade.png",
        "grindings": []
    }
    
    # Process the offer
    await process_catalog_response([sample_offer])
    
    print("Database update completed")

if __name__ == "__main__":
    asyncio.run(main()) 