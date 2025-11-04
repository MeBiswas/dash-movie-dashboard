from dash import Input, Output, callback_context
import plotly.express as px
import pandas as pd
import dash
from dash import dash_table
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Top Movies (Cleaned Data).csv')

def load_df():
    df = pd.read_csv(DATA_PATH)
    if 'Release Date' in df.columns:
        df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
        df['Year'] = df['Release Date'].dt.year
    return df

def register_callbacks(app):
    @app.callback(
        Output('kpi-total-movies', 'children'),
        Output('kpi-total-gross', 'children'),
        Output('kpi-avg-budget', 'children'),
        Output('kpi-avg-runtime', 'children'),
        Input('filter-genre', 'value'),
        Input('filter-year', 'value'),
    )
    def update_kpis(selected_genres, year_range):
        df = load_df()
        if selected_genres:
            df = df[df['Genre'].isin(selected_genres)]
        if year_range:
            df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
        total_movies = len(df)
        total_gross = df['Worldwide Gross (USD)'].dropna().sum() if 'Worldwide Gross (USD)' in df.columns else float('nan')
        avg_budget = df['Production Budget (USD)'].dropna().mean() if 'Production Budget (USD)' in df.columns else float('nan')
        avg_runtime = df['Running Time (minutes)'].dropna().mean() if 'Running Time (minutes)' in df.columns else float('nan')

        def fmt(x):
            try:
                x = float(x)
                if abs(x) >= 1e9:
                    return f"${x/1e9:,.2f}B"
                if abs(x) >= 1e6:
                    return f"${x/1e6:,.2f}M"
                return f"${x:,.0f}"
            except:
                return "N/A"

        return (
            f"{total_movies}",
            fmt(total_gross),
            fmt(avg_budget),
            f"{int(avg_runtime)} min" if not pd.isna(avg_runtime) else "N/A"
        )

    @app.callback(
        Output('chart-sales-trend', 'figure'),
        Output('chart-top-movies', 'figure'),
        Output('chart-genre-box', 'figure'),
        Output('chart-studios-treemap', 'figure'),
        Input('filter-genre', 'value'),
        Input('filter-year', 'value'),
    )
    def update_charts(selected_genres, year_range):
        df = load_df()
        if selected_genres:
            df = df[df['Genre'].isin(selected_genres)]
        if year_range:
            df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

        # Sales trend
        if 'Year' in df.columns and 'Worldwide Gross (USD)' in df.columns:
            trend = df.groupby('Year', as_index=False)['Worldwide Gross (USD)'].sum()
            fig_trend = px.line(trend, x='Year', y='Worldwide Gross (USD)', title='Worldwide Gross by Year')
        else:
            fig_trend = px.line(title='Worldwide Gross by Year (data missing)')

        # Top movies
        if 'Worldwide Gross (USD)' in df.columns:
            top = df.sort_values('Worldwide Gross (USD)', ascending=False).head(10)
            fig_top = px.bar(top, x='Movie Name', y='Worldwide Gross (USD)', title='Top 10 Movies by Worldwide Gross')
        else:
            fig_top = px.bar(title='Top 10 Movies (data missing)')

        # Genre box
        if 'Genre' in df.columns and 'Worldwide Gross (USD)' in df.columns:
            fig_box = px.box(df, x='Genre', y='Worldwide Gross (USD)', title='Revenue Distribution by Genre')
        else:
            fig_box = px.box(title='Revenue Distribution by Genre (data missing)')

        # Studios treemap
        if 'Production/Financing Companies' in df.columns:
            df_comp = df.copy()
            df_comp['Company'] = df_comp['Production/Financing Companies'].fillna('Unknown')
            top_comp = df_comp.groupby('Company', as_index=False)['Worldwide Gross (USD)'].sum().sort_values('Worldwide Gross (USD)', ascending=False).head(50)
            fig_tree = px.treemap(top_comp, path=['Company'], values='Worldwide Gross (USD)', title='Top Production Companies by Worldwide Gross')
        else:
            fig_tree = px.treemap(title='Top Production Companies (data missing)')

        return fig_trend, fig_top, fig_box, fig_tree

    @app.callback(
        Output('table-container', 'children'),
        Input('filter-genre', 'value'),
        Input('filter-year', 'value'),
    )
    def update_table(selected_genres, year_range):
        df = load_df()
        if selected_genres:
            df = df[df['Genre'].isin(selected_genres)]
        if year_range:
            df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

        display_cols = ['Movie Name', 'Year', 'Genre', 'Production Budget (USD)', 'Worldwide Gross (USD)', 'Running Time (minutes)']
        available = [c for c in display_cols if c in df.columns]
        table = dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in available],
            data=df[available].to_dict('records'),
            page_size=10,
            sort_action='native',
            filter_action='native'
        )
        return table