# src/collect_data.py (CẬP NHẬT)
"""Quick script to run only data collection"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig
from data_collection.google_news_crawler import GoogleNewsCrawler
from data_collection.reddit_crawler import RedditCrawler
from data_collection.medium_crawler import MediumCrawler
from data_collection.stackoverflow_crawler import StackOverflowCrawler
from data_collection.hackernews_crawler import HackerNewsCrawler

def main():
    print("\n" + "="*80)
    print("🚀 SOCIAL MEDIA DATA COLLECTION - MULTI-SOURCE")
    print("="*80 + "\n")
    
    # Connect to database
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if not db:
        print("❌ Failed to connect to database. Exiting...")
        return
    
    # Define topics for AI in Education
    ai_education_topics = [
        "AI in education",
        "artificial intelligence education",
        "machine learning education",
        "AI learning tools",
        "EdTech AI",
        "personalized learning AI"
    ]
    
    print("\n📊 DATA COLLECTION PHASE\n")
    
    # 1. Google News Collection
    print("\n" + "="*80)
    print("📰 GOOGLE NEWS COLLECTION")
    print("="*80)
    google_crawler = GoogleNewsCrawler(db)
    
    # Search for AI education topics
    google_crawler.collect_topics(ai_education_topics, max_results_per_query=30)
    
    # Get TECHNOLOGY topic news
    tech_articles = google_crawler.get_topic_news('TECHNOLOGY', max_results=50)
    google_crawler.save_to_mongodb(tech_articles)
    
    # Get SCIENCE topic news
    science_articles = google_crawler.get_topic_news('SCIENCE', max_results=30)
    google_crawler.save_to_mongodb(science_articles)
    
    # 2. Medium Collection
    print("\n" + "="*80)
    print("📝 MEDIUM COLLECTION")
    print("="*80)
    medium_crawler = MediumCrawler(db)
    
    medium_tags = [
        "artificial-intelligence",
        "machine-learning",
        "education-technology",
        "ai-education",
        "edtech"
    ]
    medium_crawler.collect_topics(medium_tags, max_results_per_tag=30)
    
    # 3. Stack Overflow Collection
    print("\n" + "="*80)
    print("💻 STACK OVERFLOW COLLECTION")
    print("="*80)
    stackoverflow_crawler = StackOverflowCrawler(db)
    
    stackoverflow_tags = [
        "machine-learning",
        "artificial-intelligence",
        "deep-learning",
        "nlp",
        "tensorflow",
        "pytorch"
    ]
    stackoverflow_crawler.collect_topics(stackoverflow_tags, max_results_per_tag=50)
    
    # 4. Hacker News Collection
    print("\n" + "="*80)
    print("🚀 HACKER NEWS COLLECTION")
    print("="*80)
    hackernews_crawler = HackerNewsCrawler(db)
    
    hn_queries = [
        "AI education",
        "machine learning education",
        "EdTech",
        "online learning",
        "educational technology"
    ]
    hackernews_crawler.collect_topics(hn_queries, max_results_per_query=30)
    
    # Get top stories
    top_stories = hackernews_crawler.get_top_stories(max_results=50)
    hackernews_crawler.save_to_mongodb(top_stories)
    
    # 5. Reddit Collection
    print("\n" + "="*80)
    print("🔴 REDDIT COLLECTION")
    print("="*80)
    reddit_crawler = RedditCrawler(
        db=db,
        client_id=os.getenv('REDDIT_CLIENT_ID', 'k6ozqL3mwwC0cGNUSmcdlQ'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET', 'JR6XLrrWpp2oNi5RNk0uV2GrrCaelw'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'windows:ai-trend-collector:v2.0')
    )
    
    reddit_topics = [
        "AI education",
        "artificial intelligence learning",
        "EdTech",
        "machine learning",
        "online education"
    ]
    reddit_crawler.collect_topics(reddit_topics, limit_per_topic=50)
    
    # Summary
    print("\n" + "="*80)
    print("✅ DATA COLLECTION COMPLETED")
    print("="*80)
    
    total_posts = db['posts'].count_documents({})
    print(f"\n📊 Total posts in database: {total_posts:,}")
    
    # Show breakdown by platform
    pipeline = [
        {'$group': {'_id': '$platform', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    
    platform_stats = list(db['posts'].aggregate(pipeline))
    
    if platform_stats:
        print("\n📈 Posts by Platform:")
        print("-" * 40)
        for stat in platform_stats:
            platform = stat['_id'] or 'unknown'
            count = stat['count']
            print(f"  {platform:20s}: {count:,}")
    
    print("\n" + "="*80)
    print("💡 Next Steps:")
    print("   1. Run 'python src/analyze_data.py' to analyze sentiment")
    print("   2. Run 'python src/run_dashboard.py' to view dashboard")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()