"""Database configuration and connection"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.MONGO_URI = os.getenv('MONGO_URI')
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            client = MongoClient(self.MONGO_URI)
            db = client['social_media_analysis']
            
            # Create collections
            posts_collection = db['posts']
            analysis_collection = db['sentiment_analysis']
            trends_collection = db['trends']
            
            # Create indexes
            posts_collection.create_index([("created_at", -1)])
            posts_collection.create_index([("hashtags", 1)])
            posts_collection.create_index([("topic", 1)])
            
            print("MongoDB connected successfully!")
            return db
            
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return None