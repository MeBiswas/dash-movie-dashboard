# src/layouts/main_layouts.py

from dash import html, dcc
import dash_bootstrap_components as dbc

from src.utils.data_loader import load_movies

# ---------------------------------------------------------
# KPI Card Component
# ---------------------------------------------------------
def kpi_card(title, id_value):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className='card-title'),
            html.H3(id=id_value)
        ]),
        class_name='m-2 p-2'
    )

# ---------------------------------------------------------
# Main Layout Builder
# ---------------------------------------------------------
def build_layout(app):
    # Load cleaned & corrected dataset
    df = load_movies()

    # -----------------------------
    # Extract Year & Genre filters
    # -----------------------------
    genres = sorted(df['Genre'].dropna().unique()) if 'Genre' in df.columns else []
    years = sorted(df['Year'].dropna().astype(int).unique()) if 'Year' in df.columns else []

    # Clean year boundaries
    year_min = int(min(years)) if years else 2000
    year_max = int(max(years)) if years else 2025

    # Slider marks (clean, readable)
    year_marks = {y: str(y) for y in range(year_min, year_max + 1, 10)}

    # -----------------------------
    # Header
    # -----------------------------
    header = dbc.Container([
        html.H1("🎬 Top Movies Dashboard"),
        html.P("Interactive analytics for movies: financials, genres, franchises, and more.")
    ], className='my-3')

    # -----------------------------
    # KPI Cards
    # -----------------------------
    kpis = dbc.Row([
        dbc.Col(kpi_card("Total Movies", "kpi-total-movies")),
        dbc.Col(kpi_card("Total Worldwide Gross (USD)", "kpi-total-gross")),
        dbc.Col(kpi_card("Average Budget (USD)", "kpi-avg-budget")),
        dbc.Col(kpi_card("Average Runtime (minutes)", "kpi-avg-runtime")),
    ])

    # -----------------------------
    # Filters Card
    # -----------------------------
    controls = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Genre"),
                    dcc.Dropdown(
                        options=[{"label": g, "value": g} for g in genres],
                        multi=True,
                        id='filter-genre'
                    )
                ], md=4),

                dbc.Col([
                    html.Label("Year Range"),
                    dcc.RangeSlider(
                        id="filter-year",
                        min=year_min,
                        max=year_max,
                        value=[year_min, year_max],
                        marks=year_marks,
                        tooltip={"placement": "bottom", "always_visible": False},
                    )
                ], md=6),
            ])
        ]),
        class_name='m-2'
    )

    # -----------------------------
    # Charts Section
    # -----------------------------
    charts = dbc.Row([
        dbc.Col(dcc.Graph(id='chart-sales-trend'), md=8),
        dbc.Col(dcc.Graph(id='chart-top-movies'), md=4),
    ], className='mt-3')

    more_charts = dbc.Row([
        dbc.Col(dcc.Graph(id='chart-genre-box'), md=6),
        dbc.Col(dcc.Graph(id='chart-studios-treemap'), md=6),
    ], className='mt-3')

    # -----------------------------
    # Table Section
    # -----------------------------
    table = dbc.Row([
        dbc.Col(html.Div(id='table-container'))
    ], className='mt-3')

    # -----------------------------
    # Full Layout
    # -----------------------------
    layout = html.Div([
        header,
        kpis,
        controls,
        charts,
        more_charts,
        table,
        html.Footer(
            "Generated with Dash • Dataset: Top Movies (Cleaned Data)",
            className='mt-5 mb-3 text-center'
        )
    ])

    return layout