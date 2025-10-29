"""URL Content Crawler - Thu thập và phân tích nội dung từ URL"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urlparse
import hashlib

class URLCrawler:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.url_cache_collection = db.get_collection('url_cache')
        
        self.supported_platforms = {
            'twitter.com': self._parse_twitter,
            'x.com': self._parse_twitter,
            'reddit.com': self._parse_reddit,
            'facebook.com': self._parse_facebook,
            'medium.com': self._parse_medium,
            'generic': self._parse_generic
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def crawl_url(self, url, topic=None):
        """Thu thập nội dung từ URL"""
        # Kiểm tra URL đã được crawl chưa
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cached = self.url_cache_collection.find_one({'url_hash': url_hash})
        
        if cached:
            print(f"  URL already crawled on {cached['crawled_at']}")
            return cached['post_id']
        
        try:
            print(f" Crawling: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Xác định platform
            domain = urlparse(url).netloc.lower()
            platform = self._identify_platform(domain)
            print(f" Detected platform: {platform}")
            
            # Parse content theo platform
            parser = self.supported_platforms.get(platform, self.supported_platforms['generic'])
            post_data = parser(response.text, url)
            
            # Bổ sung metadata
            post_data.update({
                'source': f'url_crawler_{platform}',
                'source_url': url,
                'topic': topic or 'url_imported',
                'collected_at': datetime.now(),
                'crawl_method': 'url_direct'
            })
            
            # Lưu vào database
            result = self.posts_collection.insert_one(post_data)
            post_id = result.inserted_id
            
            # Lưu cache
            self.url_cache_collection.insert_one({
                'url': url,
                'url_hash': url_hash,
                'post_id': post_id,
                'crawled_at': datetime.now(),
                'platform': platform
            })
            
            print(f" Successfully crawled and saved!")
            return post_id
            
        except requests.exceptions.RequestException as e:
            print(f" Network error: {e}")
            return None
        except Exception as e:
            print(f" Error crawling {url}: {e}")
            return None
    
    def _identify_platform(self, domain):
        """Xác định platform từ domain"""
        for platform in self.supported_platforms.keys():
            if platform in domain:
                return platform
        return 'generic'
    
    def _parse_twitter(self, html, url):
        """Parse Twitter content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract tweet content
        text = self._extract_meta_content(soup, 'og:description') or \
               self._extract_meta_content(soup, 'twitter:description') or \
               self._extract_meta_content(soup, 'description') or ''
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        
        return {
            'text': text,
            'title': self._extract_meta_content(soup, 'og:title') or 'Twitter Post',
            'created_at': datetime.now(),
            'likes': 0,
            'retweets': 0,
            'replies': 0,
            'hashtags': hashtags,
            'platform': 'twitter'
        }
    
    def _parse_reddit(self, html, url):
        """Parse Reddit content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        title = self._extract_meta_content(soup, 'og:title') or ''
        description = self._extract_meta_content(soup, 'og:description') or ''
        
        # Combine title and description
        full_text = f"{title}\n\n{description}" if description else title
        
        return {
            'title': title,
            'text': full_text,
            'created_at': datetime.now(),
            'score': 0,
            'num_comments': 0,
            'platform': 'reddit'
        }
    
    def _parse_facebook(self, html, url):
        """Parse Facebook content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            'text': self._extract_meta_content(soup, 'og:description') or '',
            'title': self._extract_meta_content(soup, 'og:title') or 'Facebook Post',
            'created_at': datetime.now(),
            'likes': 0,
            'platform': 'facebook'
        }
    
    def _parse_medium(self, html, url):
        """Parse Medium article"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Medium specific parsing
        article = soup.find('article')
        if article:
            text = article.get_text(separator=' ', strip=True)
        else:
            text = self._extract_meta_content(soup, 'og:description') or ''
        
        return {
            'title': self._extract_meta_content(soup, 'og:title') or 'Medium Article',
            'text': text[:2000],  # Giới hạn độ dài
            'created_at': datetime.now(),
            'platform': 'medium',
            'author': self._extract_meta_content(soup, 'author') or 'Unknown'
        }
    
    def _parse_generic(self, html, url):
        """Parse generic webpage"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)[:2000]
        
        # Extract title
        title = self._extract_meta_content(soup, 'og:title') or \
                (soup.title.string if soup.title else 'Untitled')
        
        return {
            'title': title,
            'text': text,
            'created_at': datetime.now(),
            'platform': 'web'
        }
    
    def _extract_meta_content(self, soup, property_name):
        """Extract meta tag content"""
        meta = soup.find('meta', property=property_name) or \
               soup.find('meta', attrs={'name': property_name})
        return meta.get('content', '').strip() if meta else None
    
    def crawl_multiple_urls(self, urls, topic=None):
        """Crawl nhiều URLs"""
        results = []
        for url in urls:
            url = url.strip()
            if url:
                post_id = self.crawl_url(url, topic)
                results.append({'url': url, 'post_id': post_id, 'success': post_id is not None})
        
        success_count = sum(1 for r in results if r['success'])
        print(f"\n Crawled {success_count}/{len(results)} URLs successfully")
        return results
    
    def crawl_from_file(self, filepath, topic=None):
        """Crawl URLs từ file text"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            print(f" Found {len(urls)} URLs in file")
            return self.crawl_multiple_urls(urls, topic)
        except FileNotFoundError:
            print(f" File not found: {filepath}")
            return []
        except Exception as e:
            print(f"Error reading file: {e}")
            return []