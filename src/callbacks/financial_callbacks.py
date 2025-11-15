# src/callbacks/financial_callbacks.py

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
        Output('kpi-total-profit', 'children'),
        Output('kpi-avg-roi', 'children'),
        Output('kpi-top-profit', 'children'),
        Input('filter-profit', 'value'),
        Input('filter-budget', 'value'),
        Input('filter-roi-cat', 'value'),
        Input('filter-genre-fin', 'value'),
    )
    def update_financial_kpis(profit_range, budget_range, roi_cat, genres):
        df = load_movies()
        
        # Check if dataframe is empty
        if df.empty:
            return "N/A", "N/A", "N/A"

        # Apply filters
        if genres:
            df = df[df['Genre'].isin(genres)]
            
        if 'Profit (USD)' in df.columns:
            df = df[df['Profit (USD)'].notna()]
            if profit_range and len(profit_range) == 2:
                df = df[(df['Profit (USD)'] >= profit_range[0]) & (df['Profit (USD)'] <= profit_range[1])]
                
        if 'Production Budget (USD)' in df.columns:
            df = df[df['Production Budget (USD)'].notna()]
            if budget_range and len(budget_range) == 2:
                df = df[(df['Production Budget (USD)'] >= budget_range[0]) & (df['Production Budget (USD)'] <= budget_range[1])]
                
        if 'ROI (%)' in df.columns and roi_cat and roi_cat != 'all':
            df = df[df['ROI (%)'].notna()]
            if roi_cat == 'high':
                df = df[df['ROI (%)'] > 100]  # Fixed: was 10000
            elif roi_cat == 'moderate':
                df = df[(df['ROI (%)'] >= 0) & (df['ROI (%)'] <= 100)]  # Fixed: was 10000
            elif roi_cat == 'low':
                df = df[df['ROI (%)'] < 0]

        if df.empty:
            return "N/A", "N/A", "N/A"

        # Calculate KPIs with safety checks
        total_profit = df['Profit (USD)'].sum() if 'Profit (USD)' in df.columns and df['Profit (USD)'].notna().any() else 0
        avg_roi = df['ROI (%)'].median() if 'ROI (%)' in df.columns and df['ROI (%)'].notna().any() else None
        
        top_movie = "N/A"
        if 'Profit (USD)' in df.columns and 'Movie Name' in df.columns and not df.empty:
            profit_df = df[df['Profit (USD)'].notna()]
            if not profit_df.empty:
                top_movie = profit_df.loc[profit_df['Profit (USD)'].idxmax(), 'Movie Name']

        return format_money(total_profit), f"{avg_roi:.1f}%" if avg_roi is not None else "N/A", top_movie

    @app.callback(
        Output('chart-profit-vs-budget', 'figure'),
        Output('chart-roi-genre', 'figure'),
        Output('chart-roi-distribution', 'figure'),
        Output('chart-fin-corr', 'figure'),
        Input('filter-profit', 'value'),
        Input('filter-budget', 'value'),
        Input('filter-roi-cat', 'value'),
        Input('filter-genre-fin', 'value'),
    )
    def update_financial_charts(profit_range, budget_range, roi_cat, genres):
        df = load_movies()

        # Apply same filters as KPIs
        if df.empty:
            return _empty_figure("No data available"), _empty_figure("No data available"), _empty_figure("No data available"), _empty_figure("No data available")

        if genres:
            df = df[df['Genre'].isin(genres)]
            
        if 'Profit (USD)' in df.columns:
            df = df[df['Profit (USD)'].notna()]
            if profit_range and len(profit_range) == 2:
                df = df[(df['Profit (USD)'] >= profit_range[0]) & (df['Profit (USD)'] <= profit_range[1])]
                
        if 'Production Budget (USD)' in df.columns:
            df = df[df['Production Budget (USD)'].notna()]
            if budget_range and len(budget_range) == 2:
                df = df[(df['Production Budget (USD)'] >= budget_range[0]) & (df['Production Budget (USD)'] <= budget_range[1])]
                
        if 'ROI (%)' in df.columns and roi_cat and roi_cat != 'all':
            df = df[df['ROI (%)'].notna()]
            if roi_cat == 'high':
                df = df[df['ROI (%)'] > 100]  # Fixed: was 10000
            elif roi_cat == 'moderate':
                df = df[(df['ROI (%)'] >= 0) & (df['ROI (%)'] <= 100)]  # Fixed: was 10000
            elif roi_cat == 'low':
                df = df[df['ROI (%)'] < 0]

        # Profit vs Budget scatter
        if ('Production Budget (USD)' in df.columns and 'Profit (USD)' in df.columns and 
            not df.empty and df['Production Budget (USD)'].notna().any() and df['Profit (USD)'].notna().any()):
            
            scatter_df = df.dropna(subset=['Production Budget (USD)', 'Profit (USD)'])
            if not scatter_df.empty:
                fig_scatter = px.scatter(
                    scatter_df,
                    x='Production Budget (USD)', 
                    y='Profit (USD)',
                    hover_name='Movie Name', 
                    log_x=True, 
                    trendline="lowess",
                    title='Budget vs Profit (log scale)',
                )
                fig_scatter.update_xaxes(tickformat="~s", tickprefix="$", title="Production Budget (USD)")
                fig_scatter.update_yaxes(tickformat="~s", tickprefix="$", title="Profit (USD)")
                fig_scatter.update_layout(template="plotly_white")
            else:
                fig_scatter = _empty_figure("Not enough data for Budget vs Profit")
        else:
            fig_scatter = _empty_figure("Not enough data for Budget vs Profit")

        # ROI by Genre
        if ('ROI (%)' in df.columns and 'Genre' in df.columns and 
            not df.empty and df['ROI (%)'].notna().any()):
            
            roi_gen = df.groupby('Genre', as_index=False)['ROI (%)'].median().sort_values('ROI (%)', ascending=False)
            if not roi_gen.empty:
                fig_roi_gen = px.bar(
                    roi_gen, 
                    x='Genre', 
                    y='ROI (%)', 
                    title='Median ROI by Genre',
                    color='ROI (%)',
                    color_continuous_scale='viridis'
                )
                fig_roi_gen.update_layout(template="plotly_white")
            else:
                fig_roi_gen = _empty_figure("No ROI data by Genre")
        else:
            fig_roi_gen = _empty_figure("No ROI data by Genre")

        # ROI distribution
        if 'ROI (%)' in df.columns and not df.empty and df['ROI (%)'].notna().any():
            roi_df = df[df['ROI (%)'].notna()]
            fig_roi_dist = px.histogram(
                roi_df, 
                x='ROI (%)', 
                nbins=50, 
                title='ROI Distribution',
                color_discrete_sequence=['#1f77b4']
            )
            fig_roi_dist.update_layout(template="plotly_white")
        else:
            fig_roi_dist = _empty_figure("ROI distribution not available")

        # Correlation heatmap
        numcols = ['Production Budget (USD)', 'Worldwide Gross (USD)', 'Profit (USD)', 'ROI (%)']
        present_cols = [c for c in numcols if c in df.columns]
        
        if len(present_cols) > 1:
            # Filter only numeric columns with data
            corr_df = df[present_cols].apply(pd.to_numeric, errors='coerce').dropna()
            if not corr_df.empty and len(corr_df) > 1:
                corr = corr_df.corr()
                fig_corr = px.imshow(
                    corr, 
                    text_auto=True, 
                    title='Financial Metrics Correlation',
                    color_continuous_scale='RdBu_r',
                    aspect="auto"
                )
                fig_corr.update_layout(template="plotly_white")
            else:
                fig_corr = _empty_figure("Not enough data for correlation")
        else:
            fig_corr = _empty_figure("Not enough data for correlation")

        return fig_scatter, fig_roi_gen, fig_roi_dist, fig_corr