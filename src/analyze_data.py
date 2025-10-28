"""Quick script to run only data analysis"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig
from analysis.sentiment_analyzer import SentimentAnalyzer
from analysis.trend_analyzer import TrendAnalyzer
from analysis.advanced_analyzer import AdvancedAnalyzer
from utils.report_exporter import ReportExporter

def main():
    print("🚀 Starting Data Analysis Only...")
    
    # Connect to database
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if db is None:
        print("❌ Failed to connect to database. Exiting...")
        return
    
    print("\n🔍 Analysis Phase")
    
    # Sentiment Analysis
    sentiment_analyzer = SentimentAnalyzer(db)
    sentiment_analyzer.analyze_all_posts()
    
    # Trend Analysis
    trend_analyzer = TrendAnalyzer(db)
    topic_analysis = trend_analyzer.analyze_by_topic()
    print("\n📊 Sentiment Analysis by Topic:")
    print(topic_analysis)
    trend_analyzer.generate_report()
    
    # Advanced Analysis
    advanced_analyzer = AdvancedAnalyzer(db)
    advanced_analyzer.generate_advanced_report()
    
    # Export Results
    print("\n📤 Export Phase")
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
    
    print("\n✅ Analysis completed successfully!")

if __name__ == "__main__":
    main()