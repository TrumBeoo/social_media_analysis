# Corrected analysis code that works with your actual data structure

import pandas as pd
from pymongo import MongoClient
from collections import Counter
import re

# MongoDB connection
MONGO_URI = "mongodb+srv://TrumBeoo:1xr1R8BRdLafRzTg@trumbeoo.c0hnfng.mongodb.net/social_media_analysis?" \
            "retryWrites=true&w=majority&appName=TrumBeoo"

client = MongoClient(MONGO_URI)
db = client['social_media_analysis']
posts_collection = db['posts']

def analyze_by_topic_corrected():
    """Fixed topic analysis using actual data fields"""
    pipeline = [
        {
            '$group': {
                '_id': '$topic',
                'total_posts': {'$sum': 1},
                'positive': {
                    '$sum': {'$cond': [{'$eq': ['$sentiment', 'positive']}, 1, 0]}
                },
                'negative': {
                    '$sum': {'$cond': [{'$eq': ['$sentiment', 'negative']}, 1, 0]}
                },
                'neutral': {
                    '$sum': {'$cond': [{'$eq': ['$sentiment', 'neutral']}, 1, 0]}
                },
                'avg_sentiment_score': {'$avg': '$sentiment_score'},
                'avg_score': {'$avg': '$score'},  # Use 'score' instead of 'likes'
                'avg_comments': {'$avg': '$num_comments'}  # Reddit engagement metric
            }
        },
        {'$sort': {'total_posts': -1}}
    ]
    
    results = list(posts_collection.aggregate(pipeline))
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    if not df.empty:
        df['positive_pct'] = (df['positive'] / df['total_posts'] * 100).round(2)
        df['negative_pct'] = (df['negative'] / df['total_posts'] * 100).round(2)
        df['neutral_pct'] = (df['neutral'] / df['total_posts'] * 100).round(2)
    
    return df

def get_engagement_stats():
    """Get engagement statistics using available fields"""
    pipeline = [
        {
            '$group': {
                '_id': None,
                'avg_score': {'$avg': '$score'},
                'avg_comments': {'$avg': '$num_comments'},
                'avg_upvote_ratio': {'$avg': '$upvote_ratio'},
                'total_posts': {'$sum': 1},
                'sentiment_counts': {
                    '$push': '$sentiment'
                }
            }
        }
    ]
    
    result = list(posts_collection.aggregate(pipeline))
    if result:
        stats = result[0]
        # Count sentiments
        sentiment_counts = Counter(stats['sentiment_counts'])
        stats['sentiment_distribution'] = dict(sentiment_counts)
        del stats['sentiment_counts']
        return stats
    return {}

def get_top_hashtags_from_text(limit=10):
    """Extract hashtags from text since hashtags field doesn't exist"""
    all_hashtags = []
    
    # Get all posts
    posts = posts_collection.find({}, {'text': 1, 'title': 1})
    
    for post in posts:
        # Check both text and title for hashtags
        text_content = str(post.get('text', '')) + ' ' + str(post.get('title', ''))
        hashtags = re.findall(r'#\w+', text_content)
        hashtags = [tag[1:] for tag in hashtags]  # Remove # symbol
        all_hashtags.extend(hashtags)
    
    if not all_hashtags:
        return [("No hashtags found", 0)]
    
    hashtag_counts = Counter(all_hashtags)
    return hashtag_counts.most_common(limit)

# Run the corrected analysis
print("=== CORRECTED ANALYSIS ===")

# Topic analysis
topic_analysis = analyze_by_topic_corrected()
print("\nSentiment Analysis by Topic:")
print(topic_analysis)

# Engagement stats
engagement_stats = get_engagement_stats()
print("\nEngagement Statistics:")
for key, value in engagement_stats.items():
    print(f"{key}: {value}")

# Top hashtags
top_hashtags = get_top_hashtags_from_text()
print(f"\nTop {len(top_hashtags)} Hashtags:")
for hashtag, count in top_hashtags:
    print(f"#{hashtag}: {count} mentions")

print("\nAnalysis completed successfully!")