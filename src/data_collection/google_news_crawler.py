# src/data_collection/google_news_crawler.py
"""Google News RSS Crawler"""
import feedparser
import requests
from datetime import datetime
from urllib.parse import quote
import re

class GoogleNewsCrawler:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.base_url = "https://news.google.com/rss"
        
    def search_news(self, query, language='en', country='US', max_results=100):
        """Thu thập tin tức từ Google News RSS theo từ khóa"""
        articles_data = []
        
        try:
            # Build RSS URL with search query
            encoded_query = quote(query)
            rss_url = f"{self.base_url}/search?q={encoded_query}&hl={language}&gl={country}&ceid={country}:{language}"
            
            print(f"🔍 Fetching from: {rss_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print(f"⚠️  No articles found for query: {query}")
                return []
            
            for entry in feed.entries[:max_results]:
                # Extract hashtags from title and description
                text = f"{entry.title} {entry.get('summary', '')}"
                hashtags = re.findall(r'#\w+', text)
                hashtags = [tag[1:] for tag in hashtags]
                
                article_doc = {
                    'article_id': entry.get('id', entry.link),
                    'title': entry.title,
                    'text': entry.get('summary', entry.title),
                    'link': entry.link,
                    'published': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'created_at': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'source': entry.get('source', {}).get('title', 'Google News'),
                    'topic': query,
                    'hashtags': hashtags,
                    'platform': 'google_news',
                    'collected_at': datetime.now(),
                    'likes': 0,
                    'retweets': 0,
                    'replies': 0
                }
                articles_data.append(article_doc)
            
            print(f"✅ Found {len(articles_data)} articles for '{query}'")
            return articles_data
            
        except Exception as e:
            print(f"❌ Error fetching Google News: {e}")
            return []
    
    def get_topic_news(self, topic='TECHNOLOGY', language='en', country='US', max_results=100):
        """
        Thu thập tin tức theo chủ đề Google News
        Topics: WORLD, NATION, BUSINESS, TECHNOLOGY, ENTERTAINMENT, SPORTS, SCIENCE, HEALTH
        """
        try:
            rss_url = f"{self.base_url}/topics/{topic}?hl={language}&gl={country}&ceid={country}:{language}"
            
            print(f"🔍 Fetching {topic} news from Google News...")
            
            feed = feedparser.parse(rss_url)
            articles_data = []
            
            for entry in feed.entries[:max_results]:
                text = f"{entry.title} {entry.get('summary', '')}"
                hashtags = re.findall(r'#\w+', text)
                hashtags = [tag[1:] for tag in hashtags]
                
                article_doc = {
                    'article_id': entry.get('id', entry.link),
                    'title': entry.title,
                    'text': entry.get('summary', entry.title),
                    'link': entry.link,
                    'published': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'created_at': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'source': entry.get('source', {}).get('title', 'Google News'),
                    'topic': topic.lower(),
                    'hashtags': hashtags,
                    'platform': 'google_news',
                    'collected_at': datetime.now(),
                    'likes': 0,
                    'retweets': 0,
                    'replies': 0
                }
                articles_data.append(article_doc)
            
            print(f"✅ Found {len(articles_data)} {topic} articles")
            return articles_data
            
        except Exception as e:
            print(f"❌ Error fetching topic news: {e}")
            return []
    
    def save_to_mongodb(self, articles_data):
        """Lưu vào MongoDB"""
        if not articles_data:
            print("ℹ️  No articles to save")
            return
        
        new_articles = []
        for article in articles_data:
            # Check if article already exists
            existing = self.posts_collection.find_one({'article_id': article['article_id']})
            if not existing:
                new_articles.append(article)
        
        if new_articles:
            self.posts_collection.insert_many(new_articles)
            print(f"💾 Saved {len(new_articles)} new articles to MongoDB")
        else:
            print("ℹ️  No new articles to save (all duplicates)")
    
    def collect_topics(self, queries, max_results_per_query=50):
        """Thu thập dữ liệu cho nhiều chủ đề/từ khóa"""
        total_collected = 0
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"📰 Collecting: {query}")
            print(f"{'='*60}")
            
            articles = self.search_news(query, max_results=max_results_per_query)
            self.save_to_mongodb(articles)
            total_collected += len(articles)
        
        print(f"\n{'='*60}")
        print(f"✅ Total collected: {total_collected} articles")
        print(f"{'='*60}\n")