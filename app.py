# app.py

from dash import Dash
from src.app_router import build_app
import dash_bootstrap_components as dbc

# Use a Bootstrap theme for quick styling
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

# Build layout and register callbacks
build_app(app)

if __name__ == '__main__':
    app.run(debug=True, port=8050)