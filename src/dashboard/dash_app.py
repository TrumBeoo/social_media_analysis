# src/dashboard/dash_app.py - PHIÊN BẢN NÂNG CẤP
"""Dash dashboard for social media analysis - Enhanced Version"""
import dash
from dash import dcc, html, Input, Output, State, dash_table
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
    
    def create_url_crawler_tab(self):
        """Tab URL Crawler"""
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
            
            # Tab content containers
            html.Div(id='overview-tab-content', children=self.create_overview_tab()),
            html.Div(id='crawler-tab-content', children=self.create_url_crawler_tab(), style={'display': 'none'})
            
        ], fluid=True, style={'backgroundColor': self.COLORS['background'], 'minHeight': '100vh'})
    
    def setup_callbacks(self):
        """Setup all callbacks"""
        
        # Tab switching
        @self.app.callback(
            Output('overview-tab-content', 'style'),
            Output('crawler-tab-content', 'style'),
            Input('tabs', 'active_tab')
        )
        def switch_tab(active_tab):
            if active_tab == "overview-tab":
                return {'display': 'block'}, {'display': 'none'}
            elif active_tab == "crawler-tab":
                return {'display': 'none'}, {'display': 'block'}
            return {'display': 'block'}, {'display': 'none'}
        
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
                    # Truncate text
                    text = str(row.get('text', ''))[:150] + '...' if len(str(row.get('text', ''))) > 150 else str(row.get('text', ''))
                    
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
                        'text': text,
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
                    
                    table_rows.append(
                        html.Tr([
                            html.Td(str(i), style={'fontWeight': 'bold', 'textAlign': 'center', 'width': '50px'}),
                            html.Td(post['date'], style={'width': '150px', 'fontSize': '12px'}),
                            html.Td(post['text'], style={'fontSize': '13px'}),
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
    
    def run(self, debug=True, port=8055):
        """Run the dashboard"""
        print("\n" + "="*60)
        print("Starting Dashboard...")
        print("="*60)
        print(f"Dashboard URL: http://127.0.0.1:{port}")
        print(f"Features:")
        print(f"   - Overview Tab: Enhanced data visualization")
        print(f"   - Monthly Analysis: Trends by month")
        print(f"   - Recent Posts Table: 20 newest posts with sentiment")
        print(f"   - URL Crawler Tab: Import content from URLs")
        print(f"   - Auto-refresh: Every 30 seconds")
        print("="*60 + "\n")
        try:
            self.app.run_server(debug=debug, port=port, host='127.0.0.1')
        except OSError as e:
            print(f"Port {port} is busy, trying port {port+1}")
            self.app.run_server(debug=debug, port=port+1, host='127.0.0.1')
            