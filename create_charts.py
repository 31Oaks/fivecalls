import os
import sqlite3
import pandas as pd
from datetime import datetime
from datetime import timezone
import json
import plotly.express as px
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Setup Jinja2 environment
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(['html', 'xml'])
)

# Global variable to store all chart links once
global_chart_links = []

def generate_chart(mode='all_categories', category_name=None):
    global global_chart_links

    os.makedirs('active_charts', exist_ok=True)

    conn = sqlite3.connect('data/fivecalls.db')
    df = pd.read_sql_query("SELECT calls, categories, inserted_at_utc FROM flat_data", conn)
    conn.close()

    df['categories_clean'] = df['categories'].apply(json.loads)
    df['category'] = df['categories_clean'].apply(lambda x: x[0]['name'] if x else 'Unknown')
    df['inserted_at_utc'] = pd.to_datetime(df['inserted_at_utc'], format='ISO8601', utc=True)
    df = df[df['inserted_at_utc'] >= pd.Timestamp.now(timezone.utc) - pd.Timedelta(hours=48)]
    df['hour'] = df['inserted_at_utc'].dt.floor('h')

    grouped = df.groupby(['hour', 'category'])['calls'].max().reset_index()
    grouped = grouped.sort_values(by=['category', 'hour'])
    grouped['calls'] = grouped.groupby('category')['calls'].ffill()
    grouped['hourly_calls'] = grouped.groupby('category')['calls'].diff().fillna(0)

    if mode == 'all_categories':
        all_categories = grouped['category'].unique()
        global_chart_links = ['overall.html', 'top_5_categories.html'] + [
            f'category_{cat.replace(" ", "_")}.html' for cat in all_categories
        ]
        generate_chart(mode='overall')
        generate_chart(mode='top5')
        for cat in all_categories:
            generate_chart(mode='category', category_name=cat)
        return

    if mode == 'category' and category_name:
        grouped = grouped[grouped['category'] == category_name]
        title = f'Hourly Calls: {category_name}'
        filename = f'category_{category_name.replace(" ", "_")}.html'
    elif mode == 'top5':
        top_categories = grouped.groupby('category')['hourly_calls'].sum().sort_values(ascending=False).head(5).index
        grouped = grouped[grouped['category'].isin(top_categories)]
        title = 'Hourly Calls: Top 5 Categories'
        filename = 'top_5_categories.html'
    else:
        title = 'Hourly Calls by Category (Last 48 Hours)'
        filename = 'overall.html'

    fig = px.line(grouped, x='hour', y='hourly_calls', color='category', log_y=True,
                  title=title, labels={'hour': 'Time (Hourly)', 'hourly_calls': 'Calls this Hour'})
    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    dropdown_template = env.get_template("dropdown.html")
    chart_template = env.get_template("chart_page.html")

    dropdown_html = dropdown_template.render(links=global_chart_links)
    html_output = chart_template.render(
        chart=plot_html,
        title=title,
        dropdown=dropdown_html,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    with open(f"active_charts/{filename}", "w") as f:
        f.write(html_output)

    print(f"✅ Chart saved to active_charts/{filename}")

if __name__ == "__main__":
    generate_chart()
