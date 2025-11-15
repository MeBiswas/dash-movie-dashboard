# src/pages/home.py

from dash import html, dcc
import dash_bootstrap_components as dbc

from src.utils.data_loader import load_movies
from src.layouts.main_layouts import kpi_card
from src.callbacks.home_callbacks import register_callbacks as register_home_callbacks

def layout(app):
    df = load_movies()
    years = sorted(df['Year'].dropna().astype(int).unique()) if 'Year' in df.columns else []
    genres = sorted(df['Genre'].dropna().unique()) if 'Genre' in df.columns else []

    year_min = int(min(years)) if years else 2000
    year_max = int(max(years)) if years else 2025
    year_marks = {y: str(y) for y in range(year_min, year_max + 1, 10)}

    header = dbc.Container([
        html.H2("Home"),
        html.P("Overview: KPIs, trend, top movies, genre distribution."),
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
                    html.Label("Year Range"),
                    dcc.RangeSlider(
                        id="filter-year",
                        min=year_min, max=year_max, value=[year_min, year_max],
                        marks=year_marks,
                        tooltip={"placement": "bottom", "always_visible": False},
                    )
                ], md=6),
            ])
        ]),
        class_name='m-2'
    )

    main_charts = dbc.Row([
        dbc.Col(dcc.Graph(id='chart-sales-trend'), md=8),
        dbc.Col(dcc.Graph(id='chart-top-movies'), md=4),
    ], className='mt-3')

    more_charts = dbc.Row([
        dbc.Col(dcc.Graph(id='chart-genre-box'), md=6),
        dbc.Col(dcc.Graph(id='chart-studios-treemap'), md=6),
    ], className='mt-3')

    table = dbc.Row([dbc.Col(html.Div(id='table-container'))], className='mt-3')

    # Collapsible sections for extra notebook items (kept on home)
    extra = dbc.Collapse([
        dbc.Card(dbc.CardBody([html.H5("Extra analysis from notebook"), html.P("Placeholder for additional visuals.")]))
    ], id="home-extra-collapse", is_open=False)

    return html.Div([header, kpis, controls, main_charts, more_charts, table, extra])

def register_callbacks(app):
    register_home_callbacks(app)