"""Dash page for URL input and crawling"""
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def create_url_input_layout():
    """Tạo layout cho URL input"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Import Content từ URL", className="mb-4"),
                html.P("Nhập URL của bài viết để tự động thu thập và phân tích"),
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Single URL Input"),
                    dbc.CardBody([
                        dbc.Input(
                            id='url-input',
                            type='url',
                            placeholder='https://twitter.com/...',
                            className='mb-3'
                        ),
                        dbc.Input(
                            id='topic-input',
                            type='text',
                            placeholder='Topic/Category (optional)',
                            className='mb-3'
                        ),
                        dbc.Button(
                            "Crawl URL",
                            id='crawl-button',
                            color='primary',
                            className='me-2'
                        ),
                        html.Div(id='crawl-status', className='mt-3')
                    ])
                ], className='mb-4')
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(" Multiple URLs Input"),
                    dbc.CardBody([
                        dcc.Textarea(
                            id='urls-textarea',
                            placeholder='Paste multiple URLs (one per line)',
                            style={'width': '100%', 'height': 150},
                            className='mb-3'
                        ),
                        dbc.Input(
                            id='batch-topic-input',
                            type='text',
                            placeholder='Topic for all URLs',
                            className='mb-3'
                        ),
                        dbc.Button(
                            "Crawl All URLs",
                            id='crawl-batch-button',
                            color='success'
                        ),
                        html.Div(id='batch-crawl-status', className='mt-3')
                    ])
                ])
            ], width=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recently Crawled URLs"),
                    dbc.CardBody([
                        html.Div(id='recent-urls-table')
                    ])
                ])
            ])
        ], className='mt-4')
    ], fluid=True)