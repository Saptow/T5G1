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
MAX_TOP_N = 10
app = get_app()

# === Helper Function ===
def get_top_n_countries_by_direction(df, direction, top_n):
    grouped = (
        df.groupby("Country")[direction]
        .mean()
        .nlargest(top_n)
        .index
    )
    return grouped.tolist()

# === DASH LAYOUT ===
layout = html.Div([
    html.H3("Singapore’s Top Trading Partners Over Time", className="mb-3"),
    html.P("See how Singapore’s trade flows with its top partners have evolved.", className="mb-4"),

    html.Div([
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
    ], style={"width": "500px"}),

    html.Div([
        html.Label("Select Sector", className="fw-bold"),
        dcc.Dropdown(
            id="sector-selection",
            options=[{"label": s, "value": s} for s in sorted(df["Sector"].unique())],
            placeholder="All Sectors",
            clearable=True,
            className="mb-3",
    ),
    ], style={"width": "250px", "margin-left": "20px"}),

    html.Div([
        html.Label("View Top N:", className="fw-bold"),
        dcc.Slider(
            id='top-n-slider', 
            min=0, max=MAX_TOP_N, step=1, value=0,
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style = {"width": "500px", 'padding': '0 30px'})
], style={"display": "flex", "align-items": "flex-end", "margin-bottom": "50px"}),

    # Graph Placeholder
    dcc.Graph(id="trade-chart"),
], className="container p-4")


# === CALLBACK TO UPDATE CHART ===
@app.callback(
    Output("trade-chart", "figure"),
    [Input("trade-direction", "value"), 
     Input("country-selection", "value"),
     Input('top-n-slider', 'value'),
     Input("sector-selection", "value")]
)
def update_chart(trade_type, selected_countries, top_n, selected_sector):
    # Start with raw df
    filtered_df = df.copy()

    # If a sector is selected, filter it 
    if selected_sector:
        filtered_df = filtered_df[filtered_df["Sector"] == selected_sector]
    
    else:
        # No sector selected → aggregate across all sectors
        filtered_df = (
            df.groupby(["Country", "Year"], as_index=False)[
                ["Export Volume", "Import Volume", "Total Volume", "Net Exports"]
            ].sum()
        )

    # Get top N countries based on filtered df
    top_n_countries = (
        filtered_df.groupby("Country")[trade_type]
        .mean()
        .nlargest(top_n)
        .index.tolist()
    )

    # Combine selected and top-N countries
    combined_countries = set(top_n_countries)
    if selected_countries:
        combined_countries.update(selected_countries)

    filtered_df = filtered_df[filtered_df["Country"].isin(combined_countries)]

    # Add title suffix
    title_suffix = f" — Sector: {selected_sector}" if selected_sector else ""

    fig = px.line(filtered_df, x="Year", y=trade_type, color="Country",
                  labels={"Year": "Year", trade_type: f"{trade_type} (Billion $)"},
                  title=f"Singapore’s {trade_type} Over Time{title_suffix}")

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


# # Dropdowns
# sidebar_controls =html.Div([
#     html.Div([
#         html.Label("Direction of Trade", className="fw-bold"),
#         dcc.Dropdown(
#             id="trade-direction",
#             options=[
#                 {"label": "Exports", "value": "Export Volume"},
#                 {"label": "Imports", "value": "Import Volume"},
#                 {"label": "Net Exports", "value": "Net Exports"},
#                 {"label": "Total Trade", "value": "Total Volume"},
#             ],
#             value="Export Volume",
#             className="mb-3",
#         ),
#     ], style={"width": "250px", "margin-right": "20px"}),

#     html.Div([
#         html.Label("Select Countries", className="fw-bold"),
#         dcc.Dropdown(
#             id="country-selection",
#             options=[{"label": c, "value": c} for c in df["Country"].unique()],
#             value=["China", "Malaysia", "USA", "Indonesia", "South Korea"],  # Default selection
#             multi=True,
#             className="mb-3",
#         ),
#     ], style={"width": "500px"}),

#     html.Div([
#         html.Label("Select Sector", className="fw-bold"),
#         dcc.Dropdown(
#             id="sector-selection",
#             options=[{"label": s, "value": s} for s in sorted(df["Sector"].unique())],
#             placeholder="All Sectors",
#             clearable=True,
#             className="mb-3",
#     ),
#     ], style={"width": "250px", "margin-left": "20px"}),

#     html.Div([
#         html.Label("View Top N:", className="fw-bold"),
#         dcc.Slider(
#             id='top-n-slider', 
#             min=0, max=MAX_TOP_N, step=1, value=0,
#             tooltip={"placement": "bottom", "always_visible": True},
#         ),
#     ], style = {"width": "500px", 'padding': '0 30px'})
# ], style={"display": "flex", "align-items": "flex-end", "margin-bottom": "0"})
