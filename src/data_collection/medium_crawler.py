# src/data_collection/medium_crawler.py
"""Medium RSS Crawler"""
import feedparser
from datetime import datetime
import re
from bs4 import BeautifulSoup

class MediumCrawler:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
    
    def get_tag_feed(self, tag, max_results=50):
        """Thu thập bài viết từ Medium tag"""
        try:
            rss_url = f"https://medium.com/feed/tag/{tag}"
            print(f"🔍 Fetching Medium articles for tag: {tag}")
            
            feed = feedparser.parse(rss_url)
            articles_data = []
            
            for entry in feed.entries[:max_results]:
                # Clean HTML from content
                soup = BeautifulSoup(entry.get('summary', ''), 'html.parser')
                clean_text = soup.get_text(separator=' ', strip=True)
                
                # Extract hashtags
                hashtags = re.findall(r'#\w+', clean_text)
                hashtags = [tag[1:] for tag in hashtags]
                
                article_doc = {
                    'article_id': entry.get('id', entry.link),
                    'title': entry.title,
                    'text': clean_text[:2000],  # Limit text length
                    'link': entry.link,
                    'published': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'created_at': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'author': entry.get('author', 'Unknown'),
                    'source': 'Medium',
                    'topic': tag,
                    'hashtags': hashtags,
                    'platform': 'medium',
                    'collected_at': datetime.now(),
                    'likes': 0,
                    'num_comments': 0
                }
                articles_data.append(article_doc)
            
            print(f"✅ Found {len(articles_data)} Medium articles for '{tag}'")
            return articles_data
            
        except Exception as e:
            print(f"❌ Error fetching Medium articles: {e}")
            return []
    
    def get_publication_feed(self, publication, max_results=50):
        """Thu thập bài viết từ Medium publication"""
        try:
            rss_url = f"https://medium.com/feed/{publication}"
            print(f"🔍 Fetching from Medium publication: {publication}")
            
            feed = feedparser.parse(rss_url)
            articles_data = []
            
            for entry in feed.entries[:max_results]:
                soup = BeautifulSoup(entry.get('summary', ''), 'html.parser')
                clean_text = soup.get_text(separator=' ', strip=True)
                
                hashtags = re.findall(r'#\w+', clean_text)
                hashtags = [tag[1:] for tag in hashtags]
                
                article_doc = {
                    'article_id': entry.get('id', entry.link),
                    'title': entry.title,
                    'text': clean_text[:2000],
                    'link': entry.link,
                    'published': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'created_at': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'author': entry.get('author', 'Unknown'),
                    'source': f'Medium - {publication}',
                    'topic': publication,
                    'hashtags': hashtags,
                    'platform': 'medium',
                    'collected_at': datetime.now(),
                    'likes': 0,
                    'num_comments': 0
                }
                articles_data.append(article_doc)
            
            print(f"✅ Found {len(articles_data)} articles from '{publication}'")
            return articles_data
            
        except Exception as e:
            print(f"❌ Error fetching publication feed: {e}")
            return []
    
    def save_to_mongodb(self, articles_data):
        """Lưu vào MongoDB"""
        if not articles_data:
            print("ℹ️  No articles to save")
            return
        
        new_articles = []
        for article in articles_data:
            existing = self.posts_collection.find_one({'article_id': article['article_id']})
            if not existing:
                new_articles.append(article)
        
        if new_articles:
            self.posts_collection.insert_many(new_articles)
            print(f"💾 Saved {len(new_articles)} new Medium articles")
        else:
            print("ℹ️  No new articles to save")
    
    def collect_topics(self, tags, max_results_per_tag=50):
        """Thu thập dữ liệu cho nhiều tags"""
        total_collected = 0
        
        for tag in tags:
            print(f"\n{'='*60}")
            print(f"📝 Collecting Medium: {tag}")
            print(f"{'='*60}")
            
            articles = self.get_tag_feed(tag, max_results=max_results_per_tag)
            self.save_to_mongodb(articles)
            total_collected += len(articles)
        
        print(f"\n{'='*60}")
        print(f"✅ Total Medium articles: {total_collected}")
        print(f"{'='*60}\n")