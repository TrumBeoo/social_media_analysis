# src/dashboard/dash_app.py - PHIÊN BẢN NÂNG CẤP
"""Dash dashboard for social media analysis - Enhanced Version"""
import os
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
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
        self.app = dash.Dash(
            __name__, 
            external_stylesheets=[
                dbc.themes.BOOTSTRAP,
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
            ],
            title="Social Media Analysis Dashboard"
        )
        
        self.COLORS = {
            'positive': '#2ecc71',
            'negative': '#e74c3c',
            'neutral': '#95a5a6',
            'background': '#f8f9fa',
            'card': '#ffffff',
            'primary': '#3498db',
            'warning': '#f39c12',
            'info': '#16a085'
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
                df['month'] = df['created_at'].dt.to_period('M')
                df['month_str'] = df['created_at'].dt.strftime('%Y-%m')
                df['year'] = df['created_at'].dt.year
            elif 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df['month'] = df['date'].dt.to_period('M')
                df['month_str'] = df['date'].dt.strftime('%Y-%m')
                df['year'] = df['date'].dt.year
            else:
                df['date'] = pd.Timestamp.now().date()
                df['month'] = pd.Timestamp.now().to_period('M')
                df['month_str'] = pd.Timestamp.now().strftime('%Y-%m')
                df['year'] = pd.Timestamp.now().year
            
            if 'sentiment' not in df.columns:
                df['sentiment'] = 'neutral'
            if 'sentiment_score' not in df.columns:
                df['sentiment_score'] = 0.0
            if 'topic' not in df.columns:
                df['topic'] = 'general'
            if 'hashtags' not in df.columns:
                df['hashtags'] = [[] for _ in range(len(df))]
            if 'likes' not in df.columns:
                df['likes'] = 0
            if 'source' not in df.columns:
                df['source'] = 'unknown'
            
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def create_overview_tab(self):
        """Tab tổng quan - NÂNG CẤP"""
        df = self.load_data()
        
        return dbc.Container([
            # Summary Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-chart-bar fa-2x mb-2", style={'color': '#3498db'}),
                                html.H4("Tổng Posts", className="card-title mt-2"),
                                html.H2(f"{len(df):,}" if not df.empty else "0", 
                                       style={'color': '#3498db', 'fontWeight': 'bold'})
                            ], style={'textAlign': 'center'})
                        ])
                    ], style={'backgroundColor': self.COLORS['card'], 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-smile fa-2x mb-2", style={'color': self.COLORS['positive']}),
                                html.H4("Tích cực", className="card-title mt-2"),
                                html.H2(f"{len(df[df['sentiment']=='positive']) if not df.empty and 'sentiment' in df.columns else 0:,}", 
                                       style={'color': self.COLORS['positive'], 'fontWeight': 'bold'})
                            ], style={'textAlign': 'center'})
                        ])
                    ], style={'backgroundColor': self.COLORS['card'], 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-frown fa-2x mb-2", style={'color': self.COLORS['negative']}),
                                html.H4("Tiêu cực", className="card-title mt-2"),
                                html.H2(f"{len(df[df['sentiment']=='negative']) if not df.empty and 'sentiment' in df.columns else 0:,}", 
                                       style={'color': self.COLORS['negative'], 'fontWeight': 'bold'})
                            ], style={'textAlign': 'center'})
                        ])
                    ], style={'backgroundColor': self.COLORS['card'], 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-meh fa-2x mb-2", style={'color': self.COLORS['neutral']}),
                                html.H4("Trung lập", className="card-title mt-2"),
                                html.H2(f"{len(df[df['sentiment']=='neutral']) if not df.empty and 'sentiment' in df.columns else 0:,}", 
                                       style={'color': self.COLORS['neutral'], 'fontWeight': 'bold'})
                            ], style={'textAlign': 'center'})
                        ])
                    ], style={'backgroundColor': self.COLORS['card'], 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=3),
            ], className="mb-4"),
            
            # Charts Row 1: Timeline và Sentiment Distribution
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-line me-2"),
                            "Xu hướng thảo luận theo thời gian"
                        ], style={'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Graph(id='timeline-chart', config={'displayModeBar': False})
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=8),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-pie me-2"),
                            "Phân bố cảm xúc"
                        ], style={'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Graph(id='sentiment-pie', config={'displayModeBar': False})
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=4),
            ], className="mb-4"),
            
            # Charts Row 2: Monthly Analysis và Sentiment Score Distribution
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-calendar-alt me-2"),
                            "Phân tích theo tháng"
                        ], style={'backgroundColor': '#16a085', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Graph(id='monthly-chart', config={'displayModeBar': False})
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-area me-2"),
                            "Phân bố điểm cảm xúc"
                        ], style={'backgroundColor': '#16a085', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Graph(id='sentiment-score-dist', config={'displayModeBar': False})
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=6),
            ], className="mb-4"),
            
            # Charts Row 3: Top Hashtags và Topic Sentiment
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-hashtag me-2"),
                            "Top 15 Hashtags"
                        ], style={'backgroundColor': '#8e44ad', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Graph(id='hashtag-chart', config={'displayModeBar': False})
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-tasks me-2"),
                            "Cảm xúc theo chủ đề"
                        ], style={'backgroundColor': '#8e44ad', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Graph(id='topic-sentiment-chart', config={'displayModeBar': False})
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=6),
            ], className="mb-4"),
            
            # Charts Row 4: Engagement Analysis và Source Distribution
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-heart me-2"),
                            "Phân tích Engagement"
                        ], style={'backgroundColor': '#e67e22', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Graph(id='engagement-chart', config={'displayModeBar': False})
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-database me-2"),
                            "Nguồn dữ liệu"
                        ], style={'backgroundColor': '#e67e22', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Graph(id='source-chart', config={'displayModeBar': False})
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ], width=6),
            ], className="mb-4"),
            
            # Recent Posts Table
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-list me-2"),
                                    "Bài viết gần đây (20 bài mới nhất)"
                                ], style={'display': 'inline-block'}),
                                html.Div([
                                    dbc.Button("Refresh", id="refresh-posts-btn", size="sm", color="light", className="ms-2")
                                ], style={'display': 'inline-block', 'float': 'right'})
                            ])
                        ], style={'backgroundColor': '#c0392b', 'color': 'white', 'fontWeight': 'bold'}),
                        dbc.CardBody([
                            dcc.Loading(
                                id="loading-posts",
                                type="default",
                                children=html.Div(id='recent-posts-table')
                            )
                        ])
                    ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
                ])
            ], className="mb-4"),
            
        ], fluid=True)
    
    def create_auto_crawler_tab(self):
        """Tab Auto Data Collection"""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2([
                        html.I(className="fas fa-robot me-3"),
                        "Tự động Thu thập Dữ liệu"
                    ], className="mb-4"),
                    html.P("Thu thập dữ liệu tự động từ các nguồn khác nhau", className="text-muted"),
                ])
            ]),
            
            # Quick Collection Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Thu thập Nhanh", className="bg-success text-white"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        [html.I(className="fas fa-newspaper me-2"), "Google News (30)"],
                                        id='quick-google-btn',
                                        color='primary',
                                        className='w-100 mb-2',
                                        size='lg'
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Button(
                                        [html.I(className="fab fa-reddit me-2"), "Reddit (30)"],
                                        id='quick-reddit-btn',
                                        color='danger',
                                        className='w-100 mb-2',
                                        size='lg'
                                    )
                                ], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        [html.I(className="fab fa-medium me-2"), "Medium (20)"],
                                        id='quick-medium-btn',
                                        color='dark',
                                        className='w-100 mb-2',
                                        size='lg'
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Button(
                                        [html.I(className="fas fa-code me-2"), "Stack Overflow (30)"],
                                        id='quick-stackoverflow-btn',
                                        color='warning',
                                        className='w-100 mb-2',
                                        size='lg'
                                    )
                                ], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button(
                                        [html.I(className="fas fa-fire me-2"), "Hacker News (20)"],
                                        id='quick-hackernews-btn',
                                        color='info',
                                        className='w-100 mb-2',
                                        size='lg'
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Button(
                                        [html.I(className="fas fa-rocket me-2"), "Thu thập Tất cả"],
                                        id='quick-all-btn',
                                        color='success',
                                        className='w-100 mb-2',
                                        size='lg'
                                    )
                                ], width=6),
                            ]),
                            html.Hr(),
                            html.Div(id='quick-collection-status')
                        ])
                    ])
                ], width=8),
                
                # Collection Status
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Trạng thái Thu thập", className="bg-info text-white"),
                        dbc.CardBody([
                            html.Div(id='collection-stats', children=[
                                html.P("Chưa có dữ liệu thu thập", className="text-muted text-center")
                            ])
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # Custom Collection Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Thu thập Tùy chỉnh", className="bg-primary text-white"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Chọn nguồn:", className="fw-bold"),
                                    dcc.Dropdown(
                                        id='source-dropdown',
                                        options=[
                                            {'label': '📰 Google News', 'value': 'google'},
                                            {'label': '🔴 Reddit', 'value': 'reddit'},
                                            {'label': '📝 Medium', 'value': 'medium'},
                                            {'label': '💻 Stack Overflow', 'value': 'stackoverflow'},
                                            {'label': '🚀 Hacker News', 'value': 'hackernews'}
                                        ],
                                        value='google',
                                        className='mb-3'
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Số lượng:", className="fw-bold"),
                                    dbc.Input(
                                        id='custom-count-input',
                                        type='number',
                                        value=20,
                                        min=1,
                                        max=100,
                                        className='mb-3'
                                    )
                                ], width=6)
                            ]),
                            dbc.Label("Từ khóa tìm kiếm:", className="fw-bold"),
                            dbc.Input(
                                id='custom-keywords-input',
                                type='text',
                                placeholder='AI education, machine learning, EdTech',
                                value='AI education',
                                className='mb-3'
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-search me-2"), "Bắt đầu Thu thập"],
                                id='custom-collect-btn',
                                color='primary',
                                className='w-100',
                                size='lg'
                            ),
                            html.Hr(),
                            html.Div(id='custom-collection-status')
                        ])
                    ])
                ], width=8),
                
                # URL Crawler Section (moved here)
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Thu thập từ URL", className="bg-warning text-dark"),
                        dbc.CardBody([
                            dbc.Label("URL:", className="fw-bold"),
                            dbc.Input(
                                id='url-input',
                                type='url',
                                placeholder='https://...',
                                className='mb-3'
                            ),
                            dbc.Label("Topic:", className="fw-bold"),
                            dbc.Input(
                                id='topic-input',
                                type='text',
                                placeholder='AI Education',
                                className='mb-3'
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-download me-2"), "Crawl URL"],
                                id='crawl-button',
                                color='warning',
                                className='w-100'
                            ),
                            html.Hr(),
                            html.Div(id='crawl-status')
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # Collection History
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Span([html.I(className="fas fa-history me-2"), "Lịch sử Thu thập"], className="me-2"),
                            dbc.Badge(id='history-count-badge', color='info')
                        ]),
                        dbc.CardBody([
                            dcc.Interval(id='history-refresh-interval', interval=10000, n_intervals=0),
                            html.Div(id='collection-history-table')
                        ])
                    ])
                ])
            ])
        ], fluid=True)
    
    def create_url_crawler_tab(self):
        """Tab URL Crawler (Legacy - kept for compatibility)"""
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2([
                        html.I(className="fas fa-link me-3"),
                        "Import Content từ URL"
                    ], className="mb-4"),
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
                                [html.I(className="fas fa-download me-2"), "Crawl URL"],
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
                                [html.I(className="fas fa-download me-2"), "Crawl All URLs"],
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
                            html.Span([html.I(className="fas fa-history me-2"), "Recently Crawled URLs"], className="me-2"),
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
                    html.H1([
                        html.I(className="fas fa-chart-line me-3"),
                        "Dashboard Phân tích Dữ liệu Xã hội"
                    ], className="text-center mb-3 mt-4",
                       style={'color': '#2c3e50', 'fontWeight': 'bold'}),
                    html.H5("Chủ đề: AI trong Giáo dục", 
                           className="text-center mb-4",
                           style={'color': '#7f8c8d'})
                ])
            ]),
            
            # Auto-refresh interval
            dcc.Interval(id='auto-refresh-interval', interval=30000, n_intervals=0),  # 30 seconds
            
            # Tabs
            dbc.Tabs([
                dbc.Tab(
                    label="📊 Overview", 
                    tab_id="overview-tab",
                    label_style={'fontSize': '16px', 'fontWeight': 'bold'}
                ),
                dbc.Tab(
                    label="🤖 Auto Crawler", 
                    tab_id="auto-crawler-tab",
                    label_style={'fontSize': '16px', 'fontWeight': 'bold'}
                ),
                dbc.Tab(
                    label="🔗 URL Crawler", 
                    tab_id="url-crawler-tab",
                    label_style={'fontSize': '16px', 'fontWeight': 'bold'}
                ),
            ], id="tabs", active_tab="overview-tab", className="mb-4"),
            
            # Tab content containers
            html.Div(id='overview-tab-content', children=self.create_overview_tab()),
            html.Div(id='auto-crawler-tab-content', children=self.create_auto_crawler_tab(), style={'display': 'none'}),
            html.Div(id='url-crawler-tab-content', children=self.create_url_crawler_tab(), style={'display': 'none'})
            
        ], fluid=True, style={'backgroundColor': self.COLORS['background'], 'minHeight': '100vh'})
    
    def setup_callbacks(self):
        """Setup all callbacks"""
        
        # Tab switching
        @self.app.callback(
            Output('overview-tab-content', 'style'),
            Output('auto-crawler-tab-content', 'style'),
            Output('url-crawler-tab-content', 'style'),
            Input('tabs', 'active_tab')
        )
        def switch_tab(active_tab):
            if active_tab == "overview-tab":
                return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
            elif active_tab == "auto-crawler-tab":
                return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
            elif active_tab == "url-crawler-tab":
                return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
            return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
        
        # Timeline chart
        @self.app.callback(
            Output('timeline-chart', 'figure'),
            [Input('timeline-chart', 'id'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_timeline(id, n):
            df = self.load_data()
            if df.empty:
                return go.Figure().add_annotation(text="No data available", showarrow=False)
            
            try:
                if 'date' in df.columns and 'sentiment' in df.columns:
                    daily_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
                    
                    fig = go.Figure()
                    
                    for sentiment in ['positive', 'negative', 'neutral']:
                        if sentiment in daily_sentiment.columns:
                            fig.add_trace(go.Scatter(
                                x=daily_sentiment.index,
                                y=daily_sentiment[sentiment],
                                mode='lines+markers',
                                name=sentiment.capitalize(),
                                line=dict(color=self.COLORS[sentiment], width=2),
                                marker=dict(size=6)
                            ))
                    
                    fig.update_layout(
                        xaxis_title="Ngày",
                        yaxis_title="Số lượng posts",
                        template='plotly_white',
                        height=400,
                        hovermode='x unified',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    return fig
                else:
                    return go.Figure().add_annotation(text="No date column found", showarrow=False)
            except Exception as e:
                print(f"Error in timeline chart: {e}")
                return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)
        
        # Sentiment pie chart
        @self.app.callback(
            Output('sentiment-pie', 'figure'),
            [Input('sentiment-pie', 'id'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_sentiment_pie(id, n):
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
                        textinfo='label+percent+value',
                        textfont_size=14,
                        pull=[0.05 if s == 'positive' else 0 for s in sentiment_counts.index]
                    )])
                    
                    fig.update_layout(
                        height=400,
                        template='plotly_white',
                        showlegend=True,
                        legend=dict(orientation="v", yanchor="middle", y=0.5)
                    )
                    return fig
                else:
                    return go.Figure().add_annotation(text="No sentiment column", showarrow=False)
            except Exception as e:
                print(f"Error in sentiment pie: {e}")
                return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)
        
        # BIỂU ĐỒ MỚI: Monthly Analysis
        @self.app.callback(
            Output('monthly-chart', 'figure'),
            [Input('monthly-chart', 'id'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_monthly_chart(id, n):
            df = self.load_data()
            if df.empty or 'month_str' not in df.columns:
                return go.Figure().add_annotation(text="No monthly data available", showarrow=False)
            
            try:
                if 'sentiment' in df.columns:
                    monthly_data = df.groupby(['month_str', 'sentiment']).size().unstack(fill_value=0)
                    
                    fig = go.Figure()
                    
                    for sentiment in ['positive', 'negative', 'neutral']:
                        if sentiment in monthly_data.columns:
                            fig.add_trace(go.Bar(
                                name=sentiment.capitalize(),
                                x=monthly_data.index,
                                y=monthly_data[sentiment],
                                marker_color=self.COLORS[sentiment]
                            ))
                    
                    fig.update_layout(
                        barmode='group',
                        xaxis_title="Tháng",
                        yaxis_title="Số lượng posts",
                        template='plotly_white',
                        height=400,
                        hovermode='x unified',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    return fig
                else:
                    monthly_counts = df['month_str'].value_counts().sort_index()
                    fig = go.Figure(data=[go.Bar(
                        x=monthly_counts.index,
                        y=monthly_counts.values,
                        marker_color=self.COLORS['primary']
                    )])
                    fig.update_layout(
                        xaxis_title="Tháng",
                        yaxis_title="Số lượng posts",
                        template='plotly_white',
                        height=400
                    )
                    return fig
            except Exception as e:
                print(f"Error in monthly chart: {e}")
                return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)
        
        # BIỂU ĐỒ MỚI: Sentiment Score Distribution
        @self.app.callback(
            Output('sentiment-score-dist', 'figure'),
            [Input('sentiment-score-dist', 'id'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_sentiment_score_dist(id, n):
            df = self.load_data()
            if df.empty or 'sentiment_score' not in df.columns:
                return go.Figure().add_annotation(text="No sentiment score data", showarrow=False)
            
            try:
                fig = go.Figure()
                
                # Histogram
                fig.add_trace(go.Histogram(
                    x=df['sentiment_score'],
                    nbinsx=30,
                    marker_color=self.COLORS['info'],
                    opacity=0.7,
                    name='Distribution'
                ))
                
                # Add vertical lines for mean
                mean_score = df['sentiment_score'].mean()
                fig.add_vline(x=mean_score, line_dash="dash", line_color="red",
                             annotation_text=f"Mean: {mean_score:.3f}")
                
                fig.update_layout(
                    xaxis_title="Sentiment Score",
                    yaxis_title="Frequency",
                    template='plotly_white',
                    height=400,
                    showlegend=False
                )
                return fig
            except Exception as e:
                print(f"Error in sentiment score distribution: {e}")
                return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)
        
        # Hashtag chart
        @self.app.callback(
            Output('hashtag-chart', 'figure'),
            [Input('hashtag-chart', 'id'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_hashtag_chart(id, n):
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
                marker_color=self.COLORS['primary'],
                text=hashtag_counts.values,
                textposition='outside'
            )])
            
            fig.update_layout(
                xaxis_title="Số lần xuất hiện",
                yaxis_title="",
                height=400,
                template='plotly_white',
                yaxis={'categoryorder': 'total ascending'}
            )
            
            return fig
        
        # Topic sentiment chart
        @self.app.callback(
            Output('topic-sentiment-chart', 'figure'),
            [Input('topic-sentiment-chart', 'id'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_topic_sentiment_chart(id, n):
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
                xaxis_title="Chủ đề",
                yaxis_title="Số lượng posts",
                barmode='stack',
                height=400,
                template='plotly_white',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            return fig
        
        # BIỂU ĐỒ MỚI: Engagement Analysis
        @self.app.callback(
            Output('engagement-chart', 'figure'),
            [Input('engagement-chart', 'id'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_engagement_chart(id, n):
            df = self.load_data()
            if df.empty or 'likes' not in df.columns:
                return go.Figure().add_annotation(text="No engagement data available", showarrow=False)
            
            try:
                # Create engagement metrics
                engagement_data = []
                
                if 'likes' in df.columns:
                    engagement_data.append({
                        'metric': 'Likes',
                        'total': df['likes'].sum(),
                        'avg': df['likes'].mean()
                    })
                
                if 'retweets' in df.columns:
                    engagement_data.append({
                        'metric': 'Retweets',
                        'total': df['retweets'].sum(),
                        'avg': df['retweets'].mean()
                    })
                
                if 'replies' in df.columns:
                    engagement_data.append({
                        'metric': 'Replies',
                        'total': df['replies'].sum(),
                        'avg': df['replies'].mean()
                    })
                
                if 'num_comments' in df.columns:
                    engagement_data.append({
                        'metric': 'Comments',
                        'total': df['num_comments'].sum(),
                        'avg': df['num_comments'].mean()
                    })
                
                if not engagement_data:
                    return go.Figure().add_annotation(text="No engagement metrics found", showarrow=False)
                
                eng_df = pd.DataFrame(engagement_data)
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Total',
                    x=eng_df['metric'],
                    y=eng_df['total'],
                    marker_color=self.COLORS['primary'],
                    yaxis='y',
                    offsetgroup=1,
                    text=eng_df['total'].apply(lambda x: f"{x:,.0f}"),
                    textposition='outside'
                ))
                
                fig.add_trace(go.Bar(
                    name='Average',
                    x=eng_df['metric'],
                    y=eng_df['avg'],
                    marker_color=self.COLORS['warning'],
                    yaxis='y2',
                    offsetgroup=2,
                    text=eng_df['avg'].apply(lambda x: f"{x:.1f}"),
                    textposition='outside'
                ))
                
                fig.update_layout(
                    xaxis_title="Engagement Metric",
                    yaxis=dict(title="Total", side='left'),
                    yaxis2=dict(title="Average", side='right', overlaying='y'),
                    barmode='group',
                    height=400,
                    template='plotly_white',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                return fig
            except Exception as e:
                print(f"Error in engagement chart: {e}")
                return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)
        
        # BIỂU ĐỒ MỚI: Source Distribution
        @self.app.callback(
            Output('source-chart', 'figure'),
            [Input('source-chart', 'id'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_source_chart(id, n):
            df = self.load_data()
            if df.empty or 'source' not in df.columns:
                return go.Figure().add_annotation(text="No source data available", showarrow=False)
            
            try:
                source_counts = df['source'].value_counts()
                
                colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
                
                fig = go.Figure(data=[go.Pie(
                    labels=source_counts.index,
                    values=source_counts.values,
                    marker=dict(colors=colors[:len(source_counts)]),
                    textinfo='label+percent',
                    textfont_size=12,
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
                )])
                
                fig.update_layout(
                    height=400,
                    template='plotly_white',
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5)
                )
                
                return fig
            except Exception as e:
                print(f"Error in source chart: {e}")
                return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)
        
        # BẢNG MỚI: Recent Posts Table
        @self.app.callback(
            Output('recent-posts-table', 'children'),
            [Input('recent-posts-table', 'id'),
             Input('refresh-posts-btn', 'n_clicks'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_recent_posts_table(id, n_clicks, n_intervals):
            df = self.load_data()
            
            if df.empty:
                return dbc.Alert("No posts available in database", color="info", className="text-center")
            
            try:
                # Sort by created_at (newest first) and get top 20
                if 'created_at' in df.columns:
                    df_sorted = df.sort_values('created_at', ascending=False).head(20)
                else:
                    df_sorted = df.head(20)
                
                # Prepare data for display
                table_data = []
                for idx, row in df_sorted.iterrows():
                    # Get raw text and handle empty/null values
                    raw_text = row.get('text', '')
                    if pd.isna(raw_text) or not raw_text or str(raw_text).strip() == '':
                        raw_text = 'No content available'
                    else:
                        raw_text = str(raw_text).strip()
                    
                    # Truncate text for display but keep original for length calculation
                    display_text = raw_text[:150] + '...' if len(raw_text) > 150 else raw_text
                    
                    # Format date
                    if 'created_at' in row and pd.notna(row['created_at']):
                        date_str = pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')
                    else:
                        date_str = 'N/A'
                    
                    # Get sentiment info
                    sentiment = row.get('sentiment', 'neutral')
                    sentiment_score = row.get('sentiment_score', 0.0)
                    
                    # Get source
                    source = row.get('source', 'unknown')
                    
                    # Get engagement
                    likes = row.get('likes', 0)
                    
                    table_data.append({
                        'date': date_str,
                        'text': display_text,
                        'raw_text': raw_text,  # Keep original for debugging
                        'sentiment': sentiment,
                        'score': sentiment_score,
                        'source': source,
                        'likes': likes
                    })
                
                # Create table rows
                table_rows = []
                for i, post in enumerate(table_data, 1):
                    # Sentiment badge color
                    if post['sentiment'] == 'positive':
                        badge_color = 'success'
                        badge_icon = '😊'
                    elif post['sentiment'] == 'negative':
                        badge_color = 'danger'
                        badge_icon = '😞'
                    else:
                        badge_color = 'secondary'
                        badge_icon = '😐'
                    
                    # Ensure text is not empty and properly formatted
                    display_text = post['text'] if post['text'] and post['text'].strip() else 'No content available'
                    if display_text == 'No content extracted':
                        display_text = '⚠️ Content extraction failed'
                    
                    table_rows.append(
                        html.Tr([
                            html.Td(str(i), style={'fontWeight': 'bold', 'textAlign': 'center', 'width': '50px'}),
                            html.Td(post['date'], style={'width': '150px', 'fontSize': '12px'}),
                            html.Td(
                                html.Div([
                                    html.P(display_text, style={'margin': '0', 'fontSize': '13px', 'lineHeight': '1.4'}),
                                    html.Small(f"Length: {len(post.get('raw_text', post['text']))} chars", style={'color': '#6c757d', 'fontSize': '11px'})
                                ]),
                                style={'maxWidth': '400px', 'wordWrap': 'break-word'}
                            ),
                            html.Td([
                                dbc.Badge(
                                    [badge_icon, f" {post['sentiment'].capitalize()}"],
                                    color=badge_color,
                                    className="me-1"
                                ),
                                html.Br(),
                                html.Small(f"Score: {post['score']:.3f}", style={'color': '#7f8c8d'})
                            ], style={'textAlign': 'center', 'width': '120px'}),
                            html.Td(
                                dbc.Badge(post['source'], color='info', pill=True),
                                style={'textAlign': 'center', 'width': '100px'}
                            ),
                            html.Td(
                                [html.I(className="fas fa-heart", style={'color': '#e74c3c'}), f" {post['likes']}"],
                                style={'textAlign': 'center', 'width': '80px'}
                            )
                        ], style={'borderBottom': '1px solid #dee2e6'})
                    )
                
                table = dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("#", style={'textAlign': 'center', 'backgroundColor': '#34495e', 'color': 'white'}),
                            html.Th("Date", style={'backgroundColor': '#34495e', 'color': 'white'}),
                            html.Th("Content", style={'backgroundColor': '#34495e', 'color': 'white'}),
                            html.Th("Sentiment", style={'textAlign': 'center', 'backgroundColor': '#34495e', 'color': 'white'}),
                            html.Th("Source", style={'textAlign': 'center', 'backgroundColor': '#34495e', 'color': 'white'}),
                            html.Th("Likes", style={'textAlign': 'center', 'backgroundColor': '#34495e', 'color': 'white'})
                        ])
                    ]),
                    html.Tbody(table_rows)
                ], bordered=True, hover=True, responsive=True, striped=True, className="mb-0")
                
                return html.Div([
                    dbc.Alert([
                        html.I(className="fas fa-info-circle me-2"),
                        f"Showing {len(table_data)} most recent posts out of {len(df)} total posts"
                    ], color="info", className="mb-3"),
                    table
                ])
                
            except Exception as e:
                print(f"Error creating posts table: {e}")
                return dbc.Alert(f"Error loading posts: {str(e)}", color="danger")
        
        # URL Crawler callbacks (giữ nguyên như cũ)
        @self.app.callback(
            Output('crawl-status', 'children'),
            Input('crawl-button', 'n_clicks'),
            State('url-input', 'value'),
            State('topic-input', 'value'),
            prevent_initial_call=True
        )
        def crawl_single_url(n_clicks, url, topic):
            if not url:
                return dbc.Alert("⚠ Please enter a URL", color="warning")
            
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
                    html.H5(f"Batch Crawl Completed!", className="alert-heading"),
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
                    html.H5("Batch Crawl Error", className="alert-heading"),
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
                            html.Th("Platform", style={'width': '100px', 'textAlign': 'center'}),
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
                                dbc.Badge(r.get('platform', 'unknown'), color='primary', pill=True),
                                style={'textAlign': 'center'}
                            ),
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
        
        # Auto Crawler Callbacks
        @self.app.callback(
            Output('quick-collection-status', 'children'),
            [Input('quick-google-btn', 'n_clicks'),
             Input('quick-reddit-btn', 'n_clicks'),
             Input('quick-medium-btn', 'n_clicks'),
             Input('quick-stackoverflow-btn', 'n_clicks'),
             Input('quick-hackernews-btn', 'n_clicks'),
             Input('quick-all-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def handle_quick_collection(google_clicks, reddit_clicks, medium_clicks, stackoverflow_clicks, hackernews_clicks, all_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                return ""
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            try:
                if button_id == 'quick-google-btn':
                    return self._collect_google_news()
                elif button_id == 'quick-reddit-btn':
                    return self._collect_reddit()
                elif button_id == 'quick-medium-btn':
                    return self._collect_medium()
                elif button_id == 'quick-stackoverflow-btn':
                    return self._collect_stackoverflow()
                elif button_id == 'quick-hackernews-btn':
                    return self._collect_hackernews()
                elif button_id == 'quick-all-btn':
                    return self._collect_all_sources()
            except Exception as e:
                return dbc.Alert(f"❌ Error: {str(e)}", color="danger")
        
        @self.app.callback(
            Output('custom-collection-status', 'children'),
            Input('custom-collect-btn', 'n_clicks'),
            State('source-dropdown', 'value'),
            State('custom-count-input', 'value'),
            State('custom-keywords-input', 'value'),
            prevent_initial_call=True
        )
        def handle_custom_collection(n_clicks, source, count, keywords):
            if not keywords:
                return dbc.Alert("⚠ Please enter keywords", color="warning")
            
            try:
                return self._collect_custom(source, count, keywords)
            except Exception as e:
                return dbc.Alert(f"❌ Error: {str(e)}", color="danger")
        
        @self.app.callback(
            Output('collection-stats', 'children'),
            [Input('quick-collection-status', 'children'),
             Input('custom-collection-status', 'children'),
             Input('auto-refresh-interval', 'n_intervals')]
        )
        def update_collection_stats(quick_status, custom_status, n_intervals):
            try:
                total_posts = self.posts_collection.count_documents({})
                today_posts = self.posts_collection.count_documents({
                    'created_at': {'$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
                })
                
                sources = list(self.posts_collection.aggregate([
                    {'$group': {'_id': '$source', 'count': {'$sum': 1}}},
                    {'$sort': {'count': -1}}
                ]))
                
                return [
                    html.H5(f"📊 {total_posts:,}", className="text-primary mb-1"),
                    html.P("Total Posts", className="text-muted mb-2"),
                    html.H6(f"📅 {today_posts:,}", className="text-success mb-1"),
                    html.P("Today", className="text-muted mb-3"),
                    html.Hr(),
                    html.P("Sources:", className="fw-bold mb-2"),
                ] + [
                    html.P(f"• {s['_id']}: {s['count']:,}", className="small mb-1")
                    for s in sources[:5]
                ]
            except Exception as e:
                return [html.P(f"Error: {str(e)}", className="text-danger")]
        
        @self.app.callback(
            Output('collection-history-table', 'children'),
            Output('history-count-badge', 'children'),
            Input('history-refresh-interval', 'n_intervals')
        )
        def update_collection_history(n_intervals):
            try:
                # Get recent collection activities from posts
                recent_posts = list(self.posts_collection.find(
                    {}, 
                    {'source': 1, 'created_at': 1, 'topic': 1}
                ).sort('created_at', -1).limit(20))
                
                if not recent_posts:
                    return html.P("No collection history yet", className="text-muted text-center p-4"), "0"
                
                table_rows = []
                for idx, post in enumerate(recent_posts, 1):
                    source_icon = {
                        'google_news': '📰',
                        'reddit': '🔴',
                        'medium': '📝',
                        'stackoverflow': '💻',
                        'hackernews': '🚀',
                        'url_crawler': '🔗'
                    }.get(post.get('source', ''), '❓')
                    
                    created_at = post.get('created_at', datetime.now())
                    if isinstance(created_at, str):
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    table_rows.append(
                        html.Tr([
                            html.Td(str(idx)),
                            html.Td([source_icon, f" {post.get('source', 'unknown')}"], style={'width': '150px'}),
                            html.Td(post.get('topic', 'N/A')[:30] + ('...' if len(post.get('topic', '')) > 30 else '')),
                            html.Td(created_at.strftime('%H:%M:%S'), style={'width': '100px'})
                        ])
                    )
                
                table = dbc.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("#", style={'width': '50px'}),
                            html.Th("Source"),
                            html.Th("Topic"),
                            html.Th("Time")
                        ])
                    ], className="table-dark"),
                    html.Tbody(table_rows)
                ], bordered=True, hover=True, responsive=True, striped=True, size='sm')
                
                return table, str(len(recent_posts))
            except Exception as e:
                return html.P(f"Error: {str(e)}", className="text-danger"), "0"
    
    def _collect_google_news(self):
        """Collect from Google News"""
        try:
            from data_collection.google_news_crawler import GoogleNewsCrawler
            from analysis.sentiment_analyzer import SentimentAnalyzer
            
            crawler = GoogleNewsCrawler(self.db)
            initial_count = self.posts_collection.count_documents({})
            
            crawler.collect_topics(["AI education", "artificial intelligence education"], max_results_per_query=15)
            
            final_count = self.posts_collection.count_documents({})
            new_posts = final_count - initial_count
            
            # Analyze sentiment for new posts
            analyzer = SentimentAnalyzer(self.db)
            analyzer.analyze_all_posts()
            
            return dbc.Alert([
                html.H5("✅ Google News Collection Complete!", className="alert-heading"),
                html.P(f"Collected {new_posts} new posts")
            ], color="success", dismissable=True)
        except Exception as e:
            return dbc.Alert(f"❌ Google News Error: {str(e)}", color="danger")
    
    def _collect_reddit(self):
        """Collect from Reddit"""
        try:
            from data_collection.reddit_crawler import RedditCrawler
            from analysis.sentiment_analyzer import SentimentAnalyzer
            
            crawler = RedditCrawler(
                db=self.db,
                client_id=os.getenv('REDDIT_CLIENT_ID', 'k6ozqL3mwwC0cGNUSmcdlQ'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET', 'JR6XLrrWpp2oNi5RNk0uV2GrrCaelw'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'windows:ai-trend-collector:v2.0')
            )
            initial_count = self.posts_collection.count_documents({})
            
            crawler.collect_topics(['AI education', 'EdTech'], limit_per_topic=15)
            
            final_count = self.posts_collection.count_documents({})
            new_posts = final_count - initial_count
            
            analyzer = SentimentAnalyzer(self.db)
            analyzer.analyze_all_posts()
            
            return dbc.Alert([
                html.H5("✅ Reddit Collection Complete!", className="alert-heading"),
                html.P(f"Collected {new_posts} new posts")
            ], color="success", dismissable=True)
        except Exception as e:
            return dbc.Alert(f"❌ Reddit Error: {str(e)}", color="danger")
    
    def _collect_medium(self):
        """Collect from Medium"""
        try:
            from data_collection.medium_crawler import MediumCrawler
            from analysis.sentiment_analyzer import SentimentAnalyzer
            
            crawler = MediumCrawler(self.db)
            initial_count = self.posts_collection.count_documents({})
            
            crawler.collect_topics(['artificial-intelligence', 'machine-learning'], max_results_per_tag=10)
            
            final_count = self.posts_collection.count_documents({})
            new_posts = final_count - initial_count
            
            analyzer = SentimentAnalyzer(self.db)
            analyzer.analyze_all_posts()
            
            return dbc.Alert([
                html.H5("✅ Medium Collection Complete!", className="alert-heading"),
                html.P(f"Collected {new_posts} new posts")
            ], color="success", dismissable=True)
        except Exception as e:
            return dbc.Alert(f"❌ Medium Error: {str(e)}", color="danger")
    
    def _collect_stackoverflow(self):
        """Collect from Stack Overflow"""
        try:
            from data_collection.stackoverflow_crawler import StackOverflowCrawler
            from analysis.sentiment_analyzer import SentimentAnalyzer
            
            crawler = StackOverflowCrawler(self.db)
            initial_count = self.posts_collection.count_documents({})
            
            crawler.collect_topics(['machine-learning', 'artificial-intelligence'], max_results_per_tag=15)
            
            final_count = self.posts_collection.count_documents({})
            new_posts = final_count - initial_count
            
            analyzer = SentimentAnalyzer(self.db)
            analyzer.analyze_all_posts()
            
            return dbc.Alert([
                html.H5("✅ Stack Overflow Collection Complete!", className="alert-heading"),
                html.P(f"Collected {new_posts} new posts")
            ], color="success", dismissable=True)
        except Exception as e:
            return dbc.Alert(f"❌ Stack Overflow Error: {str(e)}", color="danger")
    
    def _collect_hackernews(self):
        """Collect from Hacker News"""
        try:
            from data_collection.hackernews_crawler import HackerNewsCrawler
            from analysis.sentiment_analyzer import SentimentAnalyzer
            
            crawler = HackerNewsCrawler(self.db)
            initial_count = self.posts_collection.count_documents({})
            
            crawler.collect_topics(['AI education', 'EdTech'], max_results_per_query=10)
            
            final_count = self.posts_collection.count_documents({})
            new_posts = final_count - initial_count
            
            analyzer = SentimentAnalyzer(self.db)
            analyzer.analyze_all_posts()
            
            return dbc.Alert([
                html.H5("✅ Hacker News Collection Complete!", className="alert-heading"),
                html.P(f"Collected {new_posts} new posts")
            ], color="success", dismissable=True)
        except Exception as e:
            return dbc.Alert(f"❌ Hacker News Error: {str(e)}", color="danger")
    
    def _collect_all_sources(self):
        """Collect from all sources"""
        try:
            initial_count = self.posts_collection.count_documents({})
            results = []
            
            # Collect from each source
            sources = [
                ('Google News', self._collect_google_news),
                ('Reddit', self._collect_reddit),
                ('Medium', self._collect_medium),
                ('Stack Overflow', self._collect_stackoverflow),
                ('Hacker News', self._collect_hackernews)
            ]
            
            for source_name, collect_func in sources:
                try:
                    collect_func()
                    results.append(f"✅ {source_name}")
                except Exception as e:
                    results.append(f"❌ {source_name}: {str(e)[:50]}")
            
            final_count = self.posts_collection.count_documents({})
            total_new = final_count - initial_count
            
            return dbc.Alert([
                html.H5("🚀 All Sources Collection Complete!", className="alert-heading"),
                html.P(f"Total new posts: {total_new}"),
                html.Hr(),
                html.Ul([html.Li(result) for result in results])
            ], color="success", dismissable=True)
        except Exception as e:
            return dbc.Alert(f"❌ All Sources Error: {str(e)}", color="danger")
    
    def _collect_custom(self, source, count, keywords):
        """Custom collection based on parameters"""
        try:
            from analysis.sentiment_analyzer import SentimentAnalyzer
            
            # Validate parameters
            if not count or count <= 0:
                count = 20  # Default value
            if count > 200:
                count = 200  # Max limit
            
            initial_count = self.posts_collection.count_documents({})
            keywords_list = [k.strip() for k in keywords.split(',')]
            per_keyword = max(1, count // len(keywords_list))
            
            if source == 'google':
                from data_collection.google_news_crawler import GoogleNewsCrawler
                crawler = GoogleNewsCrawler(self.db)
                crawler.collect_topics(keywords_list, max_results_per_query=per_keyword)
            elif source == 'reddit':
                from data_collection.reddit_crawler import RedditCrawler
                crawler = RedditCrawler(
                    db=self.db,
                    client_id=os.getenv('REDDIT_CLIENT_ID', 'k6ozqL3mwwC0cGNUSmcdlQ'),
                    client_secret=os.getenv('REDDIT_CLIENT_SECRET', 'JR6XLrrWpp2oNi5RNk0uV2GrrCaelw'),
                    user_agent=os.getenv('REDDIT_USER_AGENT', 'windows:ai-trend-collector:v2.0')
                )
                crawler.collect_topics(keywords_list, limit_per_topic=per_keyword)
            elif source == 'medium':
                from data_collection.medium_crawler import MediumCrawler
                crawler = MediumCrawler(self.db)
                crawler.collect_topics(keywords_list, max_results_per_tag=per_keyword)
            elif source == 'stackoverflow':
                from data_collection.stackoverflow_crawler import StackOverflowCrawler
                crawler = StackOverflowCrawler(self.db)
                crawler.collect_topics(keywords_list, max_results_per_tag=per_keyword)
            elif source == 'hackernews':
                from data_collection.hackernews_crawler import HackerNewsCrawler
                crawler = HackerNewsCrawler(self.db)
                crawler.collect_topics(keywords_list, max_results_per_query=per_keyword)
            
            final_count = self.posts_collection.count_documents({})
            new_posts = final_count - initial_count
            
            analyzer = SentimentAnalyzer(self.db)
            analyzer.analyze_all_posts()
            
            return dbc.Alert([
                html.H5(f"✅ Custom Collection Complete!", className="alert-heading"),
                html.P(f"Source: {source.title()}"),
                html.P(f"Keywords: {keywords}"),
                html.P(f"Collected: {new_posts} new posts")
            ], color="success", dismissable=True)
        except Exception as e:
            return dbc.Alert(f"❌ Custom Collection Error: {str(e)}", color="danger")
    
    def run(self, debug=True, port=8055):
        """Run the dashboard"""
        print("\n" + "="*60)
        print("Starting Dashboard...")
        print("="*60)
        print(f"Dashboard URL: http://127.0.0.1:{port}")
        print(f"Features:")
        print(f"   - Overview Tab: Enhanced data visualization")
        print(f"   - Auto Crawler Tab: Automated data collection from all sources")
        print(f"   - URL Crawler Tab: Import content from URLs")
        print(f"   - Real-time collection status and history")
        print(f"   - Auto-refresh: Every 30 seconds")
        print("="*60 + "\n")
        try:
            self.app.run_server(debug=debug, port=port, host='127.0.0.1')
        except OSError as e:
            print(f"Port {port} is busy, trying port {port+1}")
            self.app.run_server(debug=debug, port=port+1, host='127.0.0.1')
            