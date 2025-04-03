from dash import html, dcc
import dash_bootstrap_components as dbc
from apps import module1

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
            dbc.Col(dbc.Card(html.Div("Stat 1"), className="p-3 text-center", style={"height": "120px"}), width=3),
            dbc.Col(dbc.Card(html.Div("Stat 2"), className="p-3 text-center", style={"height": "120px"}), width=3),
            dbc.Col(dbc.Card(html.Div("Stat 3"), className="p-3 text-center", style={"height": "120px"}), width=3),
            dbc.Col(dbc.Card(html.Div("Stat 4"), className="p-3 text-center", style={"height": "120px"}), width=3),
        ], className="mb-2 g-2 px-3"),

        dbc.Row([
            dbc.Col(dbc.Card(html.Div("Stat 5"), className="p-3 text-center", style={"height": "120px"}), width=3),
            dbc.Col(dbc.Card(html.Div("Stat 6"), className="p-3 text-center", style={"height": "120px"}), width=3),
            dbc.Col(dbc.Card(html.Div("Stat 7"), className="p-3 text-center", style={"height": "120px"}), width=3),
            dbc.Col(dbc.Card(html.Div("Stat 8"), className="p-3 text-center", style={"height": "120px"}), width=3),
        ], className="mb-2 g-2 px-3")
    ]),

    # === Lower Section Split: Bar Graph (Left) + PNG Image (Right) ===
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id="homepage-bargraph", figure=module1.static_bar_graph()),
            ], style={"cursor": "pointer"}, id="go-to-module1")
        ], width=6),

        dbc.Col([
            html.Div([
                html.Img(src="/assets/world_map.png", style={"width": "100%", "borderRadius": "10px", "cursor": "pointer"})
            ], id="go-to-module2")
        ], width=6),
    ])
])
