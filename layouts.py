from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Top Movies (Cleaned Data).csv')

def load_df():
    df = pd.read_csv(DATA_PATH)
    # Basic parsing
    if 'Release Date' in df.columns:
        df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
        df['Year'] = df['Release Date'].dt.year
    # Normalize column names for convenience
    return df

def kpi_card(title, id_value):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className='card-title'),
            html.H3(id=id_value)
        ]),
        class_name='m-2 p-2'
    )

def build_layout(app):
    df = load_df()
    years = sorted([int(y) for y in df['Year'].dropna().unique()]) if 'Year' in df.columns else []
    genres = sorted([g for g in df['Genre'].dropna().unique()]) if 'Genre' in df.columns else []

    header = dbc.Container([
        html.H1("🎬 Top Movies Dashboard"),
        html.P("Interactive analytics for movies: financials, genres, franchises, and more.")
    ], className='my-3')

    kpis = dbc.Row([
        dbc.Col(kpi_card("Total Movies", "kpi-total-movies")),
        dbc.Col(kpi_card("Total Worldwide Gross (USD)", "kpi-total-gross")),
        dbc.Col(kpi_card("Average Budget (USD)", "kpi-avg-budget")),
        dbc.Col(kpi_card("Average Runtime (minutes)", "kpi-avg-runtime")),
    ])

    controls = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Genre"),
                    dcc.Dropdown(options=[{"label": g, "value": g} for g in genres], multi=True, id='filter-genre')
                ], md=4),
                dbc.Col([
                    html.Label("Year range"),
                    dcc.RangeSlider(id='filter-year', min=min(years) if years else 2000, max=max(years) if years else 2025, value=[min(years) if years else 2000, max(years) if years else 2025], marks={str(y): str(y) for y in years[:10]} )
                ], md=6)
            ])
        ]),
        class_name='m-2'
    )

    charts = dbc.Row([
        dbc.Col(dcc.Graph(id='chart-sales-trend'), md=8),
        dbc.Col(dcc.Graph(id='chart-top-movies'), md=4),
    ], className='mt-3')

    more_charts = dbc.Row([
        dbc.Col(dcc.Graph(id='chart-genre-box'), md=6),
        dbc.Col(dcc.Graph(id='chart-studios-treemap'), md=6),
    ], className='mt-3')

    table = dbc.Row([
        dbc.Col(html.Div(id='table-container'))
    ], className='mt-3')

    layout = html.Div([
        header,
        kpis,
        controls,
        charts,
        more_charts,
        table,
        html.Footer("Generated with Dash • Dataset: Top Movies (Cleaned Data)", className='mt-5 mb-3 text-center')
    ])

    return layout