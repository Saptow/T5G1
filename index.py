from dash import html, dcc, get_app, Output, Input, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import pycountry
import dash

# === Load Data ===
hist_df = pd.read_csv("historical_data.csv")
fbic_df = pd.read_csv("data/final/FBIC_sentiment_comtrade_un.csv")

# === Sector Mapping ===
SECTOR_LABELS = {
    "bec_1": "Food and Agriculture",
    "bec_2": "Energy and Mining",
    "bec_3": "Construction and Housing",
    "bec_4": "Textile and Footwear",
    "bec_5": "Transport and Travel",
    "bec_6": "ICT and Business",
    "bec_7": "Health and Education",
    "bec_8": "Government and Others"
}

# === Map country codes to full names ===
country_map = {c.alpha_3: c.name for c in pycountry.countries}
hist_df["country_a"] = hist_df["country_a"].map(country_map).fillna(hist_df["country_a"])
hist_df["country_b"] = hist_df["country_b"].map(country_map).fillna(hist_df["country_b"])
fbic_df["iso3a"] = fbic_df["iso3a"].map(country_map).fillna(fbic_df["iso3a"])
fbic_df["iso3b"] = fbic_df["iso3b"].map(country_map).fillna(fbic_df["iso3b"])

# === Filter for SG in 2023 ===
df_2023 = hist_df[hist_df["year"] == 2023]
df_sg = df_2023[df_2023["country_a"] == "Singapore"]

# === Total Trade Volume ===
total_volume = df_sg["trade_volume"].sum()

# === Best Performing Country ===
country_group = df_sg.groupby("country_b")["trade_volume"].sum()
best_country = country_group.idxmax()
best_country_value = country_group.max()
best_country_pct = (best_country_value / total_volume) * 100

# === Best Performing Sector ===
sector_volumes = []
for i in range(1, 9):
    imp_col = f"bec_{i}_import_A_from_B"
    exp_col = f"bec_{i}_export_A_to_B"
    total = df_sg[imp_col].sum() + df_sg[exp_col].sum()
    sector_volumes.append((f"bec_{i}", total))

sector_df = pd.DataFrame(sector_volumes, columns=["Sector", "Volume"])
best_sector_row = sector_df.loc[sector_df["Volume"].idxmax()]
best_sector_label = SECTOR_LABELS[best_sector_row["Sector"]]
best_sector_pct = (best_sector_row["Volume"] / total_volume) * 100

# === Geopolitical Distance ===
geo_sg = fbic_df[(fbic_df["year"] == 2023) & (fbic_df["iso3a"] == "Singapore")]
geo_avg = geo_sg["IdealPointDistance"].mean()

# === Format numbers ===
def format_volume(val):
    if val >= 1e9:
        return f"{val / 1e9:.2f}B SGD"
    elif val >= 1e6:
        return f"{val / 1e6:.2f}M SGD"
    elif val >= 1e3:
        return f"{val / 1e3:.2f}K SGD"
    else:
        return f"{val:.2f} SGD"

# === Stats ===
card_titles = [
    "Total Trade Volume (2023)",
    "Best Performing Country (2023)",
    "Best Performing Sector (2023)",
    "Avg Geopolitical Distance (2023)"
]

card_values = [
    format_volume(total_volume),
    f"{best_country} ({best_country_pct:.2f}%)",
    f"{best_sector_label} ({best_sector_pct:.2f}%)",
    f"{geo_avg:.2f}"
]

app = get_app()

layout = html.Div([
    dbc.Row([
        dbc.Col(html.Div([
            dbc.Card([
                html.Div([
                    html.Div(card_titles[0], style={"fontSize": "1rem", "color": "white"}),
                    html.Div(card_values[0], style={"fontSize": "2.5rem", "fontWeight": "bold", "color": "white"}),
                    html.Div("Year 2023", style={"fontSize": "0.9rem", "color": "white"})
                ], className="d-flex flex-column justify-content-center align-items-center h-100")
            ], className="text-center", style={"height": "250px", "backgroundColor": "#00B8D9", "borderRadius": "12px"})
        ], id="go-to-module2", style={"cursor": "pointer"}), width=3),

        dbc.Col(html.Div([
            dbc.Card([
                html.Div([
                    html.Div(card_titles[1], style={"fontSize": "1rem", "color": "white"}),
                    html.Div(card_values[1], style={"fontSize": "2.5rem", "fontWeight": "bold", "color": "white"}),
                    html.Div("Year 2023", style={"fontSize": "0.9rem", "color": "white"})
                ], className="d-flex flex-column justify-content-center align-items-center h-100")
            ], className="text-center", style={"height": "250px", "backgroundColor": "#FFC400", "borderRadius": "12px"})
        ], id="go-to-module1a", style={"cursor": "pointer"}), width=3),

        dbc.Col(html.Div([
            dbc.Card([
                html.Div([
                    html.Div(card_titles[2], style={"fontSize": "1rem", "color": "white"}),
                    html.Div(card_values[2], style={"fontSize": "2.5rem", "fontWeight": "bold", "color": "white"}),
                    html.Div("Year 2023", style={"fontSize": "0.9rem", "color": "white"})
                ], className="d-flex flex-column justify-content-center align-items-center h-100")
            ], className="text-center", style={"height": "250px", "backgroundColor": "#FF5A5F", "borderRadius": "12px"})
        ], id="go-to-module3a", style={"cursor": "pointer"}), width=3),

        dbc.Col(html.Div([
            dbc.Card([
                html.Div([
                    html.Div(card_titles[3], style={"fontSize": "1rem", "color": "white"}),
                    html.Div(card_values[3], style={"fontSize": "2.5rem", "fontWeight": "bold", "color": "white"}),
                    html.Div("Year 2023", style={"fontSize": "0.9rem", "color": "white"})
                ], className="d-flex flex-column justify-content-center align-items-center h-100")
            ], className="text-center", style={"height": "250px", "backgroundColor": "#9C27B0", "borderRadius": "12px"})
        ], id="go-to-module4a", style={"cursor": "pointer"}), width=3),
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
            style={
                "maxWidth": "1500px",
                "height": "400px",
                "margin": "0 auto",
                "borderRadius": "10px",
                "boxShadow": "0 0 10px rgba(0,0,0,0.3)"
            }
        )
    ])
])

# === Register Navigation Callbacks ===
def register_callbacks(app):
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        [
            Input("go-to-module2", "n_clicks"),
            Input("go-to-module1a", "n_clicks"),
            Input("go-to-module3a", "n_clicks"),
            Input("go-to-module4a", "n_clicks"),
        ],
        prevent_initial_call=True
    )
    def navigate(go2, go1a, go3a, go4a):
        ctx = callback_context.triggered_id
        if ctx == "go-to-module2" and go2:
            return "/module2"
        elif ctx == "go-to-module1a" and go1a:
            return "/module1a"
        elif ctx == "go-to-module3a" and go3a:
            return "/module3a"
        elif ctx == "go-to-module4a" and go4a:
            return "/module4a"
        return dash.no_update

# Register layout and callbacks
app.layout = layout
register_callbacks(app)
