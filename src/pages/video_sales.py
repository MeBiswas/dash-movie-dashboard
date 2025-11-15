# src/pages/video_sales.py

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

from src.utils.data_loader import load_movies
from src.callbacks.video_callbacks import register_callbacks as register_video_callbacks

def _build_filters_card(df):
    # Safely get years
    years = []
    if 'Year' in df.columns and not df.empty:
        years = sorted(df['Year'].dropna().unique())
        years = [int(y) for y in years if str(y).isdigit()]
    
    year_min = int(min(years)) if years else 2000
    year_max = int(max(years)) if years else 2025
    
    # Safely get studios
    studios = []
    if 'Production/Financing Companies' in df.columns and not df.empty:
        studios = sorted(df['Production/Financing Companies'].dropna().unique())

    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Only movies with video sales"),
                    dcc.Checklist(
                        id="filter-video-only", 
                        options=[{"label": "Yes", "value": "yes"}], 
                        value=[],
                        inputStyle={"margin-right": "5px"}
                    )
                ], md=3),

                dbc.Col([
                    dbc.Label("Format"),
                    dcc.Dropdown(
                        id="filter-video-format",
                        options=[
                            {"label": "Both", "value": "both"},
                            {"label": "DVD", "value": "dvd"},
                            {"label": "Blu-ray", "value": "blu-ray"},
                        ],
                        value="both",
                        clearable=False
                    )
                ], md=3),

                dbc.Col([
                    dbc.Label("Year Range"),
                    dcc.RangeSlider(
                        id="filter-year-video",
                        min=year_min,
                        max=year_max,
                        value=[year_min, year_max],
                        marks={y: str(y) for y in range(year_min, year_max + 1, (year_max - year_min) // 5)},
                        tooltip={"placement": "bottom", "always_visible": False},
                    )
                ], md=4),

                dbc.Col([
                    dbc.Label("Studio"),
                    dcc.Dropdown(
                        id="filter-studio",
                        options=[{"label": s, "value": s} for s in studios],
                        placeholder="Filter by studio (optional)",
                        clearable=True
                    )
                ], md=2),
            ])
        ]),
        class_name="mb-3"
    )

def layout(app):
    df = load_movies()
    
    header = dbc.Container([
        html.H2("Video Sales", className="mb-2"),
        html.P("DVD / Blu-ray sales analysis and trends", className="text-muted")
    ], className="my-4")

    filters_card = _build_filters_card(df)
    
    filter_collapse = html.Div([
        dbc.Button(
            "📊 Show Filters", 
            id="btn-toggle-video-filters", 
            color="primary", 
            size="sm", 
            className="mb-3",
            outline=True
        ),
        dbc.Collapse(filters_card, id="collapse-video-filters", is_open=True)  # Start open for better UX
    ])

    kpis = dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6("Total Video Sales", className="card-title text-muted"),
                    html.H3(id='kpi-total-video-sales', className="card-text text-primary")
                ])
            ), 
            md=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6("DVD Share", className="card-title text-muted"),
                    html.H3(id='kpi-dvd-share', className="card-text text-success")
                ])
            ), 
            md=6
        ),
    ], className='mb-4')

    charts = dbc.Row([
        dbc.Col(
            dcc.Graph(id='chart-video-pie'), 
            md=6,
            className="mb-3"
        ),
        dbc.Col(
            dcc.Graph(id='chart-gross-vs-video'), 
            md=6,
            className="mb-3"
        ),
    ])

    return html.Div([
        header, 
        filter_collapse, 
        kpis, 
        charts
    ], className="container-fluid")

def register_callbacks(app):
    # Wire the collapse toggle
    @app.callback(
        Output("collapse-video-filters", "is_open"),
        Input("btn-toggle-video-filters", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_filters(n):
        if n is None:
            return True
        return n % 2 == 1

    # Register page callbacks
    register_video_callbacks(app)