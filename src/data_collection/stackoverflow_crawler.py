# src/data_collection/stackoverflow_crawler.py
"""Stack Overflow RSS & API Crawler"""
import requests
import feedparser
from datetime import datetime
import html

class StackOverflowCrawler:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.api_base = "https://api.stackexchange.com/2.3"
        self.rss_base = "https://stackoverflow.com/feeds"
    
    def search_questions_rss(self, tag, max_results=100):
        """Thu thập câu hỏi từ Stack Overflow RSS theo tag"""
        try:
            rss_url = f"{self.rss_base}/tag?tagnames={tag}&sort=newest"
            print(f"🔍 Fetching Stack Overflow questions for tag: {tag}")
            
            feed = feedparser.parse(rss_url)
            questions_data = []
            
            for entry in feed.entries[:max_results]:
                # Decode HTML entities
                title = html.unescape(entry.title)
                summary = html.unescape(entry.get('summary', ''))
                
                question_doc = {
                    'question_id': entry.get('id', entry.link),
                    'title': title,
                    'text': f"{title}\n\n{summary}",
                    'link': entry.link,
                    'published': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'created_at': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'author': entry.get('author', 'Unknown'),
                    'source': 'Stack Overflow',
                    'topic': tag,
                    'tags': [tag],
                    'hashtags': [tag],
                    'platform': 'stackoverflow',
                    'collected_at': datetime.now(),
                    'score': 0,
                    'num_comments': 0,
                    'likes': 0
                }
                questions_data.append(question_doc)
            
            print(f"✅ Found {len(questions_data)} Stack Overflow questions")
            return questions_data
            
        except Exception as e:
            print(f"❌ Error fetching Stack Overflow RSS: {e}")
            return []
    
    def search_questions_api(self, tag, max_results=100):
        """Thu thập câu hỏi qua Stack Exchange API (tốt hơn RSS)"""
        try:
            url = f"{self.api_base}/questions"
            params = {
                'order': 'desc',
                'sort': 'creation',
                'tagged': tag,
                'site': 'stackoverflow',
                'pagesize': min(max_results, 100),
                'filter': 'withbody'
            }
            
            print(f"🔍 Fetching Stack Overflow API for tag: {tag}")
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            questions_data = []
            
            for item in data.get('items', []):
                question_doc = {
                    'question_id': f"so_{item['question_id']}",
                    'title': html.unescape(item['title']),
                    'text': html.unescape(item.get('body', item['title']))[:2000],
                    'link': item['link'],
                    'published': datetime.fromtimestamp(item['creation_date']),
                    'created_at': datetime.fromtimestamp(item['creation_date']),
                    'author': item.get('owner', {}).get('display_name', 'Unknown'),
                    'source': 'Stack Overflow',
                    'topic': tag,
                    'tags': item.get('tags', []),
                    'hashtags': item.get('tags', []),
                    'platform': 'stackoverflow',
                    'collected_at': datetime.now(),
                    'score': item.get('score', 0),
                    'likes': item.get('score', 0),
                    'num_comments': item.get('answer_count', 0),
                    'view_count': item.get('view_count', 0),
                    'is_answered': item.get('is_answered', False)
                }
                questions_data.append(question_doc)
            
            print(f"✅ Found {len(questions_data)} questions via API")
            return questions_data
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            print("📝 Falling back to RSS feed...")
            return self.search_questions_rss(tag, max_results)
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def save_to_mongodb(self, questions_data):
        """Lưu vào MongoDB"""
        if not questions_data:
            print("ℹ️  No questions to save")
            return
        
        new_questions = []
        for question in questions_data:
            existing = self.posts_collection.find_one({'question_id': question['question_id']})
            if not existing:
                new_questions.append(question)
        
        if new_questions:
            self.posts_collection.insert_many(new_questions)
            print(f"💾 Saved {len(new_questions)} new Stack Overflow questions")
        else:
            print("ℹ️  No new questions to save")
    
    def collect_topics(self, tags, max_results_per_tag=100):
        """Thu thập dữ liệu cho nhiều tags"""
        total_collected = 0
        
        for tag in tags:
            print(f"\n{'='*60}")
            print(f"💻 Collecting Stack Overflow: {tag}")
            print(f"{'='*60}")
            
            # Try API first, fallback to RSS if needed
            questions = self.search_questions_api(tag, max_results=max_results_per_tag)
            self.save_to_mongodb(questions)
            total_collected += len(questions)
        
        print(f"\n{'='*60}")
        print(f"✅ Total Stack Overflow questions: {total_collected}")
        print(f"{'='*60}\n")