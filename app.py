from dash import Dash, html
import dash_bootstrap_components as dbc
from layouts import build_layout
from callbacks import register_callbacks

# Use a Bootstrap theme for quick styling
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

# Build layout and register callbacks
app.layout = build_layout(app)
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=8050)