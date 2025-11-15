# src/callbacks/video_callbacks.py

import pandas as pd
import plotly.express as px
from dash import Input, Output
from plotly.graph_objects import Figure

from src.utils.data_loader import load_movies
from src.utils.formatting import format_money

def _empty_figure(message="No data for the selected filters"):
    fig = Figure()
    fig.update_layout(
        title=message, 
        template="plotly_white",
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{
            "text": message,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16}
        }]
    )
    return fig

def register_callbacks(app):
    @app.callback(
        Output('kpi-total-video-sales', 'children'),
        Output('kpi-dvd-share', 'children'),
        Output('chart-video-pie', 'figure'),
        Output('chart-gross-vs-video', 'figure'),
        Input('filter-video-only', 'value'),
        Input('filter-video-format', 'value'),
        Input('filter-year-video', 'value'),
        Input('filter-studio', 'value'),
    )
    def update_video_sales(video_only, video_format, year_range, studio):
        df = load_movies().copy()
        
        # Check if dataframe is empty
        if df.empty:
            return "N/A", "N/A", _empty_figure("No video sales data available"), _empty_figure("No data available")

        # Create total video sales columns with proper handling
        dvd_col = 'Est. Domestic DVD Sales (USD)'
        blu_col = 'Est. Domestic Blu-ray Sales (USD)'
        
        # Initialize video sales columns
        if dvd_col in df.columns:
            df['DVD'] = pd.to_numeric(df[dvd_col], errors='coerce').fillna(0)
        else:
            df['DVD'] = 0
            
        if blu_col in df.columns:
            df['Blu'] = pd.to_numeric(df[blu_col], errors='coerce').fillna(0)
        else:
            df['Blu'] = 0
            
        df['Total Video Sales'] = df['DVD'] + df['Blu']

        # Filter by "only movies with video sales"
        if video_only and 'yes' in video_only:
            df = df[df['Total Video Sales'] > 0]

        # Filter by format
        if video_format == 'dvd':
            df = df[df['DVD'] > 0]
        elif video_format == 'blu-ray':
            df = df[df['Blu'] > 0]

        # Filter by year range
        if 'Year' in df.columns and year_range:
            # Ensure Year is numeric
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
            df = df[df['Year'].notna()]
            df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

        # Filter by studio
        if studio:
            if 'Production/Financing Companies' in df.columns:
                df = df[df['Production/Financing Companies'].notna()]
                df = df[df['Production/Financing Companies'].str.contains(studio, na=False)]
            else:
                df = df.iloc[0:0]  # No studio column -> empty

        if df.empty:
            return "N/A", "N/A", _empty_figure("No video sales data for selection"), _empty_figure("No data for selection")

        # Calculate totals
        total_dvd = df['DVD'].sum()
        total_blu = df['Blu'].sum()
        total = total_dvd + total_blu

        # Create pie chart
        if total > 0:
            fig_pie = px.pie(
                names=['DVD', 'Blu-ray'],
                values=[total_dvd, total_blu],
                title='DVD vs Blu-ray Sales',
                color=['DVD', 'Blu-ray'],
                color_discrete_map={'DVD': '#1f77b4', 'Blu-ray': '#ff7f0e'}
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        else:
            fig_pie = _empty_figure("No video sales data")

        # Create scatter plot
        scatter_df = df[df['Total Video Sales'] > 0]
        if 'Worldwide Gross (USD)' in scatter_df.columns and not scatter_df.empty:
            # Ensure Worldwide Gross is numeric
            scatter_df = scatter_df.copy()
            scatter_df['Worldwide Gross (USD)'] = pd.to_numeric(scatter_df['Worldwide Gross (USD)'], errors='coerce')
            scatter_df = scatter_df[scatter_df['Worldwide Gross (USD)'].notna()]
            
            if not scatter_df.empty:
                fig_sc = px.scatter(
                    scatter_df,
                    x='Worldwide Gross (USD)',
                    y='Total Video Sales',
                    hover_name='Movie Name',
                    title='Worldwide Gross vs Total Video Sales',
                    log_x=True,
                    size='Total Video Sales',
                    color='Total Video Sales',
                    color_continuous_scale='viridis'
                )
                fig_sc.update_xaxes(tickformat="~s", tickprefix="$", title="Worldwide Gross (USD)")
                fig_sc.update_yaxes(tickformat="~s", tickprefix="$", title="Total Video Sales (USD)")
                fig_sc.update_layout(coloraxis_showscale=False)
            else:
                fig_sc = _empty_figure("No valid gross vs video data")
        else:
            fig_sc = _empty_figure("No gross vs video data available")

        # Calculate DVD share percentage
        dvd_share_pct = (total_dvd / total * 100) if total > 0 else 0

        return format_money(total), f"{dvd_share_pct:.1f}%", fig_pie, fig_sc