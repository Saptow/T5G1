from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from apps import module1a

csv_path = "priscilla_worldmap_data.csv"
df = pd.read_csv(csv_path)


df_2025 = df[df['Year'] == 2025]
df_2024 = df[df['Year'] == 2024]

sg_2025 = df_2025['Total Volume'].sum()
sg_2024 = df_2024['Total Volume'].sum()
volume_diff = sg_2025 - sg_2024
percentage_change = (volume_diff / sg_2024) * 100
stat_1_title = "Predicted change in total trade volume"
stat_1_value = f"{volume_diff/1000:.2f} Million SGD ({percentage_change:.2f}%)"

country_2025 = df_2025.groupby('Country')['Total Volume'].sum()
country_2024 = df_2024.groupby('Country')['Total Volume'].sum()
country_growth = (country_2025 - country_2024).dropna()

best_country = country_growth.idxmax()
best_country_pct = (country_growth.max() / country_2024[best_country]) * 100
stat_2_title = "Best performing country"
stat_2_value = f"{best_country} (+{best_country_pct:.2f}%)"

sector_2025 = df_2025.groupby('Sector')['Sector Volume'].sum()
sector_2024 = df_2024.groupby('Sector')['Sector Volume'].sum()
sector_growth = (sector_2025 - sector_2024).dropna()

best_sector = sector_growth.idxmax()
best_sector_pct = (sector_growth.max() / sector_2024[best_sector]) * 100
stat_3_title = "Best performing sector"
stat_3_value = f"{best_sector} (+{best_sector_pct:.2f}%)"

card_titles = [stat_1_title, stat_2_title, stat_3_title, ""]
card_values = [stat_1_value, stat_2_value, stat_3_value, "Year 2025"]

layout = html.Div([
    html.Div([
        dbc.InputGroup([
            dbc.Input(id="news-url", placeholder="Paste news URL link...", type="url"),
            dbc.Button("Go", id="submit-url", color="primary")
        ], className="mb-4", style={"maxWidth": "600px", "margin": "0 auto"}),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            html.Div([
                html.Div(card_titles[i], style={"fontSize": "1rem", "color": "white"}),
                html.Div(card_values[i], style={"fontSize": "2.5rem", "fontWeight": "bold", "color": "white"}),
                html.Div("Year 2025", style={"fontSize": "0.9rem", "color": "white"}) if i < 3 else None
            ], className="d-flex flex-column justify-content-center align-items-center h-100")
        ], className="text-center", style={"height": "250px", "backgroundColor": ["#00B8D9", "#FFC400", "#FF5A5F", "#9C27B0"][i], "borderRadius": "12px"}), width=3)
        for i in range(4)
    ], className="mb-3 g-3 px-3"),

    html.Div([
        html.H4("Latest Market News", className="text-center mt-4 mb-3"),
        dbc.Carousel(
            items=[
                {"key": "1", "src": "/assets/news1.png"},
                {"key": "2", "src": "/assets/news2.png"},
                {"key": "3", "src": "/assets/news3.png"},
                {"key": "4", "src": "/assets/news4.png"},
                {"key": "5", "src": "/assets/news5.png"},
            ],
            controls=True,
            indicators=True,
            interval=5000,
            className="mb-5",
            style={"maxWidth": "1500px", "height": "400px", "margin": "0 auto", "borderRadius": "10px", "boxShadow": "0 0 10px rgba(0,0,0,0.3)"}
        )
    ]),

    #dbc.Row([
        #dbc.Col([
            #html.Div([
                #dcc.Graph(id="homepage-bargraph", figure=module1a.static_bar_graph()),
            #], style={"cursor": "pointer"}, id="go-to-module1")
        #], width=6),

        #dbc.Col([
            #html.Div([
                #html.Img(src="/assets/world_map.png", style={"width": "100%", "borderRadius": "10px", "cursor": "pointer"})
            #], id="go-to-module2")
        #], width=6),
    #])
])