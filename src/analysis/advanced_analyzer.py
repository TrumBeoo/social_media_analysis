"""Advanced analysis including topic modeling and correlation analysis"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnalyzer:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        try:
            posts_data = list(self.posts_collection.find())
            self.df = pd.DataFrame(posts_data)
            
            # Ensure required columns exist with default values
            if not self.df.empty:
                if 'sentiment_score' not in self.df.columns:
                    self.df['sentiment_score'] = 0.0
                if 'likes' not in self.df.columns:
                    self.df['likes'] = 0
                if 'retweets' not in self.df.columns:
                    self.df['retweets'] = 0
                if 'replies' not in self.df.columns:
                    self.df['replies'] = 0
                if 'sentiment' not in self.df.columns:
                    self.df['sentiment'] = 'neutral'
        except Exception as e:
            print(f"Error loading data in AdvancedAnalyzer: {e}")
            self.df = pd.DataFrame()
    
    def topic_modeling(self, n_topics=5):
        """Topic Modeling với LDA"""
        texts = self.df['text'].fillna('').tolist()
        
        vectorizer = TfidfVectorizer(
            max_features=100,
            min_df=2,
            max_df=0.8,
            stop_words='english'
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=10
        )
        
        lda.fit(tfidf_matrix)
        
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(lda.components_):
            top_indices = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            topics.append({
                'topic_id': topic_idx,
                'top_words': top_words
            })
        
        return topics
    
    def sentiment_correlation(self):
        """Phân tích correlation giữa sentiment và engagement"""
        if self.df.empty:
            return pd.DataFrame()
        
        # Only include columns that exist and have numeric data
        correlation_cols = []
        for col in ['sentiment_score', 'likes', 'retweets', 'replies']:
            if col in self.df.columns and pd.api.types.is_numeric_dtype(self.df[col]):
                correlation_cols.append(col)
        
        if len(correlation_cols) < 2:
            print("Not enough numeric columns for correlation analysis")
            return pd.DataFrame()
        
        try:
            correlation = self.df[correlation_cols].corr()
            return correlation
        except Exception as e:
            print(f"Error in correlation analysis: {e}")
            return pd.DataFrame()
    
    def sentiment_by_engagement(self):
        """Phân tích cảm xúc theo mức độ engagement"""
        if self.df.empty or 'likes' not in self.df.columns or 'sentiment' not in self.df.columns:
            return pd.DataFrame()
        
        try:
            # Ensure likes column is numeric
            self.df['likes'] = pd.to_numeric(self.df['likes'], errors='coerce').fillna(0)
            
            self.df['engagement_level'] = pd.cut(
                self.df['likes'],
                bins=[0, 10, 50, 100, float('inf')],
                labels=['Low', 'Medium', 'High', 'Viral']
            )
            
            engagement_sentiment = self.df.groupby(['engagement_level', 'sentiment']).size().unstack(fill_value=0)
            return engagement_sentiment
        except Exception as e:
            print(f"Error in engagement analysis: {e}")
            return pd.DataFrame()
    
    def keyword_extraction(self, top_n=20):
        """Trích xuất từ khóa quan trọng"""
        texts = ' '.join(self.df['text'].fillna(''))
        
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([texts])
        
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        keywords = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
        
        return keywords
    
    def generate_advanced_report(self):
        """Tạo báo cáo phân tích nâng cao"""
        print("\n🔬 PHÂN TÍCH NÂNG CAO\n")
        
        print("📚 TOPIC MODELING (LDA):")
        topics = self.topic_modeling(n_topics=5)
        for topic in topics:
            print(f"\n  Topic {topic['topic_id']}:")
            print(f"  Top words: {', '.join(topic['top_words'][:10])}")
        
        print("\n📊 CORRELATION ANALYSIS:")
        correlation = self.sentiment_correlation()
        print(correlation)
        
        print("\n🔑 TOP 15 KEYWORDS (TF-IDF):")
        keywords = self.keyword_extraction(15)
        for i, (word, score) in enumerate(keywords, 1):
            print(f"  {i}. {word}: {score:.4f}")
        
        print("\n💪 SENTIMENT BY ENGAGEMENT LEVEL:")
        engagement_sentiment = self.sentiment_by_engagement()
        print(engagement_sentiment)