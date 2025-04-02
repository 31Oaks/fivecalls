import os
import sqlite3
import pandas as pd
from datetime import datetime, timezone
import json
import plotly.express as px
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Setup Jinja2 environment
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(['html', 'xml'])
)

def load_data():
    conn = sqlite3.connect('data/fivecalls.db')
    df = pd.read_sql_query("SELECT calls, categories, inserted_at_utc FROM flat_data", conn)
    conn.close()
    df['categories_clean'] = df['categories'].apply(json.loads)
    df['category'] = df['categories_clean'].apply(lambda x: x[0]['name'] if x else 'Unknown')
    df['inserted_at_utc'] = pd.to_datetime(df['inserted_at_utc'], format='ISO8601', utc=True)
    return df

def prepare_data(df, hours):
    cutoff = pd.Timestamp.now(timezone.utc) - pd.Timedelta(hours=hours)

    extended_cutoff = cutoff - pd.Timedelta(hours=1)
    df = df[df['inserted_at_utc'] >= extended_cutoff]

    df['hour'] = df['inserted_at_utc'].dt.floor('h')
    grouped = df.groupby(['hour', 'category'])['calls'].max().reset_index()
    grouped = grouped.sort_values(by=['category', 'hour'])
    grouped['calls'] = grouped.groupby('category')['calls'].ffill()
    grouped['hourly_calls'] = grouped.groupby('category')['calls'].diff().fillna(0)

    grouped = grouped[grouped['hour'] >= cutoff]
    return grouped

def generate_all():
    os.makedirs('site_data', exist_ok=True)
    df = load_data()
    time_ranges = {"48h": 48, "1w": 168, "1mo": 720}
    combined_json = {}

    for label, hours in time_ranges.items():
        data = prepare_data(df.copy(), hours)
        categories = data['category'].unique()
        data['hour'] = data['hour'].astype(str)

        # Top 5 chart
        top5 = data.groupby('category')['hourly_calls'].sum().sort_values(ascending=False).head(5).index
        top5_data = data[data['category'].isin(top5)].copy()
        top5_data['hour'] = top5_data['hour'].astype(str)
        combined_json[f"top5_{label}"] = top5_data.to_dict(orient='records')

        # Overall chart
        combined_json[f"overall_{label}"] = data.to_dict(orient='records')

        # Per-category charts
        for cat in categories:
            key = f"{cat.replace(' ', '_')}_{label}"
            cat_data = data[data['category'] == cat].copy()
            cat_data['hour'] = cat_data['hour'].astype(str)
            combined_json[key] = cat_data.to_dict(orient='records')

    with open("site_data/chart_data.json", "w") as f:
        json.dump(combined_json, f, indent=2)

if __name__ == "__main__":
    generate_all()
