"""Sentiment analysis for Vietnamese and English text"""
from underthesea import sentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from datetime import datetime

class SentimentAnalyzer:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.vader = SentimentIntensityAnalyzer()
        
        self.vietnamese_positive = [
            'tốt', 'hay', 'tuyệt', 'hiệu quả', 'hữu ích', 'tiện lợi', 
            'sáng tạo', 'xuất sắc', 'hoàn hảo', 'thú vị'
        ]
        self.vietnamese_negative = [
            'xấu', 'kém', 'tệ', 'khó', 'phức tạp', 'lo ngại', 
            'rủi ro', 'nguy hiểm', 'thất bại', 'không tốt'
        ]
    
    def clean_text(self, text):
        """Làm sạch text"""
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().strip()
    
    def analyze_vietnamese(self, text):
        """Phân tích cảm xúc tiếng Việt"""
        cleaned_text = self.clean_text(text)
        
        positive_count = sum(1 for word in self.vietnamese_positive if word in cleaned_text)
        negative_count = sum(1 for word in self.vietnamese_negative if word in cleaned_text)
        
        try:
            underthesea_result = sentiment(text)
            if underthesea_result == 'positive':
                base_score = 0.6
            elif underthesea_result == 'negative':
                base_score = -0.6
            else:
                base_score = 0.0
        except:
            base_score = 0.0
        
        score = base_score + (positive_count * 0.1) - (negative_count * 0.1)
        score = max(-1, min(1, score))
        
        if score >= 0.2:
            label = 'positive'
        elif score <= -0.2:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'score': round(score, 3),
            'label': label,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def analyze_english(self, text):
        """Phân tích cảm xúc tiếng Anh"""
        vader_scores = self.vader.polarity_scores(text)
        compound_score = vader_scores['compound']
        
        if compound_score >= 0.05:
            label = 'positive'
        elif compound_score <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'score': round(compound_score, 3),
            'label': label,
            'vader_scores': vader_scores
        }
    
    def analyze(self, text, lang='auto'):
        """Phân tích tự động dựa vào ngôn ngữ"""
        if lang == 'auto':
            if any(ord(char) > 127 for char in text):
                lang = 'vi'
            else:
                lang = 'en'
        
        if lang == 'vi':
            return self.analyze_vietnamese(text)
        else:
            return self.analyze_english(text)
    
    def analyze_all_posts(self):
        """Phân tích cảm xúc cho tất cả posts trong database"""
        posts = self.posts_collection.find({'sentiment': {'$exists': False}})
        count = 0
        
        for post in posts:
            sentiment_result = self.analyze(post.get('text', ''))
            
            self.posts_collection.update_one(
                {'_id': post['_id']},
                {'$set': {
                    'sentiment': sentiment_result['label'],
                    'sentiment_score': sentiment_result['score'],
                    'analyzed_at': datetime.now()
                }}
            )
            count += 1
            
            if count % 100 == 0:
                print(f"Analyzed {count} posts...")
        
        print(f"✅ Completed sentiment analysis for {count} posts")