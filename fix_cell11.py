# Fix for cell 11 - Statistical Analysis
import pandas as pd
from datetime import datetime
import numpy as np

class StatisticalAnalyzer:
    def __init__(self, df):
        self.df = df
        # Add day_of_week column if it doesn't exist
        if 'created_at' in df.columns and 'day_of_week' not in df.columns:
            self.df['day_of_week'] = pd.to_datetime(df['created_at']).dt.day_name()
    
    def get_basic_stats(self):
        """Thống kê cơ bản"""
        return {
            'total_posts': len(self.df),
            'unique_topics': self.df['topic'].nunique() if 'topic' in self.df.columns else 0,
            'date_range': {
                'start': self.df['created_at'].min() if 'created_at' in self.df.columns else None,
                'end': self.df['created_at'].max() if 'created_at' in self.df.columns else None
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
            'avg_sentiment_score': self.df['sentiment_score'].mean() if 'sentiment_score' in self.df.columns else None
        }
    
    def get_engagement_stats(self):
        """Thống kê tương tác"""
        engagement_cols = ['likes', 'retweets', 'replies', 'score']
        stats = {}
        
        for col in engagement_cols:
            if col in self.df.columns:
                stats[col] = {
                    'mean': self.df[col].mean(),
                    'median': self.df[col].median(),
                    'max': self.df[col].max(),
                    'min': self.df[col].min()
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
        
        from collections import Counter
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

print("Fixed StatisticalAnalyzer class created successfully!")