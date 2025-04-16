from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pycountry

# === Load raw data ===
df_raw = pd.read_csv("sample_2026.csv")

# === Country code → full name mapping ===
country_code_to_name = {country.alpha_3: country.name for country in pycountry.countries}

# === Add Time Period and rename columns ===
df_raw["Time Period"] = df_raw["scenario"].map({"forecast": "2026a", "postshock": "2026b"})
df_raw.rename(columns={
    "country_a": "Reporter",
    "country_b": "Partner",
    "total_import_of_A_from_B": "Import Value",
    "trade_volume": "Total Trade Volume"
}, inplace=True)

# ✅ Convert country codes to full names for both Reporter and Partner
df_raw["Reporter"] = df_raw["Reporter"].map(country_code_to_name).fillna(df_raw["Reporter"])
df_raw["Partner"] = df_raw["Partner"].map(country_code_to_name).fillna(df_raw["Partner"])

# === Compute Export Value ===
df_raw["Export Value"] = df_raw["Total Trade Volume"] - df_raw["Import Value"]

# === Country-level aggregation ===
reporter_total_df = df_raw.groupby(["Reporter", "Time Period"])["Total Trade Volume"].sum().reset_index()
reporter_total_df.rename(columns={"Reporter": "Country", "Total Trade Volume": "Reporter Total"}, inplace=True)

partner_total_df = df_raw.groupby(["Partner", "Time Period"])["Total Trade Volume"].sum().reset_index()
partner_total_df.rename(columns={"Partner": "Country", "Total Trade Volume": "Partner Total"}, inplace=True)

reporter_export_df = df_raw.groupby(["Reporter", "Time Period"])["Export Value"].sum().reset_index()
reporter_export_df.rename(columns={"Reporter": "Country", "Export Value": "Reporter Export"}, inplace=True)

partner_export_df = df_raw.groupby(["Partner", "Time Period"])["Import Value"].sum().reset_index()
partner_export_df.rename(columns={"Partner": "Country", "Import Value": "Partner Export"}, inplace=True)

reporter_import_df = df_raw.groupby(["Reporter", "Time Period"])["Import Value"].sum().reset_index()
reporter_import_df.rename(columns={"Reporter": "Country", "Import Value": "Reporter Import"}, inplace=True)

partner_import_df = df_raw.groupby(["Partner", "Time Period"])["Export Value"].sum().reset_index()
partner_import_df.rename(columns={"Partner": "Country", "Export Value": "Partner Import"}, inplace=True)

# === Merge into combined_df ===
combined_df = reporter_total_df.copy()
for temp_df in [partner_total_df, reporter_export_df, partner_export_df, reporter_import_df, partner_import_df]:
    combined_df = combined_df.merge(temp_df, on=["Country", "Time Period"], how="outer")

combined_df.fillna(0, inplace=True)
combined_df["Total Trade"] = combined_df["Reporter Total"] + combined_df["Partner Total"]
combined_df["Exports"] = combined_df["Reporter Export"] + combined_df["Partner Export"]
combined_df["Imports"] = combined_df["Reporter Import"] + combined_df["Partner Import"]

# === Calculate country-level % change ===
pivot = combined_df.pivot(index="Country", columns="Time Period", values=["Total Trade", "Exports", "Imports"])
percent_change = (pivot.xs("2026b", level=1, axis=1) - pivot.xs("2026a", level=1, axis=1)) / pivot.xs("2026a", level=1, axis=1)
percent_change.reset_index(inplace=True)

# === Sector-level transformation ===
import_cols = [c for c in df_raw.columns if c.startswith("bec_") and "_import" in c]
export_cols = [c for c in df_raw.columns if c.startswith("bec_") and "_export" in c]

export_melted = df_raw[["Reporter", "Time Period"] + export_cols].melt(
    id_vars=["Reporter", "Time Period"], var_name="Sector", value_name="Export Value"
)
export_melted["Sector Group"] = "Sector " + export_melted["Sector"].str.extract(r"bec_(\d+)_")[0]

import_melted = df_raw[["Reporter", "Time Period"] + import_cols].melt(
    id_vars=["Reporter", "Time Period"], var_name="Sector", value_name="Import Value"
)
import_melted["Sector Group"] = "Sector " + import_melted["Sector"].str.extract(r"bec_(\d+)_")[0]

# === Merge import & export sectors ===
sector_df = pd.merge(
    export_melted[["Reporter", "Time Period", "Sector Group", "Export Value"]],
    import_melted[["Reporter", "Time Period", "Sector Group", "Import Value"]],
    on=["Reporter", "Time Period", "Sector Group"],
    how="outer"
)
sector_df.fillna(0, inplace=True)
sector_df["Total Trade Volume"] = sector_df["Export Value"] + sector_df["Import Value"]

# === Aggregate sector data by year ===
df_2026a = sector_df[sector_df["Time Period"] == "2026a"].groupby(["Reporter", "Sector Group"]).sum(numeric_only=True)
df_2026b = sector_df[sector_df["Time Period"] == "2026b"].groupby(["Reporter", "Sector Group"]).sum(numeric_only=True)
df_2026a.columns = [c + "_2026a" for c in df_2026a.columns]
df_2026b.columns = [c + "_2026b" for c in df_2026b.columns]

# === Combine and calculate sector % change ===
df_merged = df_2026a.join(df_2026b, how="inner").reset_index()
for col in ["Export Value", "Import Value", "Total Trade Volume"]:
    df_merged[f"{col} % Change"] = (
        (df_merged[f"{col}_2026b"] - df_merged[f"{col}_2026a"]) / df_merged[f"{col}_2026a"]
    ) * 100
app = get_app()

# === Main Layout (Graph only) ===
layout = html.Div([
    html.H3("Deviation From Baseline Forecast After Geopolitical Shock", className="mb-4"),

     html.Div([
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

    html.Div([
        html.Label("Select Sector", className="fw-bold"),
        dcc.Dropdown(
            id="sector-dropdown",
            options=[
                {"label": f"Sector {i}", "value": f"Sector_{i}"} for i in range(1, 9)
            ],
            value=None,
            clearable=True,
            placeholder="All Sectors",
            style={"width": "400px"}
        )
    ], className="mb-4")], style={"display": "flex", "flexDirection": "row", "alignItems": "center"}), 

    dcc.Graph(id="percent-change-bar")
])

# === CALLBACK TO UPDATE CHART ===
@app.callback(
    Output("percent-change-bar", "figure"),
    Input("trade-type-dropdown", "value"),
    Input("sector-dropdown", "value")
)
def update_bar_chart(trade_type,selected_sector):
    
    # Use the appropriate dataframe based on sector selection
    if selected_sector is None:
        df = percent_change.copy()
        df_sorted = percent_change.sort_values(by=trade_type, ascending=False)
        title_suffix = ""

    else:
        df_sorted = pivoted[pivoted["Sector Group"] == selected_sector].copy()
        df_sorted= df_sorted.sort_values(by=trade_type, ascending=False)
        title_suffix = f" — {selected_sector}"

    fig = px.bar(
        df_sorted,
        y="Country",
        x=trade_type,
        orientation='h',
        color=trade_type,
        color_continuous_scale=["red", "lightgray", "green"],
        labels={trade_type: "% Change"},
        title=f"Predicted Change in {trade_type} from 2026a (Baseline){title_suffix}"
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

# # Topbar Controls (should only be visible when module is selected) 
# sidebar_controls = html.Div([
#     html.Div([
#         html.Label("Select Trade Type", className="fw-bold"),
#         dcc.Dropdown(
#             id="trade-type-dropdown",
#             options=[
#                 {"label": "Total Trade", "value": "Total Trade"},
#                 {"label": "Exports", "value": "Exports"},
#                 {"label": "Imports", "value": "Imports"},
#             ],
#             value="Total Trade",
#             style={"width": "400px"}
#         )
#     ], className="mb-4"),

#     html.Div([
#         html.Label("Select Sector", className="fw-bold"),
#         dcc.Dropdown(
#             id="sector-dropdown",
#             options=[
#                 {"label": f"Sector {i}", "value": f"Sector_{i}"} for i in range(1, 9)
#             ],
#             value=None,
#             clearable=True,
#             placeholder="All Sectors",
#             style={"width": "400px"}
#         )
#     ], className="mb-4")
# ], style={"display": "flex", "flexDirection": "row", "alignItems": "center"})

# Load and prepare data (as previously done)
df = pd.read_csv("sample_2026.csv")

# Time Period
df["Time Period"] = df["scenario"].map({"forecast": "2026a", "postshock": "2026b"})

# Rename
df.rename(columns={
    "country_a": "Reporter",
    "country_b": "Partner",
    "total_import_of_A_from_B": "Import Value",
    "trade_volume": "Total Trade Volume"
}, inplace=True)

# Export value
df["Export Value"] = df["Total Trade Volume"] - df["Import Value"]

# Sector melt
import_cols = [c for c in df.columns if c.startswith("bec_") and "_import" in c]
export_cols = [c for c in df.columns if c.startswith("bec_") and "_export" in c]

export_melted = df[["Reporter", "Time Period"] + export_cols].melt(
    id_vars=["Reporter", "Time Period"], var_name="Sector", value_name="Export Value"
)
export_melted["Sector Group"] = "Sector " + export_melted["Sector"].str.extract(r"bec_(\d+)_")[0]

import_melted = df[["Reporter", "Time Period"] + import_cols].melt(
    id_vars=["Reporter", "Time Period"], var_name="Sector", value_name="Import Value"
)
import_melted["Sector Group"] = "Sector " + import_melted["Sector"].str.extract(r"bec_(\d+)_")[0]

# Merge sector data
df = pd.merge(
    export_melted[["Reporter", "Time Period", "Sector Group", "Export Value"]],
    import_melted[["Reporter", "Time Period", "Sector Group", "Import Value"]],
    on=["Reporter", "Time Period", "Sector Group"],
    how="outer"
)
df.fillna(0, inplace=True)
df["Total Trade Volume"] = df["Export Value"] + df["Import Value"]

# Group by year
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

country_code_to_name = {c.alpha_3: c.name for c in pycountry.countries}
df_merged["Reporter"] = df_merged["Reporter"].map(country_code_to_name).fillna(df_merged["Reporter"])

# Calculate % change
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

# Callback registration
def register_callbacks(app):
    @app.callback(
        Output("btn-country", "className"),
        Output("btn-sector", "className"),
        Output("filter-dropdown", "options"),
        Output("filter-dropdown", "placeholder"),
        Output("filter-dropdown", "value"),
        Input("btn-country", "n_clicks"),
        Input("btn-sector", "n_clicks")
    )
    def update_button_style(n_country, n_sector):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        clicked = ctx.triggered[0]["prop_id"].split(".")[0]

        if clicked == "btn-country":
            return "active", "inactive", [{"label": c, "value": c} for c in sorted(df_merged["Reporter"].unique())], "Choose a specific country", None
        else:
            return "inactive", "active", [{"label": s, "value": s} for s in sorted(df_merged["Sector Group"].unique())], "Choose a specific sector", None

@app.callback(
    Output("dumbbell-graph", "figure"),
    Input("filter-dropdown", "value"),
    Input("trade-type-dropdown", "value"),
    State("btn-country", "className"),
    State("btn-sector", "className")
)
def update_graph(selected_filter, trade_type, class_country, class_sector):
    if not selected_filter or not trade_type:
        # Return an empty chart with title prompting user
        return go.Figure(layout={
            "title": "Please select a country/sector and trade type to view changes."
        })

    change_col = f"{trade_type} % Change"
    df_plot = df_merged.copy()

    if class_country == "active":
        df_plot = df_plot[df_plot["Reporter"] == selected_filter]
        y_axis = df_plot["Sector Group"]
    else:
        df_plot = df_plot[df_plot["Sector Group"] == selected_filter]
        y_axis = df_plot["Reporter"]

    df_positive = df_plot[df_plot[change_col] >= 0]
    df_negative = df_plot[df_plot[change_col] < 0]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=y_axis,
        x=df_plot[f"{trade_type}_2026a"],
        mode="markers",
        name="Before (grey circle)",
        marker=dict(color="gray", size=12),
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        y=df_positive[y_axis.name],
        x=df_positive[f"{trade_type}_2026b"],
        mode="markers",
        name="After (increase %)",
        marker=dict(color="green", size=12),
        text=[
            f"Export: Before = {ev_before:.2f}, After = {ev_after:.2f}<br>"
            f"Import: Before = {iv_before:.2f}, After = {iv_after:.2f}<br>"
            f"Total: Before = {tv_before:.2f}, After = {tv_after:.2f}<br>"
            f"% Change: {chg:.2f}%"
            for ev_before, ev_after, iv_before, iv_after, tv_before, tv_after, chg in zip(
                df_positive["Export Value_2026a"],
                df_positive["Export Value_2026b"],
                df_positive["Import Value_2026a"],
                df_positive["Import Value_2026b"],
                df_positive["Total Trade Volume_2026a"],
                df_positive["Total Trade Volume_2026b"],
                df_positive[change_col]
            )
        ],
        hoverinfo="text"
    ))

    fig.add_trace(go.Scatter(
        y=df_negative[y_axis.name],
        x=df_negative[f"{trade_type}_2026b"],
        mode="markers",
        name="After (decrease %)",
        marker=dict(color="red", size=12),
        text=[
            f"Export: before = {ev_before:.2f}, after = {ev_after:.2f}<br>"
            f"Import: before = {iv_before:.2f}, after = {iv_after:.2f}<br>"
            f"Total: before = {tv_before:.2f}, after = {tv_after:.2f}<br>"
            f"% Change: {chg:.2f}%"
            for ev_before, ev_after, iv_before, iv_after, tv_before, tv_after, chg in zip(
                df_negative["Export Value_2026a"],
                df_negative["Export Value_2026b"],
                df_negative["Import Value_2026a"],
                df_negative["Import Value_2026b"],
                df_negative["Total Trade Volume_2026a"],
                df_negative["Total Trade Volume_2026b"],
                df_negative[change_col]
            )
        ],
        hoverinfo="text"
    ))

    for i in range(len(df_plot)):
        fig.add_shape(type="line",
                      y0=y_axis.iloc[i], x0=df_plot[f"{trade_type}_2026a"].iloc[i],
                      y1=y_axis.iloc[i], x1=df_plot[f"{trade_type}_2026b"].iloc[i],
                      line=dict(color="lightgray", width=4))

    fig.update_layout(
        title=f"Change in {trade_type} after Geopolitical Shock",
        xaxis_title=trade_type,
        yaxis_title="" if class_country == "active" else "Country",
        height=600
    )

    return fig

# Register to current app instance

app.layout = layout 
register_callbacks(app)

## Combined DiD 