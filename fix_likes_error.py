# Fix for KeyError: "Column(s) ['likes'] do not exist"

import pandas as pd
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb+srv://TrumBeoo:1xr1R8BRdLafRzTg@trumbeoo.c0hnfng.mongodb.net/social_media_analysis?" \
            "retryWrites=true&w=majority&appName=TrumBeoo"

client = MongoClient(MONGO_URI)
db = client['social_media_analysis']
posts_collection = db['posts']

# Check what columns exist in your data
sample_data = list(posts_collection.find().limit(5))
if sample_data:
    print("Available fields in your data:")
    for key in sample_data[0].keys():
        print(f"- {key}")
    
    # Create DataFrame to see structure
    df = pd.DataFrame(sample_data)
    print(f"\nDataFrame columns: {df.columns.tolist()}")
    print(f"DataFrame shape: {df.shape}")
    
    # Check if 'likes' column exists
    if 'likes' not in df.columns:
        print("\n❌ 'likes' column not found!")
        print("Available numeric columns for analysis:")
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        print(numeric_cols)
        
        # Suggest alternatives
        if 'score' in df.columns:
            print("✅ Use 'score' instead of 'likes' for Reddit data")
        if 'num_comments' in df.columns:
            print("✅ Use 'num_comments' for engagement analysis")
    else:
        print("✅ 'likes' column found!")
else:
    print("No data found in database")