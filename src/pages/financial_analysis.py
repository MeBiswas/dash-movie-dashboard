# src/pages/financial_analysis.py

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

from src.utils.data_loader import load_movies
from src.callbacks.financial_callbacks import register_callbacks as register_financial_callbacks

def _build_filters_card(df):
    # Safely calculate ranges
    prof_min = 0
    prof_max = 100_000_000
    bud_min = 0
    bud_max = 200_000_000
    
    if 'Profit (USD)' in df.columns and df['Profit (USD)'].notna().any():
        prof_min = int(df['Profit (USD)'].min())
        prof_max = int(df['Profit (USD)'].max())
        
    if 'Production Budget (USD)' in df.columns and df['Production Budget (USD)'].notna().any():
        bud_min = int(df['Production Budget (USD)'].min())
        bud_max = int(df['Production Budget (USD)'].max())

    genres = []
    if 'Genre' in df.columns and not df.empty:
        genres = sorted(df['Genre'].dropna().unique())

    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Profit Range (USD)"),
                    dcc.RangeSlider(
                        id="filter-profit",
                        min=prof_min,
                        max=prof_max,
                        step=max(1, (prof_max - prof_min) // 100),
                        value=[prof_min, prof_max],
                        tooltip={"placement": "bottom", "always_visible": True},
                        marks={prof_min: f"${prof_min:,}", prof_max: f"${prof_max:,}"}
                    )
                ], md=6),
                dbc.Col([
                    dbc.Label("Budget Range (USD)"),
                    dcc.RangeSlider(
                        id="filter-budget",
                        min=bud_min,
                        max=bud_max,
                        step=max(1, (bud_max - bud_min) // 100),
                        value=[bud_min, bud_max],
                        tooltip={"placement": "bottom", "always_visible": True},
                        marks={bud_min: f"${bud_min:,}", bud_max: f"${bud_max:,}"}
                    )
                ], md=6),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("ROI Category"),
                    dcc.Dropdown(
                        id="filter-roi-cat",
                        options=[
                            {"label": "All ROI", "value": "all"},
                            {"label": "High (> 100%)", "value": "high"},
                            {"label": "Moderate (0–100%)", "value": "moderate"},
                            {"label": "Low (< 0%)", "value": "low"},
                        ],
                        value="all",
                        clearable=False
                    )
                ], md=4),

                dbc.Col([
                    dbc.Label("Genre (Optional)"),
                    dcc.Dropdown(
                        id="filter-genre-fin",
                        options=[{"label": g, "value": g} for g in genres],
                        multi=True,
                        placeholder="Select genres...",
                        clearable=True
                    )
                ], md=8),
            ]),
        ]),
        class_name="mb-3"
    )

def layout(app):
    df = load_movies()
    
    header = dbc.Container([
        html.H2("Financial Analysis", className="mb-2"),
        html.P("Profitability & ROI insights across movies and genres", className="text-muted")
    ], className="my-4")
    
    # Collapsible filter area
    filters_card = _build_filters_card(df)
    filter_collapse = html.Div([
        dbc.Button(
            "📊 Show Filters", 
            id="btn-toggle-fin-filters", 
            color="primary", 
            size="sm", 
            className="mb-3",
            outline=True
        ),
        dbc.Collapse(filters_card, id="collapse-fin-filters", is_open=True)  # Start open for better UX
    ])

    top_kpis = dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6("Total Profit", className="card-title text-muted"),
                    html.H3(id='kpi-total-profit', className="card-text text-success")
                ])
            ), 
            md=4
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6("Average ROI (%)", className="card-title text-muted"),
                    html.H3(id='kpi-avg-roi', className="card-text text-primary")
                ])
            ), 
            md=4
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6("Most Profitable Movie", className="card-title text-muted"),
                    html.H3(id='kpi-top-profit', className="card-text text-info", style={"fontSize": "1.5rem"})
                ])
            ), 
            md=4
        ),
    ], className='mb-4')

    # Charts
    charts = dbc.Row([
        dbc.Col(
            dcc.Graph(id='chart-profit-vs-budget'), 
            md=6,
            className="mb-3"
        ),
        dbc.Col(
            dcc.Graph(id='chart-roi-genre'), 
            md=6,
            className="mb-3"
        ),
    ])

    more_charts = dbc.Row([
        dbc.Col(
            dcc.Graph(id='chart-roi-distribution'), 
            md=6,
            className="mb-3"
        ),
        dbc.Col(
            dcc.Graph(id='chart-fin-corr'), 
            md=6,
            className="mb-3"
        ),
    ])
    
    return html.Div([
        header, 
        filter_collapse, 
        top_kpis, 
        charts, 
        more_charts
    ], className="container-fluid")

def register_callbacks(app):
    @app.callback(
        Output("collapse-fin-filters", "is_open"),
        Input("btn-toggle-fin-filters", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_filters(n):
        if n is None:
            return True
        return n % 2 == 1
    
    register_financial_callbacks(app)