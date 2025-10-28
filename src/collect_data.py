"""Quick script to run only data collection"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig
from data_collection.twitter_crawler import TwitterCrawler
from data_collection.reddit_crawler import RedditCrawler
from utils.mock_data_generator import MockDataGenerator

def main():
    print("🚀 Starting Data Collection Only...")
    
    # Connect to database
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if not db:
        print("❌ Failed to connect to database. Exiting...")
        return
    
    print("\n📊 Data Collection Phase")
    
    # Twitter data collection
    twitter_crawler = TwitterCrawler(db)
    twitter_topics = [
        "AI education",
        "trí tuệ nhân tạo giáo dục", 
        "AI học tập",
        "#AIEducation",
        "machine learning giáo dục"
    ]
    twitter_crawler.collect_topics(twitter_topics, max_results_per_topic=50)
    
    # Reddit data collection
    reddit_crawler = RedditCrawler(
        db=db,
        client_id="k6ozqL3mwwC0cGNUSmcdlQ",
        client_secret="JR6XLrrWpp2oNi5RNk0uV2GrrCaelw",
        user_agent="windows:ai-trend-collector:v1.0 (by /u/trung_it)"
    )
    reddit_topics = ["AI education", "artificial intelligence learning", "EdTech"]
    reddit_crawler.collect_topics(reddit_topics, limit_per_topic=100)
    
    # Generate mock data for testing
    mock_generator = MockDataGenerator(db)
    mock_generator.generate_and_save(1000)
    
    print("\n✅ Data collection completed!")

if __name__ == "__main__":
    main()