from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

# Load and prepare data (as previously done)
df = pd.read_csv("bilateral_trade_data_2026.csv")

df_2026a = df[df["Time Period"] == "2026a"]
df_2026b = df[df["Time Period"] == "2026b"]

agg_2026a = df_2026a.groupby(["Reporter", "Sector Group"]).agg({
    "Export Value": "sum",
    "Import Value": "sum",
    "Total Trade Volume": "sum"
}).rename(columns=lambda x: x + "_2026a")

agg_2026b = df_2026b.groupby(["Reporter", "Sector Group"]).agg({
    "Export Value": "sum",
    "Import Value": "sum",
    "Total Trade Volume": "sum"
}).rename(columns=lambda x: x + "_2026b")

df_merged = agg_2026a.join(agg_2026b, how='inner').reset_index()

for col in ["Export Value", "Import Value", "Total Trade Volume"]:
    df_merged[f"{col} % Change"] = (
        (df_merged[f"{col}_2026b"] - df_merged[f"{col}_2026a"]) / df_merged[f"{col}_2026a"]
    ) * 100

app = get_app()
# Sidebar controls only (to be used in index.py dynamically)
sidebar_controls = html.Div([
    html.H2("Sectoral Growth Opportunities After Geopolitical Shock", className="mb-3"),

    html.Div([

        # Group 1: Button Toggle
        html.Div([
            html.P("1. Select Country/Sector:", style={"marginBottom": "2px"}),
            html.Div([
                html.Button("By Country", id="btn-country", n_clicks=0, className="inactive", style={"marginRight": "5px"}),
                html.Button("By Sector", id="btn-sector", n_clicks=0, className="inactive")
            ])
        ], style={"marginRight": "30px"}),

        # Group 2: Dropdown for filter
        html.Div([
            html.P("2. Specific Country/Sector:", style={"marginBottom": "2px"}),
            dcc.Dropdown(
                id="filter-dropdown",
                placeholder="",
                style={"width": "220px"}
            )
        ], style={"marginRight": "30px"}),

        # Group 3: Trade Type Dropdown
        html.Div([
            html.P("3. Select Trade Type:", style={"marginBottom": "2px"}),
            dcc.Dropdown(
                id="trade-type-dropdown",
                options=[
                    {"label": "Total Trade Volume", "value": "Total Trade Volume"},
                    {"label": "Export Value", "value": "Export Value"},
                    {"label": "Import Value", "value": "Import Value"}
                ],
                placeholder="",
                style={"width": "220px"}
            )
        ])
    ], style={"display": "flex", "flexWrap": "wrap", "alignItems": "flex-end"})
], style={"padding": "10px"})


# Layout (no sidebar_controls here to avoid duplication in index.py)
layout = html.Div([
    html.Div([
        dcc.Graph(id="dumbbell-graph", style={"marginTop": "20px"})
    ])
])

    dcc.Graph(id="geo-trade-chart", style={"height": "600px"}),
], className="p-4")

# Callback
@app.callback(
    Output("geo-trade-chart", "figure"),
    Input("country-selector", "value")
)
def update_geo_trade_chart(selected_country):
    country_df = df[df["Country"] == selected_country]

    # Prepare custom data for hover text
    customdata = country_df[["Geopolitical Distance","Exports", "Imports", "Trade Balance"]].values

    fig = go.Figure()

    # Bar for Total Trade (right Y-axis)
    fig.add_trace(go.Bar(
        x=country_df["Year"],
        y=country_df["Total Trade"],
        name="Total Trade",
        marker_color="blue",
        opacity=0.5,
        yaxis="y2",
        customdata=customdata,
        hovertemplate=(
            "Geopolitical Distance: %{customdata[0]}<br>" +
            "Total Trade: %{y}<br>" +
            "Exports: %{customdata[1]}<br>" +
            "Imports: %{customdata[2]}<br>" +
            "Trade Balance: %{customdata[3]}<extra></extra>"
        )
    ))

    # Line for Geopolitical Distance (left Y-axis)
    fig.add_trace(go.Scatter(
        x=country_df["Year"],
        y=country_df["Geopolitical Distance"],
        name="Geopolitical Distance",
        mode="lines+markers",
        marker=dict(color="black"),
        line=dict(width=3, color="black"),
        yaxis="y1",
        hovertemplate=(
            "Geopolitical Distance: %{customdata[0]}<br>" +
            "Total Trade: %{y}<br>" +
            "Exports: %{customdata[1]}<br>" +
            "Imports: %{customdata[2]}<br>" +
            "Trade Balance: %{customdata[3]}<extra></extra>"
        )
    ))

    # Layout
    fig.update_layout(
        barmode="overlay",
        template="plotly_white",
        title=f"{selected_country}: Geopolitical Distance vs. Total Trade (2014–2025)",
        xaxis=dict(title="Year"),
        yaxis=dict(
            title="Geopolitical Distance",
            range=[-1.1, 1.1]
        ),
        yaxis2=dict(
            title="Total Trade (Billion $)",
            overlaying="y",
            side="right"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=60, l=60, r=60)
    )

    return fig

# Register to current app instance

app.layout = layout 
register_callbacks(app)