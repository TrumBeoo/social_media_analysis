# src/main.py (CẬP NHẬT)
"""Main application entry point - Updated without Twitter & MockData"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig
from data_collection.google_news_crawler import GoogleNewsCrawler
from data_collection.reddit_crawler import RedditCrawler
from data_collection.medium_crawler import MediumCrawler
from data_collection.stackoverflow_crawler import StackOverflowCrawler
from data_collection.hackernews_crawler import HackerNewsCrawler
from analysis.sentiment_analyzer import SentimentAnalyzer
from analysis.trend_analyzer import TrendAnalyzer
from analysis.advanced_analyzer import AdvancedAnalyzer
from utils.report_exporter import ReportExporter
from dashboard.dash_app import DashboardApp

def main():
    """Main application workflow"""
    print("\n" + "="*80)
    print("🎯 SOCIAL MEDIA ANALYSIS APPLICATION - Multi-Source")
    print("="*80 + "\n")
    
    # 1. Database Connection
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if db is None:
        print("❌ Failed to connect to database. Exiting...")
        return
    
    # Check existing data
    existing_posts = db['posts'].count_documents({})
    print(f"📊 Current posts in database: {existing_posts:,}\n")
    
    # Menu
    print("Choose an option:")
    print("1. Collect Data (All Sources)")
    print("2. Analyze Data")
    print("3. Run Dashboard")
    print("4. Full Pipeline (Collect + Analyze + Dashboard)")
    print("5. Crawl Single URL")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        collect_data(db)
    elif choice == "2":
        analyze_data(db)
    elif choice == "3":
        run_dashboard(db)
    elif choice == "4":
        collect_data(db)
        analyze_data(db)
        run_dashboard(db)
    elif choice == "5":
        crawl_url(db)
    elif choice == "6":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice!")

def collect_data(db):
    """Data collection from all sources"""
    print("\n" + "="*80)
    print("📊 DATA COLLECTION PHASE")
    print("="*80 + "\n")
    
    ai_education_topics = [
        "AI in education",
        "artificial intelligence education",
        "machine learning education",
        "AI learning tools"
    ]
    
    # Google News
    print("\n📰 Collecting from Google News...")
    google_crawler = GoogleNewsCrawler(db)
    google_crawler.collect_topics(ai_education_topics[:2], max_results_per_query=30)
    
    # Medium
    print("\n📝 Collecting from Medium...")
    medium_crawler = MediumCrawler(db)
    medium_crawler.collect_topics(['artificial-intelligence', 'machine-learning', 'education-technology'], max_results_per_tag=20)
    
    # Stack Overflow
    print("\n💻 Collecting from Stack Overflow...")
    stackoverflow_crawler = StackOverflowCrawler(db)
    stackoverflow_crawler.collect_topics(['machine-learning', 'artificial-intelligence'], max_results_per_tag=30)
    
    # Hacker News
    print("\n🚀 Collecting from Hacker News...")
    hackernews_crawler = HackerNewsCrawler(db)
    hackernews_crawler.collect_topics(['AI education', 'EdTech'], max_results_per_query=20)
    
    # Reddit
    print("\n🔴 Collecting from Reddit...")
    reddit_crawler = RedditCrawler(
        db=db,
        client_id=os.getenv('REDDIT_CLIENT_ID', 'k6ozqL3mwwC0cGNUSmcdlQ'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET', 'JR6XLrrWpp2oNi5RNk0uV2GrrCaelw'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'windows:ai-trend-collector:v2.0')
    )
    reddit_crawler.collect_topics(['AI education', 'EdTech'], limit_per_topic=30)
    
    total_posts = db['posts'].count_documents({})
    print(f"\n✅ Collection completed! Total posts: {total_posts:,}")

def analyze_data(db):
    """Data analysis"""
    print("\n" + "="*80)
    print("🔍 ANALYSIS PHASE")
    print("="*80 + "\n")
    
    # Sentiment Analysis
    print("💭 Running sentiment analysis...")
    sentiment_analyzer = SentimentAnalyzer(db)
    sentiment_analyzer.analyze_all_posts()
    
    # Trend Analysis
    print("\n📈 Running trend analysis...")
    trend_analyzer = TrendAnalyzer(db)
    topic_analysis = trend_analyzer.analyze_by_topic()
    
    if not topic_analysis.empty:
        print("\n📊 Sentiment Analysis by Topic:")
        print(topic_analysis.to_string())
    
    trend_analyzer.generate_report()
    
    # Advanced Analysis
    print("\n🔬 Running advanced analysis...")
    advanced_analyzer = AdvancedAnalyzer(db)
    advanced_analyzer.generate_advanced_report()
    
    # Export Results
    print("\n📤 Exporting results...")
    exporter = ReportExporter(db)
    exporter.export_to_csv()
    
    report_data = {
        'topic_analysis': topic_analysis.to_dict('records') if not topic_analysis.empty else [],
        'hashtag_analysis': dict(trend_analyzer.get_top_hashtags()),
        'engagement_stats': trend_analyzer.get_engagement_stats()
    }
    
    exporter.export_to_json(report_data)
    exporter.create_presentation_summary(report_data)
    
    print("\n✅ Analysis completed!")

def run_dashboard(db):
    """Run dashboard"""
    print("\n" + "="*80)
    print("📊 DASHBOARD PHASE")
    print("="*80 + "\n")
    
    dashboard = DashboardApp(db)
    dashboard.run(debug=True, port=8055)

def crawl_url(db):
    """Crawl single URL"""
    from data_collection.url_crawler import URLCrawler
    
    url = input("\nEnter URL to crawl: ").strip()
    topic = input("Enter topic (optional): ").strip()
    
    if not url:
        print("❌ No URL provided!")
        return
    
    crawler = URLCrawler(db)
    post_id = crawler.crawl_url(url, topic or None)
    
    if post_id:
        print(f"\n✅ URL crawled successfully! Post ID: {post_id}")
        
        # Analyze sentiment
        sentiment_analyzer = SentimentAnalyzer(db)
        sentiment_analyzer.analyze_all_posts()
        
        print("✅ Sentiment analysis completed!")
    else:
        print("\n❌ Failed to crawl URL!")

if __name__ == "__main__":
    main()