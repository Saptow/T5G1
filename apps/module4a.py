from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Load and prepare data
df = pd.read_csv("bilateral_trade_data_2026.csv")

# Data processing for total trade volume
reporter_total_df = df.groupby(["Reporter", "Time Period"])["Total Trade Volume"].sum().reset_index()
reporter_total_df.rename(columns={"Reporter": "Country", "Total Trade Volume": "Reporter Total"}, inplace=True)

partner_total_df = df.groupby(["Partner", "Time Period"])["Total Trade Volume"].sum().reset_index()
partner_total_df.rename(columns={"Partner": "Country", "Total Trade Volume": "Partner Total"}, inplace=True)

# Data processing for total export volume
reporter_export_df = df.groupby(["Reporter", "Time Period"])["Export Value"].sum().reset_index()
reporter_export_df.rename(columns={"Reporter": "Country", "Export Value": "Reporter Export"}, inplace=True)

partner_export_df = df.groupby(["Partner", "Time Period"])["Import Value"].sum().reset_index()
partner_export_df.rename(columns={"Partner": "Country", "Import Value": "Partner Export"}, inplace=True)

# Data processing for total import volume
reporter_import_df = df.groupby(["Reporter", "Time Period"])["Import Value"].sum().reset_index()
reporter_import_df.rename(columns={"Reporter": "Country", "Import Value": "Reporter Import"}, inplace=True)

partner_import_df = df.groupby(["Partner", "Time Period"])["Export Value"].sum().reset_index()
partner_import_df.rename(columns={"Partner": "Country", "Export Value": "Partner Import"}, inplace=True)

# Start with reporter_total_df
combined_df = reporter_total_df.copy()

# Merge in each of the other dataframes
combined_df = combined_df.merge(partner_total_df, on=["Country", "Time Period"], how="outer")
combined_df = combined_df.merge(reporter_export_df, on=["Country", "Time Period"], how="outer")
combined_df = combined_df.merge(partner_export_df, on=["Country", "Time Period"], how="outer")
combined_df = combined_df.merge(reporter_import_df, on=["Country", "Time Period"], how="outer")
combined_df = combined_df.merge(partner_import_df, on=["Country", "Time Period"], how="outer")

combined_df["Reporter Total"] = combined_df["Reporter Total"].fillna(0)
combined_df["Partner Total"] = combined_df["Partner Total"].fillna(0)
combined_df["Reporter Export"] = combined_df["Reporter Export"].fillna(0)
combined_df["Partner Export"] = combined_df["Partner Export"].fillna(0)
combined_df["Reporter Import"] = combined_df["Reporter Import"].fillna(0)
combined_df["Partner Import"] = combined_df["Partner Import"].fillna(0)
combined_df["Total Trade"] = combined_df["Reporter Total"] + combined_df["Partner Total"]
combined_df["Exports"] = combined_df["Reporter Export"] + combined_df["Partner Export"]
combined_df["Imports"] = combined_df["Reporter Import"] + combined_df["Partner Import"]

#Pivot the table to get each metric by Time Period
pivot = combined_df.pivot(index="Country", columns="Time Period", values=["Total Trade", "Exports", "Imports"])

#Calculate percentage change: (2026b - 2026a) / 2026a
percent_change = (pivot.xs("2026b", level=1, axis=1) - pivot.xs("2026a", level=1, axis=1)) / pivot.xs("2026a", level=1, axis=1)
percent_change.reset_index(inplace=True)
print(percent_change.head())

app = get_app()

# === Main Layout (Graph only) ===
layout = html.Div([
    html.H3("Deviation From Baseline Forecast After Geopolitical Shock", className="mb-4"),
    dcc.Graph(id="percent-change-bar")
])

# === CALLBACK TO UPDATE CHART ===
@app.callback(
    Output("percent-change-bar", "figure"),
    Input("trade-type-dropdown", "value")
)
def update_bar_chart(trade_type):
    df_sorted = percent_change.sort_values(by=trade_type, ascending=False)

    fig = px.bar(
        df_sorted,
        y="Country",
        x=trade_type,
        orientation='h',
        color=trade_type,
        color_continuous_scale=["red", "lightgray", "green"],
        labels={trade_type: "% Change"},
        title=f"Predicted Change in {trade_type} from 2026a (Baseline)"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Percentage Change (%)",
        xaxis_tickformat=".1%",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        height=450,  
        margin=dict(l=40, r=40, t=60, b=20)
    )

    return fig

# Topbar Controls (should only be visible when module is selected) 
sidebar_controls = html.Div([
    html.Div([
        html.Label("Select Trade Type", className="fw-bold"),
        dcc.Dropdown(
            id="trade-type-dropdown",
            options=[
                {"label": "Total Trade", "value": "Total Trade"},
                {"label": "Exports", "value": "Exports"},
                {"label": "Imports", "value": "Imports"},
            ],
            value="Total Trade",
            style={"width": "400px"}
        )
    ], className="mb-4"),
])
