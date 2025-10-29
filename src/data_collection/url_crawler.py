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
        """Thu thập nội dung từ URL với logging cải tiến"""
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
            
            print(f" Response status: {response.status_code}")
            print(f" Content length: {len(response.text)} characters")
            
            # Xác định platform
            domain = urlparse(url).netloc.lower()
            platform = self._identify_platform(domain)
            print(f" Detected platform: {platform}")
            
            # Parse content theo platform
            parser = self.supported_platforms.get(platform, self.supported_platforms['generic'])
            post_data = parser(response.text, url)
            
            # Debug: Kiểm tra nội dung đã extract
            text_length = len(post_data.get('text', ''))
            title_length = len(post_data.get('title', ''))
            print(f" Extracted - Title: {title_length} chars, Text: {text_length} chars")
            
            if text_length == 0:
                print(f" ⚠️ Warning: No text content extracted from {url}")
                # Try fallback extraction
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                fallback_text = soup.get_text(separator=' ', strip=True)[:500]
                if fallback_text:
                    post_data['text'] = f"[Fallback extraction] {fallback_text}"
                    print(f" Applied fallback extraction: {len(fallback_text)} chars")
            
            # Bổ sung metadata
            post_data.update({
                'source': f'url_crawler_{platform}',
                'source_url': url,
                'topic': topic or 'url_imported',
                'collected_at': datetime.now(),
                'crawl_method': 'url_direct',
                'response_status': response.status_code,
                'content_length': len(response.text)
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
                'platform': platform,
                'text_length': text_length,
                'title_length': title_length
            })
            
            print(f" ✅ Successfully crawled and saved! Post ID: {post_id}")
            print(f" Final content - Title: '{post_data.get('title', '')[:50]}...', Text: {len(post_data.get('text', ''))} chars")
            return post_id
            
        except requests.exceptions.RequestException as e:
            print(f" ❌ Network error: {e}")
            return None
        except Exception as e:
            print(f" ❌ Error crawling {url}: {e}")
            import traceback
            print(f" Traceback: {traceback.format_exc()}")
            return None
    
    def _identify_platform(self, domain):
        """Xác định platform từ domain"""
        for platform in self.supported_platforms.keys():
            if platform in domain:
                return platform
        return 'generic'
    
    def _parse_twitter(self, html, url):
        """Parse Twitter content with improved extraction"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract tweet content from multiple sources
        text = (self._extract_meta_content(soup, 'og:description') or 
               self._extract_meta_content(soup, 'twitter:description') or 
               self._extract_meta_content(soup, 'description') or '')
        
        # Try to get more content from page structure
        if not text or len(text) < 10:
            tweet_selectors = [
                '[data-testid="tweetText"]',
                '.tweet-text',
                '.js-tweet-text',
                '.TweetTextSize'
            ]
            
            for selector in tweet_selectors:
                tweet_element = soup.select_one(selector)
                if tweet_element:
                    text = tweet_element.get_text(strip=True)
                    break
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text) if text else []
        
        title = self._extract_meta_content(soup, 'og:title') or 'Twitter Post'
        
        return {
            'text': text or 'No tweet content extracted',
            'title': title,
            'created_at': datetime.now(),
            'likes': 0,
            'retweets': 0,
            'replies': 0,
            'hashtags': hashtags,
            'platform': 'twitter',
            'url': url
        }
    
    def _parse_reddit(self, html, url):
        """Parse Reddit content with improved extraction"""
        soup = BeautifulSoup(html, 'html.parser')
        
        title = self._extract_meta_content(soup, 'og:title') or ''
        description = self._extract_meta_content(soup, 'og:description') or ''
        
        # Try to get post content from Reddit structure
        content_selectors = [
            '[data-testid="post-content"]',
            '.usertext-body',
            '.md',
            '.Post',
            '[data-click-id="text"]'
        ]
        
        post_content = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                post_content = content_element.get_text(separator=' ', strip=True)
                break
        
        # Combine all content
        full_text_parts = []
        if title:
            full_text_parts.append(title)
        if post_content:
            full_text_parts.append(post_content)
        elif description:
            full_text_parts.append(description)
        
        full_text = '\n\n'.join(full_text_parts) if full_text_parts else 'No content extracted'
        
        return {
            'title': title or 'Reddit Post',
            'text': full_text,
            'created_at': datetime.now(),
            'score': 0,
            'num_comments': 0,
            'platform': 'reddit',
            'url': url
        }
    
    def _parse_facebook(self, html, url):
        """Parse Facebook content with improved extraction"""
        soup = BeautifulSoup(html, 'html.parser')
        
        text = (self._extract_meta_content(soup, 'og:description') or 
               self._extract_meta_content(soup, 'twitter:description') or
               self._extract_meta_content(soup, 'description') or '')
        
        title = self._extract_meta_content(soup, 'og:title') or 'Facebook Post'
        
        # Try to get more content if available
        if not text or len(text) < 20:
            content_selectors = [
                '[data-testid="post_message"]',
                '.userContent',
                '.text_exposed_root'
            ]
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    text = content_element.get_text(strip=True)
                    break
        
        return {
            'text': text or 'No content extracted',
            'title': title,
            'created_at': datetime.now(),
            'likes': 0,
            'platform': 'facebook',
            'url': url
        }
    
    def _parse_medium(self, html, url):
        """Parse Medium article with improved extraction"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Medium specific selectors
        content_selectors = [
            'article',
            '[data-testid="storyContent"]',
            '.postArticle-content',
            '.section-content',
            '.story-content'
        ]
        
        text = ""
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                # Remove unwanted elements
                for unwanted in content.find_all(['script', 'style', 'nav', 'footer']):
                    unwanted.decompose()
                text = content.get_text(separator=' ', strip=True)
                break
        
        # Fallback to meta description
        if not text or len(text) < 50:
            text = self._extract_meta_content(soup, 'og:description') or ''
        
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        title = self._extract_meta_content(soup, 'og:title') or 'Medium Article'
        author = self._extract_meta_content(soup, 'author') or 'Unknown'
        
        return {
            'title': title,
            'text': text or 'No content extracted',
            'created_at': datetime.now(),
            'platform': 'medium',
            'author': author,
            'url': url
        }
    
    def _parse_generic(self, html, url):
        """Parse generic webpage with improved content extraction"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            element.decompose()
        
        # Try multiple strategies to find main content
        content_selectors = [
            'main',
            'article', 
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.story-body',
            '.post-body',
            '#content',
            '#main-content'
        ]
        
        text = ""
        title = ""
        
        # Try to find main content using selectors
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
                break
        
        # Fallback: get all paragraph text
        if not text or len(text) < 50:
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # Final fallback: get all text
        if not text or len(text) < 20:
            text = soup.get_text(separator=' ', strip=True)
        
        # Clean and limit text
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        # Extract title with multiple fallbacks
        title = (self._extract_meta_content(soup, 'og:title') or 
                self._extract_meta_content(soup, 'twitter:title') or
                (soup.title.string.strip() if soup.title and soup.title.string else '') or
                soup.find('h1').get_text(strip=True) if soup.find('h1') else 'Untitled')
        
        # Clean title
        if title:
            title = re.sub(r'\s+', ' ', title).strip()[:200]
        
        # Extract description
        description = (self._extract_meta_content(soup, 'og:description') or
                      self._extract_meta_content(soup, 'twitter:description') or
                      self._extract_meta_content(soup, 'description') or '')
        
        # If text is still empty, use description
        if not text and description:
            text = description
        
        return {
            'title': title or 'Untitled',
            'text': text or 'No content extracted',
            'description': description,
            'created_at': datetime.now(),
            'platform': 'web',
            'url': url
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
        print(f"\n ✅ Crawled {success_count}/{len(results)} URLs successfully")
        
        # Show detailed results
        for result in results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['url'][:60]}...")
        return results
    
    def crawl_from_file(self, filepath, topic=None):
        """Crawl URLs từ file text"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            print(f" 📄 Found {len(urls)} URLs in file: {filepath}")
            return self.crawl_multiple_urls(urls, topic)
        except FileNotFoundError:
            print(f" ❌ File not found: {filepath}")
            return []
        except Exception as e:
            print(f" ❌ Error reading file: {e}")
            return []