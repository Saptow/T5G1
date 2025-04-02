# module2.py , Trade World Map

from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# === Load Pre-generated Data ===
csv_path = "priscilla_worldmap_data.csv"
df = pd.read_csv(csv_path)

# Ensure proper types
df['Year'] = df['Year'].astype(int)
df['Total Volume'] = df['Total Volume'].astype(float)
df['Import Volume'] = df['Import Volume'].astype(float)
df['Export Volume'] = df['Export Volume'].astype(float)

# Extract distinct values for controls
years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())
sectors = sorted(df['Sector'].unique())

country_iso = {
    'China': 'CHN', 'USA': 'USA', 'Malaysia': 'MYS', 'Indonesia': 'IDN', 'Germany': 'DEU',
    'India': 'IND', 'Vietnam': 'VNM', 'Australia': 'AUS', 'Japan': 'JPN', 'UK': 'GBR',
    'France': 'FRA', 'Brazil': 'BRA', 'South Korea': 'KOR', 'Mexico': 'MEX', 'Russia': 'RUS',
    'Canada': 'CAN', 'Italy': 'ITA', 'Spain': 'ESP', 'Thailand': 'THA', 'Netherlands': 'NLD'
}

app = get_app()

