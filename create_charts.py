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
    df = df[df['inserted_at_utc'] >= cutoff]
    df['hour'] = df['inserted_at_utc'].dt.floor('h')
    grouped = df.groupby(['hour', 'category'])['calls'].max().reset_index()
    grouped = grouped.sort_values(by=['category', 'hour'])
    grouped['calls'] = grouped.groupby('category')['calls'].ffill()
    grouped['hourly_calls'] = grouped.groupby('category')['calls'].diff().fillna(0)
    return grouped

def render_page(chart_html, table_html, filename, dropdown_html):
    chart_template = env.get_template("chart_page.html")
    full_html = chart_template.render(chart=chart_html, table=table_html, dropdown=dropdown_html)
    with open(f"active_charts/{filename}", "w") as f:
        f.write(full_html)

def generate_all():
    os.makedirs('active_charts', exist_ok=True)
    df = load_data()
    time_ranges = {"48h": 48, "1w": 168, "1mo": 720}
    page_data = []

    # Step 1: collect all page info first
    for label, hours in time_ranges.items():
        data = prepare_data(df.copy(), hours)
        categories = data['category'].unique()

        # Overall chart
        page_data.append({
            'title': f"Hourly Calls by Category ({label})",
            'data': data,
            'filename': f"overall_{label}.html",
            'mode': 'overall'
        })

        # Top 5 chart
        top5 = data.groupby('category')['hourly_calls'].sum().sort_values(ascending=False).head(5).index
        top5_data = data[data['category'].isin(top5)]
        page_data.append({
            'title': f"Hourly Calls: Top 5 Categories ({label})",
            'data': top5_data,
            'filename': f"top5_{label}.html",
            'mode': 'top5'
        })

        # Per-category charts
        for cat in categories:
            cat_data = data[data['category'] == cat]
            page_data.append({
                'title': f"Hourly Calls: {cat} ({label})",
                'data': cat_data,
                'filename': f"category_{cat.replace(' ', '_')}_{label}.html",
                'mode': 'category'
            })

    # Step 2: build dropdown HTML once
    links = [p['filename'] for p in page_data]
    dropdown_template = env.get_template("dropdown.html")
    dropdown_html = dropdown_template.render(links=links)

    # Step 3: render all pages using full dropdown
    for p in page_data:
        fig = px.line(p['data'], x='hour', y='hourly_calls', color='category' if p['mode'] != 'category' else None,
                      title=p['title'], log_y=True,
                      labels={'hour': 'Time (Hourly)', 'hourly_calls': 'Calls this Hour'})
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        table_html = p['data'].to_html(index=False, classes='table table-striped')
        render_page(chart_html, table_html, p['filename'], dropdown_html)

if __name__ == "__main__":
    generate_all()
