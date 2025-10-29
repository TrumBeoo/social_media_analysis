"""Reddit data collection using PRAW"""
import praw
from datetime import datetime

class RedditCrawler:
    def __init__(self, db, client_id, client_secret, user_agent):
        self.db = db
        self.posts_collection = db['posts']
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def search_posts(self, query, subreddit_name='all', limit=100):
        """Thu thập posts từ Reddit"""
        posts_data = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            for post in subreddit.search(query, limit=limit, sort='new'):
                post_doc = {
                    'post_id': post.id,
                    'title': post.title,
                    'text': post.selftext,
                    'created_at': datetime.fromtimestamp(post.created_utc),
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'upvote_ratio': post.upvote_ratio,
                    'subreddit': post.subreddit.display_name,
                    'author': str(post.author),
                    'url': post.url,
                    'topic': query,
                    'source': 'reddit',
                    'collected_at': datetime.now()
                }
                posts_data.append(post_doc)
            
            return posts_data
        
        except Exception as e:
            print(f"Error collecting Reddit posts: {e}")
            return []
    
    def save_to_mongodb(self, posts_data):
        """Lưu vào MongoDB"""
        if posts_data:
            self.posts_collection.insert_many(posts_data)
            print(f" Saved {len(posts_data)} Reddit posts to MongoDB")
    
    def collect_topics(self, topics, limit_per_topic=100):
        """Thu thập dữ liệu cho nhiều chủ đề"""
        for topic in topics:
            print(f" Collecting Reddit posts about: {topic}")
            posts = self.search_posts(topic, limit=limit_per_topic)
            self.save_to_mongodb(posts)