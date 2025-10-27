# Cell 11 Fixed - Statistical Analysis
import pandas as pd
from datetime import datetime
import numpy as np
from collections import Counter

# Load data from MongoDB
df = pd.DataFrame(list(posts_collection.find()))

class StatisticalAnalyzer:
    def __init__(self, df):
        self.df = df.copy()
        # Add day_of_week column if it doesn't exist
        if 'created_at' in self.df.columns and 'day_of_week' not in self.df.columns:
            self.df['day_of_week'] = pd.to_datetime(self.df['created_at']).dt.day_name()
    
    def get_basic_stats(self):
        """Thống kê cơ bản"""
        return {
            'total_posts': len(self.df),
            'unique_topics': self.df['topic'].nunique() if 'topic' in self.df.columns else 0,
            'date_range': {
                'start': str(self.df['created_at'].min()) if 'created_at' in self.df.columns else None,
                'end': str(self.df['created_at'].max()) if 'created_at' in self.df.columns else None
            }
        }
    
    def get_sentiment_stats(self):
        """Thống kê cảm xúc"""
        if 'sentiment' not in self.df.columns:
            return {'error': 'No sentiment data available'}
        
        sentiment_counts = self.df['sentiment'].value_counts()
        total = len(self.df)
        
        return {
            'distribution': sentiment_counts.to_dict(),
            'percentages': (sentiment_counts / total * 100).round(2).to_dict(),
            'avg_sentiment_score': float(self.df['sentiment_score'].mean()) if 'sentiment_score' in self.df.columns else None
        }
    
    def get_engagement_stats(self):
        """Thống kê tương tác"""
        engagement_cols = ['likes', 'retweets', 'replies', 'score']
        stats = {}
        
        for col in engagement_cols:
            if col in self.df.columns:
                stats[col] = {
                    'mean': float(self.df[col].mean()),
                    'median': float(self.df[col].median()),
                    'max': int(self.df[col].max()),
                    'min': int(self.df[col].min())
                }
        
        return stats
    
    def get_time_analysis(self):
        """Phân tích theo thời gian"""
        if 'created_at' not in self.df.columns:
            return {'error': 'No time data available'}
        
        # Ensure day_of_week exists
        if 'day_of_week' not in self.df.columns:
            self.df['day_of_week'] = pd.to_datetime(self.df['created_at']).dt.day_name()
        
        return {
            'posts_by_day': self.df['day_of_week'].value_counts().to_dict(),
            'posts_by_hour': pd.to_datetime(self.df['created_at']).dt.hour.value_counts().to_dict()
        }
    
    def get_top_hashtags(self, limit=10):
        """Top hashtags"""
        if 'hashtags' not in self.df.columns:
            return []
        
        all_hashtags = []
        for hashtags in self.df['hashtags'].dropna():
            if isinstance(hashtags, list):
                all_hashtags.extend(hashtags)
        
        return Counter(all_hashtags).most_common(limit)
    
    def generate_comprehensive_report(self):
        """Tạo báo cáo thống kê toàn diện"""
        report = {
            'basic_stats': self.get_basic_stats(),
            'sentiment_stats': self.get_sentiment_stats(),
            'time_analysis': self.get_time_analysis(),
            'engagement_stats': self.get_engagement_stats(),
            'top_hashtags': self.get_top_hashtags(),
            'generated_at': datetime.now()
        }
        return report

# Tạo báo cáo
stat_analyzer = StatisticalAnalyzer(df)
comprehensive_report = stat_analyzer.generate_comprehensive_report()

# In báo cáo
print("📊 COMPREHENSIVE SOCIAL MEDIA ANALYSIS REPORT")
print("=" * 50)

print(f"\n📈 Basic Statistics:")
basic = comprehensive_report['basic_stats']
print(f"Total Posts: {basic['total_posts']}")
print(f"Unique Topics: {basic['unique_topics']}")
print(f"Date Range: {basic['date_range']['start']} to {basic['date_range']['end']}")

print(f"\n💭 Sentiment Analysis:")
sentiment = comprehensive_report['sentiment_stats']
if 'error' not in sentiment:
    print("Distribution:")
    for sentiment_type, count in sentiment['distribution'].items():
        pct = sentiment['percentages'][sentiment_type]
        print(f"  {sentiment_type.title()}: {count} posts ({pct}%)")
    print(f"Average Sentiment Score: {sentiment['avg_sentiment_score']:.3f}")

print(f"\n📅 Time Analysis:")
time_analysis = comprehensive_report['time_analysis']
if 'error' not in time_analysis:
    print("Posts by Day of Week:")
    for day, count in sorted(time_analysis['posts_by_day'].items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"  {day}: {count} posts")

print(f"\n🔥 Top Hashtags:")
for hashtag, count in comprehensive_report['top_hashtags'][:5]:
    print(f"  #{hashtag}: {count} mentions")

print(f"\n📊 Engagement Statistics:")
engagement = comprehensive_report['engagement_stats']
for metric, stats in engagement.items():
    print(f"  {metric.title()}:")
    print(f"    Average: {stats['mean']:.2f}")
    print(f"    Max: {stats['max']}")

print("\n✅ Analysis completed successfully!")