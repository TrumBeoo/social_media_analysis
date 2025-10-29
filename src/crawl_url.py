"""Command line tool for URL crawling"""
import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig
from data_collection.url_crawler import URLCrawler
from analysis.sentiment_analyzer import SentimentAnalyzer

def main():
    parser = argparse.ArgumentParser(description='Crawl content from URLs')
    parser.add_argument('url', nargs='?', help='Single URL to crawl')
    parser.add_argument('--file', '-f', help='File containing URLs (one per line)')
    parser.add_argument('--topic', '-t', help='Topic/category for the content')
    parser.add_argument('--analyze', '-a', action='store_true', help='Run sentiment analysis after crawling')
    
    args = parser.parse_args()
    
    if not args.url and not args.file:
        parser.print_help()
        print("\nExamples:")
        print("  python src/crawl_url.py https://twitter.com/...")
        print("  python src/crawl_url.py --file urls.txt --topic 'AI Education'")
        print("  python src/crawl_url.py https://reddit.com/... --analyze")
        return
    
    # Connect to database
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if not db:
        print(" Failed to connect to database")
        return
    
    # Initialize crawler
    crawler = URLCrawler(db)
    
    # Crawl
    if args.file:
        print(f" Reading URLs from file: {args.file}")
        results = crawler.crawl_from_file(args.file, args.topic)
    else:
        print(f" Crawling URL: {args.url}")
        post_id = crawler.crawl_url(args.url, args.topic)
        results = [{'url': args.url, 'post_id': post_id, 'success': post_id is not None}]
    
    # Analyze sentiment if requested
    if args.analyze:
        print("\n Running sentiment analysis...")
        analyzer = SentimentAnalyzer(db)
        analyzer.analyze_all_posts()
    
    # Summary
    success_count = sum(1 for r in results if r['success'])
    print(f"\n{'='*60}")
    print(f"Successfully crawled: {success_count}/{len(results)} URLs")
    print(f"{'='*60}")
    
    # Show failed URLs if any
    failed = [r for r in results if not r['success']]
    if failed:
        print("\nFailed URLs:")
        for r in failed:
            print(f"  - {r['url']}")

if __name__ == "__main__":
    main()