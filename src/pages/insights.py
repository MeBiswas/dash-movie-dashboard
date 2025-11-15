# src/pages/insights.py

from dash import html, dcc
import dash_bootstrap_components as dbc

from src.callbacks.insights_callbacks import register_callbacks as register_insights_callbacks

def insight_card(title, id_value, icon=""):
    return dbc.Card(
        dbc.CardBody([
            html.H6(f"{icon} {title}", className="card-title"),
            html.H3(id=id_value, className="mb-0")
        ]),
        class_name="m-2 p-3",
    )

def layout(app):
    header = dbc.Container([
        html.H2("Insights Dashboard"),
        html.P("High-level insights extracted from global movie trends, genres, revenue performance, and outlier behavior.")
    ], className="my-3")

    # KPI CARDS
    kpis = dbc.Row([
        dbc.Col(insight_card("Highest-Grossing Decade", "insight-decade", "📈"), md=3),
        dbc.Col(insight_card("Highest ROI Genre", "insight-genre", "🏆"), md=3),
        dbc.Col(insight_card("Most Profitable Studio", "insight-studio", "💼"), md=3),
        dbc.Col(insight_card("Biggest Outlier Movie", "insight-outlier", "🌟"), md=3),
    ], className="mt-4")

    # CHARTS
    charts = dbc.Row([
        dbc.Col(dcc.Graph(id="chart-decade"), md=6),
        dbc.Col(dcc.Graph(id="chart-budget-gross"), md=6),
    ], className="mt-4")

    # INSIGHT TABLE
    table_section = dbc.Row([
        dbc.Col(dcc.Graph(id="insight-table"), md=12)
    ], className="mt-4 mb-5")

    return html.Div([header, kpis, charts, table_section])

def register_callbacks(app):
    register_insights_callbacks(app)