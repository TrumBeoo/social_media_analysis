"""Trend analysis and statistics"""
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta
import re

class TrendAnalyzer:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.trends_collection = db['trends']
        try:
            posts_data = list(self.posts_collection.find())
            self.df = pd.DataFrame(posts_data)
            
            # Ensure date columns are properly formatted
            if not self.df.empty:
                if 'created_at' in self.df.columns:
                    self.df['created_at'] = pd.to_datetime(self.df['created_at'], errors='coerce')
                elif 'date' in self.df.columns:
                    self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        except Exception as e:
            print(f"Error loading data in TrendAnalyzer: {e}")
            self.df = pd.DataFrame()
    
    def get_top_hashtags(self, limit=10):
        """Lấy top hashtags phổ biến"""
        all_hashtags = []
        
        if 'hashtags' in self.df.columns:
            for hashtags in self.df['hashtags'].dropna():
                if isinstance(hashtags, list):
                    all_hashtags.extend(hashtags)
        else:
            for text in self.df['text'].dropna():
                hashtags = re.findall(r'#\w+', str(text))
                hashtags = [tag[1:] for tag in hashtags]
                all_hashtags.extend(hashtags)
        
        if not all_hashtags:
            return [("No hashtags found", 0)]
        
        hashtag_counts = Counter(all_hashtags)
        return hashtag_counts.most_common(limit)
    
    def get_sentiment_trend(self, days=30):
        """Phân tích xu hướng cảm xúc theo thời gian"""
        if self.df.empty:
            return pd.DataFrame()
        
        # Check if we have date column or created_at column
        date_col = None
        if 'created_at' in self.df.columns:
            date_col = 'created_at'
        elif 'date' in self.df.columns:
            date_col = 'date'
        else:
            return pd.DataFrame()
        
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
            self.df[date_col] = pd.to_datetime(self.df[date_col], errors='coerce')
        
        recent_date = datetime.now() - timedelta(days=days)
        recent_posts = self.df[self.df[date_col] >= recent_date]
        
        if recent_posts.empty or 'sentiment' not in recent_posts.columns:
            return pd.DataFrame()
        
        recent_posts = recent_posts.copy()
        recent_posts['date'] = recent_posts[date_col].dt.date
        
        try:
            daily_sentiment = recent_posts.groupby([
                'date', 'sentiment'
            ]).size().unstack(fill_value=0)
            return daily_sentiment
        except KeyError as e:
            print(f"KeyError in sentiment trend analysis: {e}")
            return pd.DataFrame()
    
    def get_engagement_stats(self):
        """Thống kê engagement"""
        stats = {
            'avg_likes': self.df['likes'].mean() if 'likes' in self.df.columns else 0,
            'avg_retweets': self.df['retweets'].mean() if 'retweets' in self.df.columns else 0,
            'avg_replies': self.df['replies'].mean() if 'replies' in self.df.columns else 0,
            'avg_score': self.df['score'].mean() if 'score' in self.df.columns else 0,
            'total_posts': len(self.df),
            'sentiment_distribution': self.df['sentiment'].value_counts().to_dict() if 'sentiment' in self.df.columns else {}
        }
        return stats
    
    def analyze_by_topic(self):
        """Phân tích cảm xúc theo từng chủ đề"""
        pipeline = [
            {
                '$group': {
                    '_id': '$topic',
                    'total_posts': {'$sum': 1},
                    'positive': {
                        '$sum': {'$cond': [{'$eq': ['$sentiment', 'positive']}, 1, 0]}
                    },
                    'negative': {
                        '$sum': {'$cond': [{'$eq': ['$sentiment', 'negative']}, 1, 0]}
                    },
                    'neutral': {
                        '$sum': {'$cond': [{'$eq': ['$sentiment', 'neutral']}, 1, 0]}
                    },
                    'avg_sentiment_score': {'$avg': '$sentiment_score'},
                    'avg_likes': {'$avg': '$likes'}
                }
            },
            {'$sort': {'total_posts': -1}}
        ]
        
        results = list(self.posts_collection.aggregate(pipeline))
        
        df = pd.DataFrame(results)
        if not df.empty:
            df['positive_pct'] = (df['positive'] / df['total_posts'] * 100).round(2)
            df['negative_pct'] = (df['negative'] / df['total_posts'] * 100).round(2)
            df['neutral_pct'] = (df['neutral'] / df['total_posts'] * 100).round(2)
        
        return df
    
    def save_trends_to_db(self):
        """Lưu kết quả phân tích vào database"""
        trends_data = {
            'analysis_date': datetime.now(),
            'top_hashtags': dict(self.get_top_hashtags()),
            'engagement_stats': self.get_engagement_stats(),
            'total_posts_analyzed': len(self.df)
        }
        
        self.trends_collection.delete_many({})
        self.trends_collection.insert_one(trends_data)
        print("Trends analysis saved to database")
    
    def generate_report(self):
        """Tạo báo cáo tổng hợp"""
        print("\n🔥 Top 10 Hashtags:")
        for hashtag, count in self.get_top_hashtags(10):
            print(f"#{hashtag}: {count} mentions")
        
        print("\n📊 Engagement Statistics:")
        stats = self.get_engagement_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
        
        self.save_trends_to_db()