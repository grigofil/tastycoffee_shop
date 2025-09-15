#!/usr/bin/env python3
"""
Test script for the Telegram bot
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import constants
        print("✓ constants imported")
        
        from config import config
        print("✓ config imported")
        
        import database
        print("✓ database imported")
        
        import models.users as users
        print("✓ models.users imported")
        
        import models.items as items
        print("✓ models.items imported")
        
        import models.categories as categories
        print("✓ models.categories imported")
        
        import models.orders as orders
        print("✓ models.orders imported")
        
        import utils
        print("✓ utils imported")
        
        import schedules
        print("✓ schedules imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database connection"""
    try:
        print("\nTesting database...")
        import asyncio
        import database
        
        async def test_db():
            # Test database connection
            result = await database.fetch("SELECT name FROM sqlite_master WHERE type='table'")
            print(f"✓ Database connected, found {len(result)} tables")
            return True
        
        return asyncio.run(test_db())
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        print("\nTesting configuration...")
        from config import config
        
        # Check if config has required sections
        required_sections = ['settings', 'delivery', 'checkout', 'payment_methods', 'info']
        for section in required_sections:
            if section in config:
                print(f"✓ {section} section found")
            else:
                print(f"❌ {section} section missing")
                return False
        
        print("✅ Configuration looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 Telegram Bot Debug Test")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("src"):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Check if config.json exists
    if not os.path.exists("config.json"):
        print("❌ config.json not found")
        return False
    
    print("✓ config.json found")
    
    # Run tests
    tests = [
        test_imports,
        test_config,
        test_database
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"Imports: {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"Config: {'✅ PASS' if results[1] else '❌ FAIL'}")
    print(f"Database: {'✅ PASS' if results[2] else '❌ FAIL'}")
    
    if all(results):
        print("\n🎉 All tests passed! Bot should work correctly.")
        print("\n📝 Next steps:")
        print("1. Set your bot token in environment variable TOKEN")
        print("2. Run: python src/__init__.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    return all(results)

if __name__ == "__main__":
    main()
