from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

import dash
import dash_bootstrap_components as dbc
from dash import html
from layout.homepage_layout import layout

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Trade Heatmap Dashboard"
app.layout = layout



# Load CSV and compute stats for 2025
df = pd.read_csv("data/priscilla_worldmap_data.csv")

# Filter for 2025 only
df_2025 = df[df['Year'] == 2025]
df_2024 = df[df['Year'] == 2024]

# Stat 1: Most common sector
stat_1 = df_2025['Sector'].mode().iloc[0]

# Stat 2 & 3: Sector change from 2024 to 2025
sector_vol_2025 = df_2025.groupby('Sector')['Sector Volume'].sum()
sector_vol_2024 = df_2024.groupby('Sector')['Sector Volume'].sum()
sector_change = (sector_vol_2025 - sector_vol_2024).sort_values(ascending=False)
stat_2 = sector_change.idxmax()
stat_3 = sector_change.idxmin()

# Stat 4 & 5: Country change from 2024 to 2025
country_vol_2025 = df_2025.groupby('Country')['Total Volume'].sum()
country_vol_2024 = df_2024.groupby('Country')['Total Volume'].sum()
country_change = (country_vol_2025 - country_vol_2024).sort_values(ascending=False)
stat_4 = country_change.idxmax()
stat_5 = country_change.idxmin()

# Stat 6: SG Trade Increase
sg_2025 = df_2025['Total Volume'].sum()
sg_2024 = df_2024['Total Volume'].sum()
stat_6 = f"{((sg_2025 - sg_2024)/sg_2024 * 100):.2f}%"

# Stat 7: Top Trading Partner
stat_7 = df_2025.groupby('Country')['Total Volume'].sum().idxmax()

# Stat 8: Total trade volume 2025
stat_8 = f"{sg_2025:.2f} Billion SGD"

layout = html.Div([
    # === Top Center Input Section ===
    html.Div([
        dbc.InputGroup([
            dbc.Input(id="news-url", placeholder="Paste news URL link...", type="url"),
            dbc.Button("Go", id="submit-url", color="primary")
        ], className="mb-4", style={"maxWidth": "600px", "margin": "0 auto"}),
    ]),

    # === 2 Rows of 4 Stats Blocks ===
    html.Div([
        dbc.Row([
            dbc.Col(dbc.Card(html.Div([
                html.Div("Stat 1", style={"fontWeight": "bold"}),
                html.Div(id="stat-1", children=stat_1)
            ], className="text-center"), className="p-3", style={"height": "120px"}), width=3),

            dbc.Col(dbc.Card(html.Div([
                html.Div("Stat 2", style={"fontWeight": "bold"}),
                html.Div(id="stat-2", children=stat_2)
            ], className="text-center"), className="p-3", style={"height": "120px"}), width=3),

            dbc.Col(dbc.Card(html.Div([
                html.Div("Stat 3", style={"fontWeight": "bold"}),
                html.Div(id="stat-3", children=stat_3)
            ], className="text-center"), className="p-3", style={"height": "120px"}), width=3),

            dbc.Col(dbc.Card(html.Div([
                html.Div("Stat 4", style={"fontWeight": "bold"}),
                html.Div(id="stat-4", children=stat_4)
            ], className="text-center"), className="p-3", style={"height": "120px"}), width=3),
        ], className="mb-2 g-2 px-3"),

        dbc.Row([
            dbc.Col(dbc.Card(html.Div([
                html.Div("Stat 5", style={"fontWeight": "bold"}),
                html.Div(id="stat-5", children=stat_5)
            ], className="text-center"), className="p-3", style={"height": "120px"}), width=3),

            dbc.Col(dbc.Card(html.Div([
                html.Div("Stat 6", style={"fontWeight": "bold"}),
                html.Div(id="stat-6", children=stat_6)
            ], className="text-center"), className="p-3", style={"height": "120px"}), width=3),

            dbc.Col(dbc.Card(html.Div([
                html.Div("Stat 7", style={"fontWeight": "bold"}),
                html.Div(id="stat-7", children=stat_7)
            ], className="text-center"), className="p-3", style={"height": "120px"}), width=3),

            dbc.Col(dbc.Card(html.Div([
                html.Div("Stat 8", style={"fontWeight": "bold"}),
                html.Div(id="stat-8", children=stat_8)
            ], className="text-center"), className="p-3", style={"height": "120px"}), width=3),
        ], className="mb-2 g-2 px-3")
    ]),
])

if __name__ == '__main__':
    app.run(debug=True)
