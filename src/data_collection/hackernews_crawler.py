# src/data_collection/hackernews_crawler.py
"""Hacker News API Crawler"""
import requests
from datetime import datetime
import time

class HackerNewsCrawler:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.api_base = "https://hacker-news.firebaseio.com/v0"
    
    def get_story_details(self, story_id):
        """Lấy chi tiết một story"""
        try:
            url = f"{self.api_base}/item/{story_id}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching story {story_id}: {e}")
            return None
    
    def search_by_keyword(self, query, max_results=100):
        """
        Tìm kiếm stories theo từ khóa
        Note: HN không có search API chính thức, phải dùng algolia
        """
        try:
            algolia_url = "https://hn.algolia.com/api/v1/search"
            params = {
                'query': query,
                'tags': 'story',
                'hitsPerPage': max_results
            }
            
            print(f"🔍 Searching Hacker News for: {query}")
            
            response = requests.get(algolia_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            stories_data = []
            
            for hit in data.get('hits', []):
                story_doc = {
                    'story_id': f"hn_{hit['objectID']}",
                    'title': hit.get('title', ''),
                    'text': hit.get('story_text', hit.get('title', '')),
                    'link': hit.get('url', f"https://news.ycombinator.com/item?id={hit['objectID']}"),
                    'published': datetime.fromtimestamp(hit['created_at_i']) if 'created_at_i' in hit else datetime.now(),
                    'created_at': datetime.fromtimestamp(hit['created_at_i']) if 'created_at_i' in hit else datetime.now(),
                    'author': hit.get('author', 'Unknown'),
                    'source': 'Hacker News',
                    'topic': query,
                    'hashtags': [query],
                    'platform': 'hackernews',
                    'collected_at': datetime.now(),
                    'score': hit.get('points', 0),
                    'likes': hit.get('points', 0),
                    'num_comments': hit.get('num_comments', 0)
                }
                stories_data.append(story_doc)
            
            print(f"✅ Found {len(stories_data)} Hacker News stories")
            return stories_data
            
        except Exception as e:
            print(f"❌ Error searching Hacker News: {e}")
            return []
    
    def get_top_stories(self, max_results=100):
        """Lấy top stories từ Hacker News"""
        try:
            print(f"🔍 Fetching top {max_results} Hacker News stories...")
            
            # Get top story IDs
            url = f"{self.api_base}/topstories.json"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            story_ids = response.json()[:max_results]
            stories_data = []
            
            for i, story_id in enumerate(story_ids, 1):
                if i % 20 == 0:
                    print(f"   Fetched {i}/{len(story_ids)} stories...")
                
                story = self.get_story_details(story_id)
                if story and story.get('type') == 'story':
                    story_doc = {
                        'story_id': f"hn_{story['id']}",
                        'title': story.get('title', ''),
                        'text': story.get('text', story.get('title', '')),
                        'link': story.get('url', f"https://news.ycombinator.com/item?id={story['id']}"),
                        'published': datetime.fromtimestamp(story['time']) if 'time' in story else datetime.now(),
                        'created_at': datetime.fromtimestamp(story['time']) if 'time' in story else datetime.now(),
                        'author': story.get('by', 'Unknown'),
                        'source': 'Hacker News',
                        'topic': 'top_stories',
                        'hashtags': ['hackernews', 'top'],
                        'platform': 'hackernews',
                        'collected_at': datetime.now(),
                        'score': story.get('score', 0),
                        'likes': story.get('score', 0),
                        'num_comments': story.get('descendants', 0)
                    }
                    stories_data.append(story_doc)
                
                # Be nice to API
                time.sleep(0.1)
            
            print(f"✅ Found {len(stories_data)} top stories")
            return stories_data
            
        except Exception as e:
            print(f"❌ Error fetching top stories: {e}")
            return []
    
    def save_to_mongodb(self, stories_data):
        """Lưu vào MongoDB"""
        if not stories_data:
            print("ℹ️  No stories to save")
            return
        
        new_stories = []
        for story in stories_data:
            existing = self.posts_collection.find_one({'story_id': story['story_id']})
            if not existing:
                new_stories.append(story)
        
        if new_stories:
            self.posts_collection.insert_many(new_stories)
            print(f"💾 Saved {len(new_stories)} new Hacker News stories")
        else:
            print("ℹ️  No new stories to save")
    
    def collect_topics(self, queries, max_results_per_query=50):
        """Thu thập dữ liệu cho nhiều từ khóa"""
        total_collected = 0
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"🚀 Collecting Hacker News: {query}")
            print(f"{'='*60}")
            
            stories = self.search_by_keyword(query, max_results=max_results_per_query)
            self.save_to_mongodb(stories)
            total_collected += len(stories)
        
        print(f"\n{'='*60}")
        print(f"✅ Total Hacker News stories: {total_collected}")
        print(f"{'='*60}\n")