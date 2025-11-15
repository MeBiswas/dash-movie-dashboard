# src/utils/filters.py

def apply_filters(df, genres=None, year_range=None):
    df = df[df["Year"].notna()]
    
    if genres:
        df = df[df["Genre"].isin(genres)]

    if year_range:
        df = df[
            (df["Year"] >= year_range[0]) &
            (df["Year"] <= year_range[1])
        ]

    return df
