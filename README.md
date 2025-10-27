# Social Media Analysis Project

## Tổng quan
Project phân tích dữ liệu mạng xã hội về chủ đề "AI trong Giáo dục" sử dụng snscrape thay vì Twitter API để thu thập dữ liệu mà không cần Bearer token.

## Thay đổi chính
- ✅ **Thay thế Tweepy bằng snscrape**: Không cần API key hay Bearer token
- ✅ **Thu thập dữ liệu miễn phí**: Sử dụng web scraping thay vì API có giới hạn
- ✅ **Tăng khả năng thu thập**: Có thể lấy tweets cũ hơn 7 ngày
- ✅ **Thêm thông tin user**: Username, số followers

## Cài đặt

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy thu thập dữ liệu Twitter
```bash
python twitter_snscrape.py
```

### 3. Chạy Jupyter Notebook
```bash
jupyter notebook main.ipynb
```

## Ưu điểm của snscrape

### So với Twitter API:
- ❌ **Twitter API**: Cần đăng ký developer account, có giới hạn rate limit
- ✅ **snscrape**: Hoàn toàn miễn phí, không cần đăng ký

### Tính năng:
- Thu thập tweets theo từ khóa
- Lọc theo ngày tháng
- Lấy thông tin engagement (likes, retweets, replies)
- Trích xuất hashtags tự động
- Thông tin user (username, followers)

## Cấu trúc Project

```
social_media_analysis/
├── main.ipynb              # Notebook chính
├── twitter_snscrape.py     # Script thu thập Twitter riêng
├── requirements.txt        # Dependencies
└── README.md              # Hướng dẫn này
```

## Sử dụng

### 1. Thu thập dữ liệu Twitter
```python
from twitter_snscrape import TwitterCrawler

crawler = TwitterCrawler()
tweets = crawler.search_tweets("AI education", max_results=100)
```

### 2. Tùy chỉnh query
```python
# Lấy tweets từ ngày cụ thể
tweets = crawler.search_tweets("AI giáo dục", since_date="2024-01-01")

# Kết hợp nhiều từ khóa
tweets = crawler.search_tweets("AI education OR machine learning")
```

### 3. Lưu vào MongoDB
```python
crawler.save_to_mongodb(tweets, mongo_uri)
```

## Các chủ đề thu thập

1. "AI education"
2. "trí tuệ nhân tạo giáo dục"
3. "AI học tập"
4. "#AIEducation"
5. "machine learning giáo dục"

## Tính năng phân tích

- 📊 **Sentiment Analysis**: Phân tích cảm xúc tiếng Việt và tiếng Anh
- 📈 **Trend Analysis**: Xu hướng theo thời gian
- #️⃣ **Hashtag Analysis**: Top hashtags phổ biến
- 🎯 **Topic Modeling**: Phân loại chủ đề tự động
- 📱 **Interactive Dashboard**: Dash và Streamlit

## Lưu ý

### Giới hạn của snscrape:
- Có thể bị rate limit nếu thu thập quá nhiều
- Cần cập nhật thường xuyên do Twitter thay đổi
- Không có quyền truy cập API chính thức

### Khuyến nghị:
- Thu thập từng đợt nhỏ (50-100 tweets/lần)
- Thêm delay giữa các request
- Kiểm tra trùng lặp trước khi lưu DB

## Troubleshooting

### Lỗi cài đặt snscrape:
```bash
pip install --upgrade snscrape
```

### Lỗi kết nối MongoDB:
- Kiểm tra connection string
- Đảm bảo IP được whitelist

### Lỗi thu thập tweets:
- Thử giảm max_results
- Kiểm tra query syntax
- Thêm delay giữa requests