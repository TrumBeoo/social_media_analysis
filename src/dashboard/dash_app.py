"""Dash dashboard for social media analysis"""
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

class DashboardApp:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.trends_collection = db['trends']
        self.url_cache_collection = db.get_collection('url_cache')
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                             title="Social Media Analysis Dashboard")
        
        self.COLORS = {
            'positive': '#2ecc71',
            'negative': '#e74c3c',
            'neutral': '#95a5a6',
            'background': '#f8f9fa',
            'card': '#ffffff'
        }
        
        self.setup_layout()
        self.setup_callbacks()
    
    def load_data(self):
        """Load data từ MongoDB"""
        try:
            posts = list(self.posts_collection.find())
            df = pd.DataFrame(posts)
            
            if df.empty:
                return df
            
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['date'] = df['created_at'].dt.date
                df['month'] = df['created_at'].dt.month
                df['year'] = df['created_at'].dt.year
            elif 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.date
                df['month'] = pd.to_datetime(df['date']).dt.month
                df['year'] = pd.to_datetime(df['date']).dt.year
            else:
                df['date'] = pd.Timestamp.now().date()
                df['month'] = pd.Timestamp.now().month
                df['year'] = pd.Timestamp.now().year
            
            if 'sentiment' not in df.columns:
                df['sentiment'] = 'neutral'
            if 'topic' not in df.columns:
                df['topic'] = 'general'
            if 'hashtags' not in df.columns:
                df['hashtags'] = [[] for _ in range(len(df))]
            
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def create_overview_tab(self):
        """Tab tổng quan"""
        df = self.load_data()
        
        return dbc.Container([
            # Summary Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Tổng Posts", className="card-title"),
                            html.H2(f"{len(df):,}" if not df.empty else "0", style={'color': '#3498db'})
                        ])
                    ], style={'backgroundColor': self.COLORS['card']})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Tích cực", className="card-title"),
                            html.H2(f"{len(df[df['sentiment']=='positive']) if not df.empty and 'sentiment' in df.columns else 0:,}", 
                                   style={'color': self.COLORS['positive']})
                        ])
                    ], style={'backgroundColor': self.COLORS['card']})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Tiêu cực", className="card-title"),
                            html.H2(f"{len(df[df['sentiment']=='negative']) if not df.empty and 'sentiment' in df.columns else 0:,}", 
                                   style={'color': self.COLORS['negative']})
                        ])
                    ], style={'backgroundColor': self.COLORS['card']})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Trung lập", className="card-title"),
                            html.H2(f"{len(df[df['sentiment']=='neutral']) if not df.empty and 'sentiment' in df.columns else 0:,}", 
                                   style={'color': self.COLORS['neutral']})
                        ])
                    ], style={'backgroundColor': self.COLORS['card']})
                ], width=3),
            ], className="mb-4"),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Xu hướng thảo luận theo thời gian"),
                        dbc.CardBody([
                            dcc.Graph(id='timeline-chart')
                        ])
                    ])
                ], width=8),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Phân bố cảm xúc"),
                        dbc.CardBody([
                            dcc.Graph(id='sentiment-pie')
                        ])
                    ])
                ], width=4),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Top 15 Hashtags"),
                        dbc.CardBody([
                            dcc.Graph(id='hashtag-chart')
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Cảm xúc theo chủ đề"),
                        dbc.CardBody([
                            dcc.Graph(id='topic-sentiment-chart')
                        ])
                    ])
                ], width=6),
            ], className="mb-4"),
        ], fluid=True)
    
    def create_url_crawler_tab(self):
        """Tab URL Crawler"""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("Import Content từ URL", className="mb-4"),
                    html.P("Nhập URL của bài viết để tự động thu thập và phân tích", className="text-muted"),
                ])
            ]),
            
            dbc.Row([
                # Single URL Input
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Single URL Input", className="bg-primary text-white"),
                        dbc.CardBody([
                            dbc.Label("URL:", className="fw-bold"),
                            dbc.Input(
                                id='url-input',
                                type='url',
                                placeholder='https://twitter.com/user/status/123...',
                                className='mb-3'
                            ),
                            dbc.Label("Topic/Category (optional):", className="fw-bold"),
                            dbc.Input(
                                id='topic-input',
                                type='text',
                                placeholder='AI Education, EdTech, etc.',
                                className='mb-3'
                            ),
                            dbc.Button(
                                "Crawl URL",
                                id='crawl-button',
                                color='primary',
                                className='w-100',
                                size='lg'
                            ),
                            html.Hr(),
                            html.Div(id='crawl-status', className='mt-3')
                        ])
                    ], className='mb-4')
                ], width=6),
                
                # Multiple URLs Input
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Multiple URLs Input", className="bg-success text-white"),
                        dbc.CardBody([
                            dbc.Label("URLs (one per line):", className="fw-bold"),
                            dcc.Textarea(
                                id='urls-textarea',
                                placeholder='https://twitter.com/...\nhttps://reddit.com/...\nhttps://medium.com/...',
                                style={'width': '100%', 'height': 120},
                                className='mb-3'
                            ),
                            dbc.Label("Topic for all URLs:", className="fw-bold"),
                            dbc.Input(
                                id='batch-topic-input',
                                type='text',
                                placeholder='Common topic',
                                className='mb-3'
                            ),
                            dbc.Button(
                                "Crawl All URLs",
                                id='crawl-batch-button',
                                color='success',
                                className='w-100',
                                size='lg'
                            ),
                            html.Hr(),
                            html.Div(id='batch-crawl-status', className='mt-3')
                        ])
                    ])
                ], width=6)
            ]),
            
            # Recently Crawled URLs
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Span("Recently Crawled URLs", className="me-2"),
                            dbc.Badge(id='url-count-badge', color='info')
                        ]),
                        dbc.CardBody([
                            dcc.Interval(id='url-refresh-interval', interval=5000, n_intervals=0),
                            html.Div(id='recent-urls-table')
                        ])
                    ])
                ])
            ], className='mt-4')
        ], fluid=True)
    
    def setup_layout(self):
        """Setup dashboard layout với tabs"""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1(" Dashboard Phân tích Dữ liệu Xã hội", 
                           className="text-center mb-3 mt-4",
                           style={'color': '#2c3e50', 'fontWeight': 'bold'}),
                    html.H5("Chủ đề: AI trong Giáo dục", 
                           className="text-center mb-4",
                           style={'color': '#7f8c8d'})
                ])
            ]),
            
            # Tabs
            dbc.Tabs([
                dbc.Tab(
                    label="Overview", 
                    tab_id="overview-tab",
                    label_style={'fontSize': '18px', 'fontWeight': 'bold'}
                ),
                dbc.Tab(
                    label="URL Crawler", 
                    tab_id="crawler-tab",
                    label_style={'fontSize': '18px', 'fontWeight': 'bold'}
                ),
            ], id="tabs", active_tab="overview-tab", className="mb-4"),
            
            # Tab content containers (initially render all, control visibility with callbacks)
            html.Div(id='overview-tab-content', children=self.create_overview_tab()),
            html.Div(id='crawler-tab-content', children=self.create_url_crawler_tab(), style={'display': 'none'})
            
        ], fluid=True, style={'backgroundColor': self.COLORS['background'], 'minHeight': '100vh'})
    
    def setup_callbacks(self):
        """Setup all callbacks"""
        
        # Tab switching (control visibility of tab content divs)
        @self.app.callback(
            Output('overview-tab-content', 'style'),
            Output('crawler-tab-content', 'style'),
            Input('tabs', 'active_tab')
        )
        def switch_tab(active_tab):
            if active_tab == "overview-tab": # Overview tab is active
                return {'display': 'block'}, {'display': 'none'}
            elif active_tab == "crawler-tab": # Crawler tab is active
                return {'display': 'none'}, {'display': 'block'}
            return {'display': 'block'}, {'display': 'none'} # Default to overview if something goes wrong
        
        # Overview tab callbacks
        @self.app.callback(
            Output('timeline-chart', 'figure'),
            Input('timeline-chart', 'id')
        )
        def update_timeline(id):
            df = self.load_data()
            if df.empty:
                return go.Figure().add_annotation(text="No data available", showarrow=False)
            
            try:
                if 'date' in df.columns:
                    daily_counts = df.groupby('date').size()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_counts.index,
                        y=daily_counts.values,
                        mode='lines+markers',
                        line=dict(color='#3498db', width=2),
                        name='Posts per day'
                    ))
                    
                    fig.update_layout(
                        title="Xu hướng posts theo ngày",
                        xaxis_title="Ngày",
                        yaxis_title="Số lượng posts",
                        template='plotly_white',
                        height=400
                    )
                    return fig
                else:
                    return go.Figure().add_annotation(text="No date column found", showarrow=False)
            except Exception as e:
                print(f"Error in timeline chart: {e}")
                return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)
        
        @self.app.callback(
            Output('sentiment-pie', 'figure'),
            Input('sentiment-pie', 'id')
        )
        def update_sentiment_pie(id):
            df = self.load_data()
            if df.empty:
                return go.Figure().add_annotation(text="No data available", showarrow=False)
            
            try:
                if 'sentiment' in df.columns:
                    sentiment_counts = df['sentiment'].value_counts()
                    
                    if sentiment_counts.empty:
                        return go.Figure().add_annotation(text="No sentiment data", showarrow=False)
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=[str(s).capitalize() for s in sentiment_counts.index],
                        values=sentiment_counts.values,
                        marker=dict(colors=[self.COLORS.get(s, '#95a5a6') for s in sentiment_counts.index]),
                        hole=0.4,
                        textinfo='label+percent',
                        textfont_size=12
                    )])
                    
                    fig.update_layout(
                        title="Tỷ lệ cảm xúc",
                        height=400,
                        template='plotly_white',
                        showlegend=True
                    )
                    return fig
                else:
                    return go.Figure().add_annotation(text="No sentiment column", showarrow=False)
            except Exception as e:
                print(f"Error in sentiment pie: {e}")
                return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)
        
        @self.app.callback(
            Output('hashtag-chart', 'figure'),
            Input('hashtag-chart', 'id')
        )
        def update_hashtag_chart(id):
            df = self.load_data()
            if df.empty or 'hashtags' not in df.columns:
                return go.Figure().add_annotation(text="No hashtag data available", showarrow=False)
            
            all_hashtags = []
            for hashtags in df['hashtags'].dropna():
                if isinstance(hashtags, list):
                    all_hashtags.extend(hashtags)
            
            if not all_hashtags:
                return go.Figure().add_annotation(text="No hashtags found", showarrow=False)
            
            hashtag_counts = pd.Series(all_hashtags).value_counts().head(15)
            
            fig = go.Figure(data=[go.Bar(
                x=hashtag_counts.values,
                y=hashtag_counts.index,
                orientation='h',
                marker_color='#3498db'
            )])
            
            fig.update_layout(
                title="Top 15 Hashtags",
                xaxis_title="Số lần xuất hiện",
                height=400,
                template='plotly_white'
            )
            
            return fig
        
        @self.app.callback(
            Output('topic-sentiment-chart', 'figure'),
            Input('topic-sentiment-chart', 'id')
        )
        def update_topic_sentiment_chart(id):
            df = self.load_data()
            if df.empty or 'topic' not in df.columns or 'sentiment' not in df.columns:
                return go.Figure().add_annotation(text="No topic/sentiment data available", showarrow=False)
            
            topic_sentiment = df.groupby(['topic', 'sentiment']).size().unstack(fill_value=0)
            
            fig = go.Figure()
            
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment in topic_sentiment.columns:
                    fig.add_trace(go.Bar(
                        name=sentiment.capitalize(),
                        x=topic_sentiment.index,
                        y=topic_sentiment[sentiment],
                        marker_color=self.COLORS.get(sentiment, '#95a5a6')
                    ))
            
            fig.update_layout(
                title="Cảm xúc theo chủ đề",
                xaxis_title="Chủ đề",
                yaxis_title="Số lượng posts",
                barmode='stack',
                height=400,
                template='plotly_white'
            )
            
            return fig
        
        # URL Crawler callbacks
        @self.app.callback(
            Output('crawl-status', 'children'),
            Input('crawl-button', 'n_clicks'),
            State('url-input', 'value'),
            State('topic-input', 'value'),
            prevent_initial_call=True
        )
        def crawl_single_url(n_clicks, url, topic):
            if not url:
                return dbc.Alert(" Please enter a URL", color="warning")
            
            try:
                from data_collection.url_crawler import URLCrawler
                from analysis.sentiment_analyzer import SentimentAnalyzer
                
                crawler = URLCrawler(self.db)
                post_id = crawler.crawl_url(url, topic)
                
                if post_id:
                    analyzer = SentimentAnalyzer(self.db)
                    post = self.posts_collection.find_one({'_id': post_id})
                    if post and 'text' in post:
                        sentiment = analyzer.analyze(post.get('text', ''))
                        self.posts_collection.update_one(
                            {'_id': post_id},
                            {'$set': {
                                'sentiment': sentiment['label'],
                                'sentiment_score': sentiment['score'],
                                'analyzed_at': datetime.now()
                            }}
                        )
                        
                        return dbc.Alert([
                            html.H5("✅ Successfully Crawled!", className="alert-heading"),
                            html.Hr(),
                            html.P([
                                html.Strong("Post ID: "), str(post_id)
                            ]),
                            html.P([
                                html.Strong("Sentiment: "),
                                dbc.Badge(
                                    f"{sentiment['label'].upper()} ({sentiment['score']:.2f})",
                                    color='success' if sentiment['label'] == 'positive' else 'danger' if sentiment['label'] == 'negative' else 'secondary'
                                )
                            ]),
                            html.P([
                                html.Strong("Text preview: "),
                                html.Br(),
                                post.get('text', '')[:200] + '...' if len(post.get('text', '')) > 200 else post.get('text', '')
                            ])
                        ], color="success", dismissable=True)
                    else:
                        return dbc.Alert("✅ Crawled but no text found", color="info")
                else:
                    return dbc.Alert("❌ Failed to crawl URL. Please check the URL format.", color="danger")
                    
            except Exception as e:
                return dbc.Alert([
                    html.H5("❌ Error", className="alert-heading"),
                    html.P(f"Details: {str(e)}")
                ], color="danger")
        
        @self.app.callback(
            Output('batch-crawl-status', 'children'),
            Input('crawl-batch-button', 'n_clicks'),
            State('urls-textarea', 'value'),
            State('batch-topic-input', 'value'),
            prevent_initial_call=True
        )
        def crawl_multiple_urls(n_clicks, urls_text, topic):
            if not urls_text:
                return dbc.Alert(" Please enter at least one URL", color="warning")
            
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            
            if not urls:
                return dbc.Alert(" No valid URLs found", color="warning")
            
            try:
                from data_collection.url_crawler import URLCrawler
                from analysis.sentiment_analyzer import SentimentAnalyzer
                
                crawler = URLCrawler(self.db)
                results = crawler.crawl_multiple_urls(urls, topic)
                
                analyzer = SentimentAnalyzer(self.db)
                analyzer.analyze_all_posts()
                
                success_count = sum(1 for r in results if r['post_id'])
                fail_count = len(results) - success_count
                
                return dbc.Alert([
                    html.H5(f"✅ Batch Crawl Completed!", className="alert-heading"),
                    html.Hr(),
                    html.P([
                        html.Strong(f"Success: "), f"{success_count}/{len(urls)} URLs",
                        html.Br(),
                        html.Strong(f"Failed: "), f"{fail_count} URLs"
                    ]),
                    html.Hr(),
                    html.P("Results:", className="fw-bold"),
                    html.Ul([
                        html.Li([
                            '✅ ' if r['post_id'] else '❌ ',
                            html.Small(r['url'][:60] + ('...' if len(r['url']) > 60 else ''))
                        ]) for r in results[:10]
                    ] + ([html.Li(f"... and {len(results) - 10} more")] if len(results) > 10 else []))
                ], color="success" if success_count > 0 else "warning", dismissable=True)
                
            except Exception as e:
                return dbc.Alert([
                    html.H5("❌ Batch Crawl Error", className="alert-heading"),
                    html.P(f"Details: {str(e)}")
                ], color="danger")
        
        @self.app.callback(
            [Output('recent-urls-table', 'children'),
             Output('url-count-badge', 'children')],
            [Input('url-refresh-interval', 'n_intervals'),
             Input('crawl-status', 'children'),
             Input('batch-crawl-status', 'children')]
        )
        def update_recent_urls(n_intervals, status1, status2):
            """Hiển thị URLs đã crawl gần đây"""
            try:
                recent = list(self.url_cache_collection.find().sort('crawled_at', -1).limit(20))
                
                if not recent:
                    return html.P("No URLs crawled yet. Start by entering a URL above!", className="text-muted text-center p-4"), "0"
                
                table = dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("#", style={'width': '50px'}),
                            html.Th("URL"),
                            html.Th("Crawled At", style={'width': '180px'}),
                            html.Th("Status", style={'width': '80px', 'textAlign': 'center'})
                        ])
                    ], className="table-dark"),
                    html.Tbody([
                        html.Tr([
                            html.Td(str(idx + 1)),
                            html.Td(
                                html.A(
                                    r['url'][:70] + ('...' if len(r['url']) > 70 else ''),
                                    href=r['url'],
                                    target='_blank',
                                    className="text-decoration-none"
                                )
                            ),
                            html.Td(r['crawled_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(r['crawled_at'], datetime) else str(r['crawled_at'])),
                            html.Td(
                                dbc.Badge("✅", color="success", className="w-100"),
                                style={'textAlign': 'center'}
                            )
                        ]) for idx, r in enumerate(recent)
                    ])
                ], bordered=True, hover=True, responsive=True, striped=True, size='sm')
                
                return table, str(len(recent))
            except Exception as e:
                print(f"Error updating recent URLs: {e}")
                return html.P(f"Error loading URLs: {str(e)}", className="text-danger"), "0"
    
    def run(self, debug=True, port=8055):
        """Run the dashboard"""
        print("\n" + "="*60)
        print(" Starting Dashboard...")
        print("="*60)
        print(f"Dashboard URL: http://127.0.0.1:{port}")
        print(f" Features:")
        print(f"   - Overview Tab: Data visualization")
        print(f"   - URL Crawler Tab: Import content from URLs")
        print("="*60 + "\n")
        try:
            self.app.run_server(debug=debug, port=port, host='127.0.0.1')
        except OSError as e:
            print(f"  Port {port} is busy, trying port {port+1}")
            self.app.run_server(debug=debug, port=port+1, host='127.0.0.1')