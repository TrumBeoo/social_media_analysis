# Twitter Data Collection với snscrape (không cần API key)
import snscrape.modules.twitter as sntwitter
import json
import re
from datetime import datetime, timedelta
from pymongo import MongoClient

class TwitterCrawler:
    def __init__(self):
        pass
    
    def search_tweets(self, query, max_results=100, since_date=None):
        """
        Thu thập tweets về chủ đề cụ thể bằng snscrape
        """
        tweets_data = []
        
        try:
            # Tạo query với ngày nếu có
            if since_date:
                search_query = f"{query} since:{since_date}"
            else:
                # Mặc định lấy tweets trong 7 ngày qua
                since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                search_query = f"{query} since:{since_date}"
            
            print(f"Searching: {search_query}")
            
            # Sử dụng snscrape để thu thập tweets
            tweets = sntwitter.TwitterSearchScraper(search_query).get_items()
            
            count = 0
            for tweet in tweets:
                if count >= max_results:
                    break
                
                # Extract hashtags từ text
                hashtags = re.findall(r'#\w+', tweet.content)
                hashtags = [tag[1:] for tag in hashtags]  # Bỏ dấu #
                
                tweet_doc = {
                    'tweet_id': str(tweet.id),
                    'text': tweet.content,
                    'created_at': tweet.date,
                    'likes': tweet.likeCount or 0,
                    'retweets': tweet.retweetCount or 0,
                    'replies': tweet.replyCount or 0,
                    'hashtags': hashtags,
                    'lang': tweet.lang or 'unknown',
                    'username': tweet.user.username,
                    'user_followers': tweet.user.followersCount or 0,
                    'topic': query,
                    'source': 'twitter',
                    'collected_at': datetime.now()
                }
                tweets_data.append(tweet_doc)
                count += 1
            
            return tweets_data
        
        except Exception as e:
            print(f"Error collecting tweets: {e}")
            return []
    
    def save_to_mongodb(self, tweets_data, mongo_uri):
        """Lưu vào MongoDB"""
        if tweets_data:
            client = MongoClient(mongo_uri)
            db = client['social_media_analysis']
            posts_collection = db['posts']
            
            # Kiểm tra trùng lặp trước khi insert
            new_tweets = []
            for tweet in tweets_data:
                existing = posts_collection.find_one({'tweet_id': tweet['tweet_id']})
                if not existing:
                    new_tweets.append(tweet)
            
            if new_tweets:
                posts_collection.insert_many(new_tweets)
                print(f"✅ Saved {len(new_tweets)} new tweets to MongoDB")
            else:
                print("ℹ️ No new tweets to save")

# Sử dụng
if __name__ == "__main__":
    # MongoDB URI
    MONGO_URI = "mongodb+srv://TrumBeoo:1xr1R8BRdLafRzTg@trumbeoo.c0hnfng.mongodb.net/social_media_analysis?" \
                "retryWrites=true&w=majority&appName=TrumBeoo"
    
    # Khởi tạo crawler
    crawler = TwitterCrawler()
    
    # Thu thập dữ liệu về các chủ đề
    topics = [
        "AI education",
        "trí tuệ nhân tạo giáo dục", 
        "AI học tập",
        "#AIEducation",
        "machine learning giáo dục"
    ]
    
    for topic in topics:
        print(f"🔍 Collecting tweets about: {topic}")
        tweets = crawler.search_tweets(topic, max_results=50)
        crawler.save_to_mongodb(tweets, MONGO_URI)
        print(f"Found {len(tweets)} tweets\n")