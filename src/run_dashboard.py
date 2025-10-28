"""Quick script to run only the dashboard"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.database import DatabaseConfig
from dashboard.dash_app import DashboardApp

def main():
    print("Starting Dashboard Only...")
    
    # Connect to database
    db_config = DatabaseConfig()
    db = db_config.connect()
    
    if db is None:
        print("❌ Failed to connect to database. Exiting...")
        return
    
    # Run dashboard
    dashboard = DashboardApp(db)
    dashboard.run(debug=True, port=8050)

if __name__ == "__main__":
    main()