from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from apps import module1a

# Load CSV and compute stats for 2025
csv_path = "priscilla_worldmap_data.csv"
df = pd.read_csv(csv_path)

# Filter for 2025 only
df_2025 = df[df['Year'] == 2025]
df_2024 = df[df['Year'] == 2024]

# Stat 1: Most common sector
stat_1 = df_2025['Sector'].mode().iloc[0]

# Stat 2 & 3: Sector change from 2024 to 2025
sector_vol_2025 = df_2025.groupby('Sector')['Sector Volume'].sum()
sector_vol_2024 = df_2024.groupby('Sector')['Sector Volume'].sum()
sector_change = (sector_vol_2025 - sector_vol_2024).sort_values(ascending=False)
stat_2 = (sector_change.idxmax(), "🔺" )
stat_3 = (sector_change.idxmin(), "🔻")

# Stat 4 & 5: Country change from 2024 to 2025
country_vol_2025 = df_2025.groupby('Country')['Total Volume'].sum()
country_vol_2024 = df_2024.groupby('Country')['Total Volume'].sum()
country_change = (country_vol_2025 - country_vol_2024).sort_values(ascending=False)
stat_4 = country_change.idxmax()
stat_5 = country_change.idxmin()

# Stat 6: SG Trade Increase
sg_2025 = df_2025['Total Volume'].sum()
sg_2024 = df_2024['Total Volume'].sum()
trade_change = (sg_2025 - sg_2024)/sg_2024 * 100
stat_6 = f"{trade_change:.2f}%"
arrow = "🔺" if trade_change > 0 else "🔻"

# Stat 7: Top Trading Partner
stat_7 = df_2025.groupby('Country')['Total Volume'].sum().idxmax()

# Stat 8: Total trade volume 2025 - dynamic units
if sg_2025 >= 1_000:
    stat_8 = f"{sg_2025 / 1_000:.2f} Billion SGD"
elif sg_2025 >= 1:
    stat_8 = f"{sg_2025:.2f} Million SGD"
else:
    stat_8 = f"{sg_2025 * 1_000:.2f} Thousand SGD"

# Define colors for each card
colors = ["#00B8D9", "#FFC400", "#FF5A5F", "#9C27B0", "#5C6BC0", "#8D6E63", "#26A69A", "#00ACC1"]
labels = [
    "Largest Sector", "Largest Sector Increase", "Largest Sector Decrease",
    "Largest Country Increase", "Largest Country Decrease",
    "Predicted Increase in Trade Volume",
    "Top Trading Partner", "Total Predicted Trade Volume in 2025"
]
values = [stat_1, stat_2, stat_3, stat_4, stat_5, stat_6 + " " + arrow, stat_7, stat_8]

layout = html.Div([
    html.Div([
        dbc.InputGroup([
            dbc.Input(id="news-url", placeholder="Paste news URL link...", type="url"),
            dbc.Button("Go", id="submit-url", color="primary")
        ], className="mb-4", style={"maxWidth": "600px", "margin": "0 auto"}),
    ]),

    html.Div([
        dbc.Row([
            dbc.Col(dbc.Card([
                html.Div(labels[i], style={"fontSize": "0.9rem", "color": "white"}),
                html.Div(values[i], style={"fontSize": "2.0rem", "fontWeight": "bold", "color": "white"})
            ], className="p-3 text-center", style={"height": "120px", "backgroundColor": colors[i], "borderRadius": "10px"}), width=3)
            for i in range(4)
        ], className="mb-2 g-2 px-3"),

        dbc.Row([
            dbc.Col(dbc.Card([
                html.Div(labels[i], style={"fontSize": "0.9rem", "color": "white"}),
                html.Div(values[i], style={"fontSize": "2.0rem", "fontWeight": "bold", "color": "white"})
            ], className="p-3 text-center", style={"height": "120px", "backgroundColor": colors[i], "borderRadius": "10px"}), width=3)
            for i in range(4, 8)
        ], className="mb-2 g-2 px-3")
    ]),

    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id="homepage-bargraph", figure=module1a.static_bar_graph()),
            ], style={"cursor": "pointer"}, id="go-to-module1")
        ], width=6),

        dbc.Col([
            html.Div([
                html.Img(src="/assets/world_map.png", style={"width": "100%", "borderRadius": "10px", "cursor": "pointer"})
            ], id="go-to-module2")
        ], width=6),
    ])
])