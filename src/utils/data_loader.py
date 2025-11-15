# src/utils/data_loader.py

import pandas as pd
from .constants import DATA_PATH

from src.preprocessing.clean_data_types import clean_movie_dtypes

def load_movies():
    df = pd.read_csv(DATA_PATH)
    
    df, dtype_report = clean_movie_dtypes(df)
    
    # Parse cleanly
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")
    
    # Extract year (may be NaN)
    df["Year"] = df["Release Date"].dt.year
    
    # Fix future-year parsing errors (2062 → 1962)
    df.loc[df["Year"] > 2025, "Year"] -= 100
    
    # Ensure dtype consistency
    df["Year"] = df["Year"].astype("float")   # allows NaN safely
    
    df['Profit (USD)'] = df['Worldwide Gross (USD)'] - df['Production Budget (USD)']
    df['ROI (%)'] = (df['Profit (USD)'] / df['Production Budget (USD)']) * 100


    return df