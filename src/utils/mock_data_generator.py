"""Mock data generator for testing"""
import random
from datetime import datetime, timedelta

class MockDataGenerator:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.topics = ["AI trong giáo dục", "trí tuệ nhân tạo", "học máy", "EdTech"]
        self.hashtags = [
            "AIEducation", "EdTech", "MachineLearning", "DeepLearning",
            "GiáoDục", "HọcTậpAI", "TríTuệNhânTạo", "CôngNghệGiáoDục"
        ]
        self.positive_words = [
            "tuyệt vời", "hiệu quả", "hữu ích", "tiện lợi", "sáng tạo",
            "amazing", "excellent", "great", "helpful", "innovative"
        ]
        self.negative_words = [
            "khó", "phức tạp", "tốn kém", "lo ngại", "rủi ro",
            "difficult", "complex", "expensive", "worried", "risk"
        ]
        self.neutral_words = [
            "nghiên cứu", "phát triển", "ứng dụng", "thảo luận",
            "research", "development", "application", "discussion"
        ]
    
    def generate_post(self, sentiment_type='mixed'):
        """Tạo post giả lập"""
        if sentiment_type == 'positive':
            words = self.positive_words
        elif sentiment_type == 'negative':
            words = self.negative_words
        else:
            words = self.positive_words + self.negative_words + self.neutral_words
        
        text = f"{random.choice(self.topics)} {random.choice(words)} " \
               f"trong {random.choice(['lớp học', 'trường học', 'đại học', 'khóa học'])}. " \
               f"#{random.choice(self.hashtags)} #{random.choice(self.hashtags)}"
        
        days_ago = random.randint(0, 90)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        return {
            'text': text,
            'created_at': created_at,
            'likes': random.randint(0, 1000),
            'retweets': random.randint(0, 500),
            'replies': random.randint(0, 200),
            'hashtags': random.sample(self.hashtags, random.randint(1, 3)),
            'topic': random.choice(self.topics),
            'source': 'mock_data',
            'collected_at': datetime.now()
        }
    
    def generate_dataset(self, num_posts=1000):
        """Tạo dataset với tỷ lệ cảm xúc cân bằng"""
        posts = []
        
        # 40% positive, 30% negative, 30% neutral
        for _ in range(int(num_posts * 0.4)):
            posts.append(self.generate_post('positive'))
        
        for _ in range(int(num_posts * 0.3)):
            posts.append(self.generate_post('negative'))
        
        for _ in range(int(num_posts * 0.3)):
            posts.append(self.generate_post('mixed'))
        
        return posts
    
    def save_to_mongodb(self, posts):
        """Lưu vào MongoDB"""
        if posts:
            self.posts_collection.insert_many(posts)
            print(f"✅ Generated and saved {len(posts)} mock posts")
    
    def generate_and_save(self, num_posts=1000):
        """Tạo và lưu dữ liệu mẫu"""
        mock_posts = self.generate_dataset(num_posts)
        self.save_to_mongodb(mock_posts)
        
        print(f"\n📊 Total posts in database: {self.posts_collection.count_documents({})}")