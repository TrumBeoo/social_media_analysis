#!/usr/bin/env python3
"""Script to delete all mock data from database"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig

def clear_mockdata():
    """Delete all mock data from database"""
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if db is None:
        print("❌ Failed to connect to database")
        return
    
    # Count existing data
    posts_count = db['posts'].count_documents({})
    sentiment_count = db['sentiment_analysis'].count_documents({})
    trends_count = db['trends'].count_documents({})
    
    print(f"📊 Current data count:")
    print(f"   Posts: {posts_count:,}")
    print(f"   Sentiment Analysis: {sentiment_count:,}")
    print(f"   Trends: {trends_count:,}")
    
    if posts_count == 0 and sentiment_count == 0 and trends_count == 0:
        print("✅ Database is already empty")
        return
    
    # Confirm deletion
    confirm = input("\n⚠️  Delete ALL data? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Operation cancelled")
        return
    
    # Delete all data
    print("\n🗑️  Deleting data...")
    
    posts_deleted = db['posts'].delete_many({})
    sentiment_deleted = db['sentiment_analysis'].delete_many({})
    trends_deleted = db['trends'].delete_many({})
    
    print(f"✅ Deleted:")
    print(f"   Posts: {posts_deleted.deleted_count:,}")
    print(f"   Sentiment Analysis: {sentiment_deleted.deleted_count:,}")
    print(f"   Trends: {trends_deleted.deleted_count:,}")
    print("\n🎯 Database cleared successfully!")

if __name__ == "__main__":
    clear_mockdata()