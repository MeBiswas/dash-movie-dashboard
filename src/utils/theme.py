# utils/theme.py

import plotly.express as px

# Business Blue Palette
BLUE = "#1f77b4"
BLUE_LIGHT = "#6baed6"
BLUE_DARK = "#0d3b66"

PALETTE = ["#1f77b4", "#2a5783", "#4e79a7", "#6baed6", "#9ecae1"]

COMMON_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=40, r=25, t=60, b=40),
    title_font=dict(size=18, color="#0d3b66", family="Arial"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    hoverlabel=dict(bgcolor="white", font_size=12),
    xaxis=dict(
        showgrid=True,
        gridcolor="rgba(200,200,200,0.35)",
        linecolor="#0d3b66",
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(200,200,200,0.35)",
        linecolor="#0d3b66",
    ),
)
