# src/callbacks/home_callbacks.py

import pandas as pd
import plotly.express as px
from dash import Input, Output, dash_table

from src.utils.filters import apply_filters
from src.utils.data_loader import load_movies
from src.utils.formatting import format_money
from src.utils.theme import COMMON_LAYOUT, BLUE, BLUE_LIGHT

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
        df = apply_filters(load_movies(), selected_genres, year_range)
        
        total = len(df)
        total_gross = df['Worldwide Gross (USD)'].sum()
        avg_budget = df['Production Budget (USD)'].mean()
        avg_runtime = df['Running Time (minutes)'].mean()

        return (
            f"{total}",
            format_money(total_gross),
            format_money(avg_budget),
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
        df = apply_filters(load_movies(), selected_genres, year_range)

        # -------------------------------
        # SALES TREND (LINE CHART)
        # -------------------------------
        trend = (
            df.groupby("Year", as_index=False)["Worldwide Gross (USD)"]
            .sum()
            .sort_values("Year")
        )
        fig_trend = px.line(
           trend,
            x="Year",
            y="Worldwide Gross (USD)",
            title="Worldwide Gross by Year",
            markers=True,
            color_discrete_sequence=[BLUE],
        )
        
        fig_trend.update_traces(line_width=3)
        fig_trend.update_yaxes(
            tickformat="~s",
            tickprefix="$",
        )
        fig_trend.update_layout(**COMMON_LAYOUT)

        # -------------------------------
        # TOP 10 MOVIES (HORIZONTAL BAR)
        # -------------------------------
        top = df.nlargest(10, "Worldwide Gross (USD)")
        fig_top = px.bar(
            top,
            x="Worldwide Gross (USD)",
            y="Movie Name",
            title="Top 10 Movies by Worldwide Gross",
            orientation="h",
            color_discrete_sequence=[BLUE],
        )
        fig_top.update_xaxes(tickformat="~s", tickprefix="$")
        fig_top.update_layout(**COMMON_LAYOUT)

        # -------------------------------
        # GENRE DISTRIBUTION BOX PLOT
        # -------------------------------
        # Sort genres by median revenue
        medians = df.groupby("Genre")["Worldwide Gross (USD)"].median().sort_values()
        df_sorted = df.set_index("Genre").loc[medians.index].reset_index()

        fig_box = px.box(
            df_sorted,
            x="Genre",
            y="Worldwide Gross (USD)",
            title="Revenue Distribution by Genre",
            color_discrete_sequence=[BLUE_LIGHT],
        )
        fig_box.update_yaxes(tickformat="~s", tickprefix="$")
        fig_box.update_layout(**COMMON_LAYOUT)
        
        # -------------------------------
        # STUDIO TREEMAP
        # -------------------------------
        df_comp = df.copy()
        # df_comp["Company"] = df_comp["Production/Financing Companies"].fillna("Unknown")
        df_comp = df_comp[df_comp["Production/Financing Companies"].notna()]
        
        def clean_companies(x):
            if not isinstance(x, str):
                return []
            comps = [c.strip() for c in x.split(",")]
            return [c for c in comps if c and c.lower() not in ["unknown", "n/a", "na"]]
        
        df_comp["Company"] = df_comp["Production/Financing Companies"].apply(clean_companies)
        
        df_comp = df_comp.explode("Company")
        
        df_comp = df_comp[df_comp["Company"].notna() & (df_comp["Company"] != "")]
        
        if df_comp.empty:
            fig_tree = px.treemap(
                title="Top Production Companies by Worldwide Gross (no valid data)"
            )
        else:

            top_comp = (
                df_comp.groupby("Company", as_index=False)["Worldwide Gross (USD)"]
                .sum()
                .nlargest(40, "Worldwide Gross (USD)")
            )

            fig_tree = px.treemap(
                top_comp,
                path=["Company"],
                values="Worldwide Gross (USD)",
                title="Top Production Companies by Worldwide Gross",
                color="Worldwide Gross (USD)",
                color_continuous_scale=px.colors.sequential.Blues,
            )

            fig_tree.update_traces(
                hovertemplate="<b>%{label}</b><br>Gross: $%{value:,.0f}",
                texttemplate="%{label}",
            )
            
        fig_tree.update_layout(**COMMON_LAYOUT)

        return fig_trend, fig_top, fig_box, fig_tree

    @app.callback(
        Output('table-container', 'children'),
        Input('filter-genre', 'value'),
        Input('filter-year', 'value'),
    )
    def update_table(selected_genres, year_range):
        df = apply_filters(load_movies(), selected_genres, year_range)

        cols = [
            "Movie Name", "Year", "Genre",
            "Production Budget (USD)", "Worldwide Gross (USD)",
            "Running Time (minutes)"
        ]
        available = [c for c in cols if c in df.columns]

        return dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in available],
            data=df[available].to_dict("records"),
            page_size=10,
            sort_action="native",
            filter_action="native",
        )