"""Twitter data collection using snscrape"""
import snscrape.modules.twitter as sntwitter
import re
from datetime import datetime, timedelta

class TwitterCrawler:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
    
    def search_tweets(self, query, max_results=100, since_date=None):
        """Thu thập tweets về chủ đề cụ thể bằng snscrape"""
        tweets_data = []
        
        try:
            if since_date:
                search_query = f"{query} since:{since_date}"
            else:
                since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                search_query = f"{query} since:{since_date}"
            
            print(f"Searching: {search_query}")
            
            tweets = sntwitter.TwitterSearchScraper(search_query).get_items()
            
            count = 0
            for tweet in tweets:
                if count >= max_results:
                    break
                
                hashtags = re.findall(r'#\w+', tweet.content)
                hashtags = [tag[1:] for tag in hashtags]
                
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
    
    def save_to_mongodb(self, tweets_data):
        """Lưu vào MongoDB"""
        if tweets_data:
            new_tweets = []
            for tweet in tweets_data:
                existing = self.posts_collection.find_one({'tweet_id': tweet['tweet_id']})
                if not existing:
                    new_tweets.append(tweet)
            
            if new_tweets:
                self.posts_collection.insert_many(new_tweets)
                print(f" Saved {len(new_tweets)} new tweets to MongoDB")
            else:
                print("ℹ No new tweets to save")
    
    def collect_topics(self, topics, max_results_per_topic=50):
        """Thu thập dữ liệu cho nhiều chủ đề"""
        for topic in topics:
            print(f" Collecting tweets about: {topic}")
            tweets = self.search_tweets(topic, max_results=max_results_per_topic)
            self.save_to_mongodb(tweets)
            print(f"Found {len(tweets)} tweets\n")