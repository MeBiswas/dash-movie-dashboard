import re
import numpy as np
import pandas as pd

# Load file
df = pd.read_csv('/mnt/data/Top Movies (Cleaned Data).csv')

# --- 1: Extract Release Year, Month, Quarter ---
df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
df['Release Year'] = df['Release Date'].dt.year
df['Release Month'] = df['Release Date'].dt.month
df['Release Quarter'] = df['Release Date'].dt.quarter

# --- Helper: Clean numeric columns ---
def clean_numeric(col):
    df[col] = (
        df[col].astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip()
        .replace("nan", np.nan)
    )
    df[col] = pd.to_numeric(df[col], errors='coerce')
    df[col] = df[col].fillna(df[col].median())

# Identify numeric-money-like columns
num_cols = [
    c for c in df.columns 
    if any(x in c.lower() for x in ["gross", "budget", "revenue", "box office"])
]

for col in num_cols:
    clean_numeric(col)

# --- 3: Convert numeric for Domestic Share Percentage ---
df['Domestic Share Percentage'] = (
    df['Domestic Share Percentage']
    .astype(str)
    .str.replace("%", "", regex=False)
    .str.strip()
)
df['Domestic Share Percentage'] = pd.to_numeric(
    df['Domestic Share Percentage'], errors='coerce'
)
df['Domestic Share Percentage'] = df['Domestic Share Percentage'].fillna(
    df['Domestic Share Percentage'].median()
)

# --- 4: Extract theater counts ---
def extract_theaters(text):
    if pd.isna(text):
        return np.nan, np.nan
    match = re.match(r"([0-9,]+) opening theaters/([0-9,]+) max. theaters", str(text))
    if match:
        opening = int(match.group(1).replace(",", ""))
        maximum = int(match.group(2).replace(",", ""))
        return opening, maximum
    return np.nan, np.nan

df["Opening Theaters"], df["Max Theaters"] = zip(*df["Theater counts"].map(extract_theaters))
df = df.drop(columns=["Theater counts"])

# --- Save cleaned data ---
output_path = "/mnt/data/movies_cleaned_dashboard.csv"
df.to_csv(output_path, index=False)

output_path
