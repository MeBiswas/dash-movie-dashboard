# preprocessing/clean_data_types.py

import re
import numpy as np
import pandas as pd

def fix_numeric_column(series):
    """Convert a messy numeric column to clean float or int."""
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace({"nan": np.nan, "": np.nan})
        .astype(float)
    )

def clean_movie_dtypes(df: pd.DataFrame):
    df = df.copy()

    # -----------------------------------
    # 1. Clean numeric money columns
    # -----------------------------------
    money_cols = [
        "Production Budget (USD)",
        "Domestic Gross (USD)",
        "International Gross (USD)",
        "Worldwide Gross (USD)",
        "Domestic Box Office (USD)",
        "International Box Office (USD)",
    ]

    for col in money_cols:
        if col in df.columns:
            df[col] = fix_numeric_column(df[col])

    # -----------------------------------
    # 2. Clean numeric non-money columns
    # -----------------------------------
    numeric_cols = [
        "Running Time (minutes)",
        "Opening Theaters",
        "Max Theaters",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # -----------------------------------
    # 3. Clean percentage columns
    # -----------------------------------
    if "Domestic Share Percentage" in df.columns:
        df["Domestic Share Percentage"] = (
            df["Domestic Share Percentage"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        df["Domestic Share Percentage"] = pd.to_numeric(
            df["Domestic Share Percentage"], errors="coerce"
        )

    # -----------------------------------
    # 4. Clean Release Date → datetime
    # -----------------------------------
    if "Release Date" in df.columns:
        df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")
        df["Year"] = df["Release Date"].dt.year

        # Fix future-year parsing issues (2062→1962)
        df.loc[df["Year"] > 2025, "Year"] -= 100
        df["Year"] = df["Year"].astype("float")  # allow NaN

    # -----------------------------------
    # 5. Normalize text columns
    # -----------------------------------
    for col in df.select_dtypes(include="object").columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace("\xa0", " ", regex=False)  # remove weird unicode space
            .replace({"nan": np.nan})              # remove "nan" strings
        )

    # -----------------------------------
    # 6. Ensure consistent column dtypes summary
    # -----------------------------------
    dtype_report = df.dtypes.to_dict()

    return df, dtype_report