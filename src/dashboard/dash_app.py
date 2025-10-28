"""Dash dashboard for social media analysis"""
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

class DashboardApp:
    def __init__(self, db):
        self.db = db
        self.posts_collection = db['posts']
        self.trends_collection = db['trends']
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
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
                # Create default date columns if none exist
                df['date'] = pd.Timestamp.now().date()
                df['month'] = pd.Timestamp.now().month
                df['year'] = pd.Timestamp.now().year
            
            # Ensure required columns exist with default values
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
    
    def setup_layout(self):
        """Setup dashboard layout"""
        try:
            df = self.load_data()
            trend_data = self.trends_collection.find_one()
        except Exception as e:
            print(f"Error in setup_layout: {e}")
            df = pd.DataFrame()
            trend_data = None
        
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("📊 Dashboard Phân tích Dữ liệu Xã hội", 
                           className="text-center mb-4 mt-4",
                           style={'color': '#2c3e50', 'fontWeight': 'bold'}),
                    html.H5("Chủ đề: AI trong Giáo dục", 
                           className="text-center mb-4",
                           style={'color': '#7f8c8d'})
                ])
            ]),
            
            # Summary Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📝 Tổng Posts", className="card-title"),
                            html.H2(f"{len(df):,}" if not df.empty else "0", style={'color': '#3498db'})
                        ])
                    ], style={'backgroundColor': self.COLORS['card']})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("😊 Tích cực", className="card-title"),
                            html.H2(f"{len(df[df['sentiment']=='positive']) if not df.empty and 'sentiment' in df.columns else 0:,}", 
                                   style={'color': self.COLORS['positive']})
                        ])
                    ], style={'backgroundColor': self.COLORS['card']})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("😞 Tiêu cực", className="card-title"),
                            html.H2(f"{len(df[df['sentiment']=='negative']) if not df.empty and 'sentiment' in df.columns else 0:,}", 
                                   style={'color': self.COLORS['negative']})
                        ])
                    ], style={'backgroundColor': self.COLORS['card']})
                ], width=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("😐 Trung lập", className="card-title"),
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
                        dbc.CardHeader("📈 Xu hướng thảo luận theo thời gian"),
                        dbc.CardBody([
                            dcc.Graph(id='timeline-chart')
                        ])
                    ])
                ], width=8),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🎯 Phân bố cảm xúc"),
                        dbc.CardBody([
                            dcc.Graph(id='sentiment-pie')
                        ])
                    ])
                ], width=4),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🔥 Top 15 Hashtags"),
                        dbc.CardBody([
                            dcc.Graph(id='hashtag-chart')
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Cảm xúc theo chủ đề"),
                        dbc.CardBody([
                            dcc.Graph(id='topic-sentiment-chart')
                        ])
                    ])
                ], width=6),
            ], className="mb-4"),
            
        ], fluid=True, style={'backgroundColor': self.COLORS['background']})
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
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
            
            # Extract hashtags
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
    
    def run(self, debug=True, port=8050):
        """Run the dashboard"""
        print("\nStarting Dashboard...")
        print(f"Dashboard URL: http://127.0.0.1:{port}")
        try:
            self.app.run_server(debug=debug, port=port, host='127.0.0.1')
        except OSError as e:
            print(f"Port {port} is busy, trying port {port+1}")
            self.app.run_server(debug=debug, port=port+1, host='127.0.0.1')