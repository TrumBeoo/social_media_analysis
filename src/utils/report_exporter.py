"""Export analysis results to various formats"""
import json
import pandas as pd
from datetime import datetime

class ReportExporter:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def export_to_csv(self, filename=None):
        """Export DataFrame to CSV"""
        if filename is None:
            filename = f'social_media_analysis_{self.timestamp}.csv'
        
        df = pd.DataFrame(list(self.posts_collection.find()))
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ Exported to {filename}")
        return filename
    
    def export_to_json(self, report_data, filename=None):
        """Export report to JSON"""
        if filename is None:
            filename = f'analysis_report_{self.timestamp}.json'
        
        df = pd.DataFrame(list(self.posts_collection.find()))
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_records': len(df),
                'date_range': {
                    'start': df['created_at'].min().isoformat() if 'created_at' in df.columns else None,
                    'end': df['created_at'].max().isoformat() if 'created_at' in df.columns else None
                }
            },
            'analysis': report_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Exported to {filename}")
        return filename
    
    def create_presentation_summary(self, report_data, filename=None):
        """Tạo file summary cho presentation"""
        if filename is None:
            filename = f'presentation_summary_{self.timestamp}.txt'
        
        df = pd.DataFrame(list(self.posts_collection.find()))
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("SOCIAL MEDIA ANALYSIS SUMMARY\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Dataset Size: {len(df):,} posts\n")
            if 'created_at' in df.columns:
                f.write(f"Date Range: {df['created_at'].min().date()} to {df['created_at'].max().date()}\n\n")
            
            if 'sentiment' in df.columns:
                f.write("SENTIMENT DISTRIBUTION:\n")
                sentiment_counts = df['sentiment'].value_counts()
                for sentiment, count in sentiment_counts.items():
                    pct = count / len(df) * 100
                    f.write(f"  - {sentiment.capitalize()}: {count:,} ({pct:.1f}%)\n")
            
            if 'topic' in df.columns:
                f.write("\nTOP 5 TOPICS:\n")
                topic_counts = df['topic'].value_counts().head(5)
                for i, (topic, count) in enumerate(topic_counts.items(), 1):
                    f.write(f"  {i}. {topic}: {count:,} posts\n")
        
        print(f"✅ Created summary: {filename}")
        return filename