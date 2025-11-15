# src/callbacks/insights_callbacks.py

import plotly.express as px
from dash import Input, Output
from plotly.graph_objects import Figure, Table

from src.utils.data_loader import load_movies
from src.utils.theme import COMMON_LAYOUT, BLUE, BLUE_LIGHT

def _empty_fig(title):
    fig = Figure()
    fig.update_layout(
        title=title, 
        template="plotly_white",
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{
            "text": "No data available",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16}
        }]
    )
    return fig

def register_callbacks(app):

    # ------------------------------------------------------
    # KPI CALLBACK
    # ------------------------------------------------------
    @app.callback(
        Output("insight-decade", "children"),
        Output("insight-genre", "children"),
        Output("insight-studio", "children"),
        Output("insight-outlier", "children"),
        Input("url", "pathname")
    )
    def update_kpis(_):
        df = load_movies()
        
        # Check if dataframe is empty
        if df.empty:
            return "N/A", "N/A", "N/A", "N/A"

        # Decade extraction
        df["Decade"] = (df["Year"] // 10) * 10
        top_decade = (
            df.groupby("Decade")["Worldwide Gross (USD)"]
              .sum()
              .idxmax()
            if df["Decade"].notna().any() else "N/A"
        )

        # ROI Genre
        top_genre = (
            df.groupby("Genre")["ROI (%)"].median()
              .idxmax()
            if "ROI (%)" in df.columns and df["ROI (%)"].notna().any() else "N/A"
        )

        # Studio (explode)
        df_studio = df.copy()
        df_studio = df_studio[df_studio["Production/Financing Companies"].notna()]
        if not df_studio.empty:
            df_studio["Company"] = df_studio["Production/Financing Companies"].str.split(",").apply(
                lambda lst: [c.strip() for c in lst] if isinstance(lst, list) else []
            )
            df_studio = df_studio.explode("Company")
            df_studio = df_studio[df_studio["Company"] != ""]

            if not df_studio.empty and "Profit (USD)" in df_studio.columns:
                top_studio = (
                    df_studio.groupby("Company")["Profit (USD)"].sum().idxmax()
                    if df_studio["Profit (USD)"].notna().any() else "N/A"
                )
            else:
                top_studio = "N/A"
        else:
            top_studio = "N/A"

        # Outlier: using z-score on worldwide gross
        outlier_movie = "None"
        if "Worldwide Gross (USD)" in df.columns and df["Worldwide Gross (USD)"].notna().any():
            if df["Worldwide Gross (USD)"].std() > 0:
                df["z"] = (df["Worldwide Gross (USD)"] - df["Worldwide Gross (USD)"].mean()) / df["Worldwide Gross (USD)"].std()
                df_out = df[df["z"] > 3]
                outlier_movie = df_out.iloc[0]["Movie Name"] if not df_out.empty else "None"

        return f"{int(top_decade)}s", top_genre, top_studio, outlier_movie

    # ------------------------------------------------------
    # CHART CALLBACK
    # ------------------------------------------------------
    @app.callback(
        Output("chart-decade", "figure"),
        Output("chart-budget-gross", "figure"),
        Output("insight-table", "figure"),
        Input("url", "pathname")
    )
    def update_insight_charts(_):
        df = load_movies()
        
        # Check if dataframe is empty
        if df.empty:
            return _empty_fig("Revenue by Decade"), _empty_fig("Budget vs Gross"), _empty_fig("Insights Summary")

        # ------ Chart 1: Gross by Decade ------
        df["Decade"] = (df["Year"] // 10) * 10
        decade_sum = (
            df.groupby("Decade")["Worldwide Gross (USD)"]
              .sum()
              .reset_index()
              .sort_values("Decade")
        )

        if decade_sum.empty or decade_sum["Worldwide Gross (USD)"].sum() == 0:
            fig_decade = _empty_fig("Revenue by Decade")
        else:
            fig_decade = px.bar(
                decade_sum,
                x="Decade",
                y="Worldwide Gross (USD)",
                title="Revenue by Decade",
                text_auto=True,
                color_discrete_sequence=[BLUE],
            )
            fig_decade.update_yaxes(tickformat="~s", tickprefix="$")
            fig_decade.update_layout(**COMMON_LAYOUT)

        # ------ Chart 2: Budget vs Gross ------
        if ("Production Budget (USD)" in df.columns and "Worldwide Gross (USD)" in df.columns and
            df["Production Budget (USD)"].notna().any() and df["Worldwide Gross (USD)"].notna().any()):
            
            # Filter out rows with missing data
            scatter_df = df.dropna(subset=["Production Budget (USD)", "Worldwide Gross (USD)"])
            
            if not scatter_df.empty:
                fig_bg = px.scatter(
                    scatter_df,
                    x="Production Budget (USD)",
                    y="Worldwide Gross (USD)",
                    hover_name="Movie Name",
                    title="Budget vs Gross (Lowess Trend)",
                    trendline="lowess",
                    log_x=True,
                    color_discrete_sequence=[BLUE],
                )
                fig_bg.update_xaxes(tickformat="~s", tickprefix="$")
                fig_bg.update_yaxes(tickformat="~s", tickprefix="$")
                fig_bg.update_layout(**COMMON_LAYOUT)
            else:
                fig_bg = _empty_fig("Budget vs Gross")
        else:
            fig_bg = _empty_fig("Budget vs Gross")

        # ------ Table of Insights ------
        # Prepare studio data for table (same logic as KPI callback)
        df_studio = df.copy()
        df_studio = df_studio[df_studio["Production/Financing Companies"].notna()]
        if not df_studio.empty:
            df_studio["Company"] = df_studio["Production/Financing Companies"].str.split(",").apply(
                lambda lst: [c.strip() for c in lst] if isinstance(lst, list) else []
            )
            df_studio = df_studio.explode("Company")
            df_studio = df_studio[df_studio["Company"] != ""]
        
        # Get top movie
        top_movie = "N/A"
        if "Worldwide Gross (USD)" in df.columns and df["Worldwide Gross (USD)"].notna().any():
            top_movie_row = df.loc[df["Worldwide Gross (USD)"].idxmax()]
            top_movie = top_movie_row["Movie Name"] if "Movie Name" in top_movie_row else "N/A"

        # Get highest ROI genre
        top_roi_genre = "N/A"
        if "ROI (%)" in df.columns and df["ROI (%)"].notna().any():
            top_roi_genre = df.groupby("Genre")["ROI (%)"].median().idxmax()

        # Get most profitable studio
        top_studio = "N/A"
        if not df_studio.empty and "Profit (USD)" in df_studio.columns and df_studio["Profit (USD)"].notna().any():
            top_studio = df_studio.groupby("Company")["Profit (USD)"].sum().idxmax()

        # Get highest-grossing decade for table
        highest_decade = "N/A"
        if not decade_sum.empty:
            highest_decade_row = decade_sum.loc[decade_sum["Worldwide Gross (USD)"].idxmax()]
            highest_decade = f"{int(highest_decade_row['Decade'])}s"

        # Create table using plotly.graph_objects
        table_data = {
            "Insight": ["Highest-Grossing Decade", "Highest ROI Genre", "Most Profitable Studio", "Highest Gross Movie"],
            "Value": [highest_decade, top_roi_genre, top_studio, top_movie]
        }

        fig_table = Figure(data=[Table(
            header=dict(
                values=["<b>Insight</b>", "<b>Value</b>"],
                fill_color=BLUE_LIGHT,
                align="left",
                font=dict(size=14, color="white"),
                height=40
            ),
            cells=dict(
                values=[table_data["Insight"], table_data["Value"]],
                fill_color="white",
                align="left",
                font=dict(size=12),
                height=30
            )
        )])
        
        fig_table.update_layout(
            title="Insights Summary",
            **COMMON_LAYOUT
        )

        return fig_decade, fig_bg, fig_table