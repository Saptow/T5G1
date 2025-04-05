from dash import html, dcc
from dash import dcc, html, Input, Output, State, callback_context, get_app, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Load data from CSV 
df = pd.read_csv("priscilla_worldmap_data.csv")
df["Net Exports"] = df["Export Volume"] - df["Import Volume"]

app = get_app()

# === DASH LAYOUT ===
layout = html.Div([
    html.H3("Singapore’s Top Trading Partners Over Time", className="mb-3"),
    html.P("See how Singapore’s trade flows with its top partners have evolved.", className="mb-4"),

    # Graph Placeholder
    dcc.Graph(id="trade-chart"),
], className="container p-4")


# === CALLBACK TO UPDATE CHART ===
@app.callback(
    Output("trade-chart", "figure"),
    [Input("trade-direction", "value"), Input("country-selection", "value")]
)
def update_chart(trade_type, selected_countries):
    filtered_df = df[df["Country"].isin(selected_countries)]

    fig = px.line(filtered_df, x="Year", y=trade_type, color="Country",
                  labels={"Year": "Year", trade_type: f"{trade_type} (Billion $)"},
                  title=f"Singapore’s {trade_type} Over Time")

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",  
        xaxis=dict(
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            showline=True,
            spikedash="dot", 
            spikecolor="gray",
            spikethickness=1,
        ),
    )

    return fig


# Dropdowns
sidebar_controls =html.Div([
    html.Div([
        html.Label("Direction of Trade", className="fw-bold"),
        dcc.Dropdown(
            id="trade-direction",
            options=[
                {"label": "Exports", "value": "Export Volume"},
                {"label": "Imports", "value": "Import Volume"},
                {"label": "Net Exports", "value": "Net Exports"},
                {"label": "Total Trade", "value": "Total Volume"},
            ],
            value="Export Volume",
            className="mb-3",
        ),
    ], style={"width": "250px", "margin-right": "20px"}),

    html.Div([
        html.Label("Select Countries", className="fw-bold"),
        dcc.Dropdown(
            id="country-selection",
            options=[{"label": c, "value": c} for c in df["Country"].unique()],
            value=["China", "Malaysia", "USA", "Indonesia", "South Korea"],  # Default selection
            multi=True,
            className="mb-3",
        ),
    ], style={"width": "300px"}),
], style={"display": "flex", "align-items": "flex-end", "margin-bottom": "0"}),
