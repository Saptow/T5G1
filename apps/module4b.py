from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go

df = pd.read_csv("sample_trade_data_geopo.csv")
df["Year"] = df["Year"].astype(str)

app = get_app()

# Layout
layout = html.Div([
    html.H4("Geopolitical Distance vs. Total Trade Over Time", className="mb-4"),

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

# Topbar Controls (should only be visible when module is selected) 

sidebar_controls = html.Div([
    html.Label("Select a Country:", className="fw-bold"),
        dcc.Dropdown(
            id="country-selector",
            options=[{"label": c, "value": c} for c in sorted(df["Country"].unique())],
            value="Germany",  # default
            style={"width": "300px"}
        ),
    ], className="mb-4"),
    
        