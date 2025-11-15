# src/app_router.py

import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

from src.pages.home import layout as home_layout, register_callbacks as register_home_callbacks
from src.pages.video_sales import layout as video_layout, register_callbacks as register_video_callbacks
from src.pages.financial_analysis import layout as fin_layout, register_callbacks as register_fin_callbacks
from src.pages.insights import layout as insights_layout, register_callbacks as register_insights_callbacks

NAV = dbc.Nav(
    [
        dbc.NavLink("Home", href="/", active="exact"),
        dbc.NavLink("Video Sales", href="/video-sales", active="exact"),
        dbc.NavLink("Financial Analysis", href="/financial-analysis", active="exact"),
        dbc.NavLink("Insights", href="/insights", active="exact")
    ],
    vertical=False,
    pills=True,
)

def build_app(app):
    app.layout = dbc.Container(
        [
            dcc.Location(id="url", refresh=False),
            dbc.Row(
                [
                    dbc.Col(html.Div("🎬 Top Movies Dashboard", className="h3 my-2"), md=8),
                    dbc.Col(NAV, md=4, className="d-flex justify-content-end align-items-center"),
                ],
                align="center",
            ),
            html.Hr(),
            html.Div(id="page-content")
        ],
        fluid=True,
        className="p-2"
    )
    
    # router callback
    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname):
        if pathname == "/financial-analysis":
            return fin_layout(app)
        elif pathname == "/video-sales":
            return video_layout(app)
        elif pathname == "/insights":
            return insights_layout(app)
        else:
            return home_layout(app)

    # Register callbacks for all pages (safe: each module registers when called)
    register_fin_callbacks(app)
    register_home_callbacks(app)
    register_video_callbacks(app)
    register_insights_callbacks(app)