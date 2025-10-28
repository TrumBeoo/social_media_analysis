# Social Media Analysis Project - Restructured

## Tổng quan
Project phân tích dữ liệu mạng xã hội về chủ đề "AI trong Giáo dục" được tái cấu trúc từ Jupyter Notebook thành các module Python riêng biệt.

## Cấu trúc thư mục mới

```
social_media_analysis/
├── src/                          # Source code chính
│   ├── config/                   # Cấu hình
│   │   └── database.py          # Kết nối MongoDB
│   ├── data_collection/         # Thu thập dữ liệu
│   │   ├── twitter_crawler.py   # Thu thập Twitter
│   │   └── reddit_crawler.py    # Thu thập Reddit
│   ├── analysis/                # Phân tích dữ liệu
│   │   ├── sentiment_analyzer.py    # Phân tích cảm xúc
│   │   ├── trend_analyzer.py        # Phân tích xu hướng
│   │   └── advanced_analyzer.py     # Phân tích nâng cao
│   ├── dashboard/               # Dashboard
│   │   └── dash_app.py         # Dash dashboard
│   └── utils/                   # Tiện ích
│       ├── mock_data_generator.py   # Tạo dữ liệu mẫu
│       └── report_exporter.py       # Xuất báo cáo
├── data/                        # Dữ liệu thô
├── reports/                     # Báo cáo xuất ra
├── tests/                       # Unit tests
├── main.py                      # Entry point chính
├── requirements.txt             # Dependencies
└── README_NEW.md               # Hướng dẫn mới
```


# Chỉ thu thập dữ liệu
python collect_data.py

# Chỉ phân tích dữ liệu
python analyze_data.py

# Chỉ dashboard
python run_dashboard.py


## Cài đặt

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng
```bash
python main.py
```

## Các module chính

### 1. Database Configuration (`src/config/database.py`)
- Quản lý kết nối MongoDB
- Tạo collections và indexes

### 2. Data Collection
- **Twitter Crawler**: Thu thập tweets bằng snscrape
- **Reddit Crawler**: Thu thập posts từ Reddit bằng PRAW

### 3. Analysis Modules
- **Sentiment Analyzer**: Phân tích cảm xúc tiếng Việt và Anh
- **Trend Analyzer**: Phân tích xu hướng và thống kê
- **Advanced Analyzer**: Topic modeling, correlation analysis

### 4. Dashboard (`src/dashboard/dash_app.py`)
- Interactive dashboard với Dash
- Biểu đồ real-time
- Filters và controls

### 5. Utilities
- **Mock Data Generator**: Tạo dữ liệu test
- **Report Exporter**: Xuất báo cáo CSV, JSON

## Sử dụng từng module riêng

### Thu thập dữ liệu Twitter
```python
from src.config.database import DatabaseConfig
from src.data_collection.twitter_crawler import TwitterCrawler

db = DatabaseConfig().connect()
crawler = TwitterCrawler(db)
crawler.collect_topics(["AI education"], max_results_per_topic=100)
```

### Phân tích cảm xúc
```python
from src.analysis.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer(db)
analyzer.analyze_all_posts()
```

### Chạy dashboard
```python
from src.dashboard.dash_app import DashboardApp

dashboard = DashboardApp(db)
dashboard.run(port=8050)
```

## Ưu điểm của cấu trúc mới

### ✅ Modular Design
- Mỗi chức năng trong module riêng
- Dễ maintain và debug
- Có thể test từng module

### ✅ Scalability
- Dễ thêm data sources mới
- Dễ mở rộng analysis methods
- Có thể deploy từng phần

### ✅ Reusability
- Các module có thể dùng lại
- Import theo nhu cầu
- Không phụ thuộc Jupyter

### ✅ Production Ready
- Có thể chạy như service
- Error handling tốt hơn
- Logging và monitoring

## Workflow chính

1. **Database Connection**: Kết nối MongoDB
2. **Data Collection**: Thu thập từ Twitter, Reddit
3. **Data Processing**: Sentiment analysis, trend analysis
4. **Advanced Analysis**: Topic modeling, correlations
5. **Export Results**: CSV, JSON reports
6. **Dashboard**: Interactive visualization

## Chạy từng phần riêng

### Chỉ thu thập dữ liệu
```python
from src.config.database import DatabaseConfig
from src.data_collection.twitter_crawler import TwitterCrawler

db = DatabaseConfig().connect()
crawler = TwitterCrawler(db)
# Thu thập dữ liệu...
```

### Chỉ phân tích
```python
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.trend_analyzer import TrendAnalyzer

# Phân tích dữ liệu có sẵn...
```

### Chỉ dashboard
```python
from src.dashboard.dash_app import DashboardApp

dashboard = DashboardApp(db)
dashboard.run()
```

## Testing

Mỗi module có thể test riêng:
```bash
python -m pytest tests/test_sentiment_analyzer.py
python -m pytest tests/test_twitter_crawler.py
```

## Deployment

Có thể deploy:
- Dashboard như web app
- Data collection như scheduled job
- Analysis như batch processing

## Migration từ Notebook

Tất cả code từ `main.ipynb` đã được tách thành:
- 11 modules Python riêng biệt
- Cấu trúc rõ ràng theo chức năng
- Dễ maintain và scale

Chạy `python main.py` để có workflow tương tự notebook nhưng với cấu trúc tốt hơn.


