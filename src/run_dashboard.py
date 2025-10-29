"""Quick script to run only the dashboard"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig
from dashboard.dash_app import DashboardApp

def main():
    print("\n" + "="*60)
    print("Starting Social Media Analysis Dashboard")
    print("="*60)
    
    # Connect to database
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if db is None:
        print("Failed to connect to database. Exiting...")
        return
    
    # Check data
    posts_count = db['posts'].count_documents({})
    print(f"Found {posts_count} posts in database")
    
    if posts_count == 0:
        print("\nWarning: No data in database!")
        print("Tip: Run 'python src/collect_data.py' first to collect data")
        print("Or use the URL Crawler tab to import data from URLs")
    
    # Run dashboard
    print("\nStarting dashboard server...")
    dashboard = DashboardApp(db)
    dashboard.run(debug=True, port=8055)

if __name__ == "__main__":
    main()