#!/usr/bin/env python3
"""
Test script for the database update functionality.
This script can be run independently to test the data collection process.
"""

import sys
import os
import sqlite3
from pathlib import Path

# Try to import optional packages with fallbacks
PANDAS_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    print("Warning: pandas not found. Using fallback implementation.")
    print("For better performance, install pandas: pip install pandas")

def main():
    print("Testing database update functionality...")
    
    # Import the update_database module
    try:
        sys.path.append(str(Path(__file__).parent / 'src'))
        from utils.update_database import main as update_db
    except ImportError as e:
        print(f"Error importing update_database module: {e}")
        return False
    
    # Backup the current database if it exists
    db_path = Path(__file__).parent / "database.db"
    if db_path.exists():
        print("Backing up current database...")
        backup_path = db_path.with_suffix(".db.bak")
        try:
            with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            print(f"Backup created at {backup_path}")
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    # Run the update process
    print("Running database update process...")
    success = update_db()
    
    if success:
        print("Database update successful!")
        
        # Verify the database was updated correctly
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check categories table
            if PANDAS_AVAILABLE:
                categories_count = pd.read_sql_query("SELECT COUNT(*) as count FROM categories", conn).iloc[0]['count']
                items_count = pd.read_sql_query("SELECT COUNT(*) as count FROM items", conn).iloc[0]['count']
            else:
                cursor.execute("SELECT COUNT(*) FROM categories")
                categories_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM items")
                items_count = cursor.fetchone()[0]
            
            print(f"Categories count: {categories_count}")
            print(f"Items count: {items_count}")
            
            conn.close()
            
            if categories_count > 0 and items_count > 0:
                print("Verification successful: Database contains data.")
                return True
            else:
                print("Verification failed: Database appears to be empty.")
                return False
            
        except Exception as e:
            print(f"Error verifying database: {e}")
            return False
    else:
        print("Database update failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 