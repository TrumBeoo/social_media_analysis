"""Main application entry point"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig
from data_collection.twitter_crawler import TwitterCrawler
from data_collection.reddit_crawler import RedditCrawler
from analysis.sentiment_analyzer import SentimentAnalyzer
from analysis.trend_analyzer import TrendAnalyzer
from analysis.advanced_analyzer import AdvancedAnalyzer
from utils.mock_data_generator import MockDataGenerator
from utils.report_exporter import ReportExporter
from dashboard.dash_app import DashboardApp

def main():
    """Main application workflow"""
    print("Starting Social Media Analysis Application")
    
    # 1. Database Connection
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if db is None:
        print(" Failed to connect to database. Exiting...")
        return
    
    # 2. Data Collection
    print("\nData Collection Phase")
    
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
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    reddit_topics = ["AI education", "artificial intelligence learning", "EdTech"]
    reddit_crawler.collect_topics(reddit_topics, limit_per_topic=100)
    
    # Generate mock data for testing
    mock_generator = MockDataGenerator(db)
    mock_generator.generate_and_save(1000)
    
    # 3. Analysis Phase
    print("\nAnalysis Phase")
    
    # Sentiment Analysis
    sentiment_analyzer = SentimentAnalyzer(db)
    sentiment_analyzer.analyze_all_posts()
    
    # Trend Analysis
    trend_analyzer = TrendAnalyzer(db)
    topic_analysis = trend_analyzer.analyze_by_topic()
    print("\nSentiment Analysis by Topic:")
    print(topic_analysis)
    trend_analyzer.generate_report()
    
    # Advanced Analysis
    advanced_analyzer = AdvancedAnalyzer(db)
    advanced_analyzer.generate_advanced_report()
    
    # 4. Export Results
    print("\nExport Phase")
    exporter = ReportExporter(db)
    exporter.export_to_csv()
    
    # Create comprehensive report data
    report_data = {
        'topic_analysis': topic_analysis.to_dict('records') if not topic_analysis.empty else [],
        'hashtag_analysis': dict(trend_analyzer.get_top_hashtags()),
        'engagement_stats': trend_analyzer.get_engagement_stats()
    }
    
    exporter.export_to_json(report_data)
    exporter.create_presentation_summary(report_data)
    
    # 5. Dashboard
    print("\n Dashboard Phase")
    dashboard = DashboardApp(db)
    
    print("\nAnalysis completed successfully!")
    print("Choose an option:")
    print("1. Run Dashboard")
    print("2. Crawl URL")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        dashboard.run(debug=True, port=8050)
    elif choice == "2":
        url = input("Enter URL to crawl: ")
        topic = input("Enter topic (optional): ")
        
        from data_collection.url_crawler import URLCrawler
        crawler = URLCrawler(db)
        post_id = crawler.crawl_url(url, topic or None)
        
        if post_id:
            sentiment_analyzer.analyze_all_posts()
            print(f"URL crawled and analyzed! Post ID: {post_id}")
    elif choice == "3":
        print("Goodbye!")

if __name__ == "__main__":
    main()