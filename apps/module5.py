# module 5 new 

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, callback_context, get_app, MATCH, ALL
import dash
import pycountry 
import dash_daq as daq


app = get_app()

# === 1. LOAD AND TRANSFORM DATA ONCE ===
df_raw = pd.read_csv("sample_2026.csv")

# Map country codes
country_code_to_name = {c.alpha_3: c.name for c in pycountry.countries}
df_raw["Time Period"] = df_raw["scenario"].map({"forecast": "2026a", "postshock": "2026b"})
df_raw.rename(columns={
    "country_a": "Reporter",
    "country_b": "Partner",
    "total_import_of_A_from_B": "Import Value",
    "trade_volume": "Total Trade Volume"
}, inplace=True)
df_raw["Reporter"] = df_raw["Reporter"].map(country_code_to_name).fillna(df_raw["Reporter"])
df_raw["Partner"] = df_raw["Partner"].map(country_code_to_name).fillna(df_raw["Partner"])
df_raw["Export Value"] = df_raw["Total Trade Volume"] - df_raw["Import Value"]

# === 2. COUNTRY-LEVEL AGGREGATION ===
country_metrics = {}
for role, col_name in [("Reporter", "Reporter"), ("Partner", "Partner")]:
    for metric, new_col in [
        ("Total Trade Volume", f"{col_name} Total"),
        ("Export Value", f"{col_name} Export"),
        ("Import Value", f"{col_name} Import")
    ]:
        temp = df_raw.groupby([role, "Time Period"])[metric].sum().reset_index()
        temp.rename(columns={role: "Reporter", metric: new_col}, inplace=True)
        country_metrics[new_col] = temp

combined_df = country_metrics["Reporter Total"]
for key in list(country_metrics.keys())[1:]:
    combined_df = combined_df.merge(country_metrics[key], on=["Reporter", "Time Period"], how="outer")

combined_df.fillna(0, inplace=True)
combined_df["Total Trade Volume"] = combined_df["Reporter Total"] + combined_df["Partner Total"]
combined_df["Export Value"] = combined_df["Reporter Export"] + combined_df["Partner Export"]
combined_df["Import Value"] = combined_df["Reporter Import"] + combined_df["Partner Import"]

pivot = combined_df.pivot(index="Reporter", columns="Time Period", values=["Total Trade Volume", "Export Value", "Import Value"])
percent_change = (pivot.xs("2026b", level=1, axis=1) - pivot.xs("2026a", level=1, axis=1)) / pivot.xs("2026a", level=1, axis=1)*100
percent_change.reset_index(inplace=True)


# === 3. SECTOR-LEVEL TRANSFORMATION ===
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

sector_df = pd.merge(
    export_melted[["Reporter", "Time Period", "Sector Group", "Export Value"]],
    import_melted[["Reporter", "Time Period", "Sector Group", "Import Value"]],
    on=["Reporter", "Time Period", "Sector Group"],
    how="outer"
)
sector_df.fillna(0, inplace=True)
sector_df["Total Trade Volume"] = sector_df["Export Value"] + sector_df["Import Value"]

df_2026a = sector_df[sector_df["Time Period"] == "2026a"].groupby(["Reporter", "Sector Group"]).sum(numeric_only=True)
df_2026b = sector_df[sector_df["Time Period"] == "2026b"].groupby(["Reporter", "Sector Group"]).sum(numeric_only=True)

df_2026a.columns = [c + "_2026a" for c in df_2026a.columns]
df_2026b.columns = [c + "_2026b" for c in df_2026b.columns]

df_merged = df_2026a.join(df_2026b, how="inner").reset_index()

for col in ["Export Value", "Import Value", "Total Trade Volume"]:
    df_merged[f"{col}"] = (
        (df_merged[f"{col}_2026b"] - df_merged[f"{col}_2026a"]) / df_merged[f"{col}_2026a"].replace(0, 1)
    ) * 100


# for col in ["Export", "Import", "Trade"]:
#     pivoted[f"{col}s"] = (
#         (pivoted[f"{col}_2026b"] - pivoted[f"{col}_2026a"]) / pivoted[f"{col}_2026a"].replace(0, 1)
#     ) * 100

layout = html.Div([

    dcc.Store(id="view-toggle", data='country'),

    html.Div([  
        # === OVERLAY (Positioned absolutely within this container) ===
        html.Div(
            id="page-overlay",
            children=[
                html.Div("No visualisation is currently displayed as no prediction input has been provided. " \
                "Click the Predict button and enter a URL or select a sample article to view the page.", className="overlay-text")
            ],
            style={
                "position": "absolute",
                "top": 0,
                "left": 0,
                "width": "100%",
                "height": "100%",
                "backgroundColor": "rgba(0, 0, 0, 0.6)",
                # "backgroundImage": "url('/homepage.png')",
                # "backgroundSize": "cover",
                "zIndex": 10,
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "textAlign": "center",
                "fontSize": "1.5rem",
                "fontWeight": "bold",
                "color": "white",
            }
        ),

        # === Main Page Content ===
        html.Div(id="main-page-content", children=[
            html.H2("Which countries and sectors are most impacted from this development?", className="mb-3"),
            html.H5("View in real-time the biggest winners and losers from this news, across countries and sectors"),
            html.Div([
                # 1. Toggle Switch Section
            html.Div([
                html.P("1. Sector/Country View:", style={"marginBottom": "6px"}),

                html.Div([
                    html.Div("Country View", style={"marginRight": "10px", "marginBottom": "0"}),
                    daq.BooleanSwitch(
                        id="view-toggle-switch",
                        on=False, # False means Country View is selected (default)
                        color="#000000",  # black color when ON
                        style={"marginRight": "10px"}
                    ),
                    html.Div("Sector View", style={"marginLeft": "10px", "marginBottom": "0"})
                ], style={"display": "flex", "alignItems": "center"})
            ], style={"marginRight": "30px"}),

            # 2. Filter Dropdown
            html.Div([
                html.P("2. Specific Country/Sector:", style={"marginBottom": "2px"}),
                dcc.Dropdown(id="filter-dropdown", placeholder = '', style={"width": "220px"})
            ], style={"marginRight": "30px"}),

            # 3. Trade Type Dropdown
            html.Div([
                html.P("3. Trade Type:", style={"marginBottom": "2px"}),
                dcc.Dropdown(
                    id="trade-type-dropdown",
                    options=[
                        {"label": "Total Trade Volume", "value": "Total Trade Volume"},
                        {"label": "Export Value", "value": "Export Value"},
                        {"label": "Import Value", "value": "Import Value"}
                    ],
                    value = "Total Trade Volume",
                    style={"width": "220px"}
                )
            ])
            ], style={"display": "flex", "flexWrap": "wrap", "alignItems": "flex-end"}, className="mb-4"),

            dcc.Tabs(id="trade-tabs", value="ranking", children=[
                dcc.Tab(label="Ranking (Sector selection is optional)", value="ranking"),
                dcc.Tab(label="Dumbbell", value="dumbbell"),
                dcc.Tab(label="Bubble", value="bubble")
            ]),
            html.Div(id="tab-content")
        ])
    ], style={"position": "relative"})  
])


# Callback to control overlay visibility

@app.callback(
    Output("page-overlay", "style"),
    Input("uploaded-url", "data")
)
def toggle_overlay(news_url_data):
    if news_url_data:
        return {"display": "none"}  
    return {
        "position": "absolute",
        "top": 0,
        "left": 0,
        "width": "100%",
        "height": "100%",
        "backgroundColor": "rgba(0, 0, 0, 0.6)",
        "backgroundImage": "url('/assets/homepage.png')",
        # "backgroundSize": "cover",
        # "backgroundColor": "white",
        "zIndex": 9999,
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "fontSize": "2rem",
        "fontWeight": "bold",
        "color": "black",
    }


# === TAB SELECTION CALLBACK ===
@app.callback(
    Output("tab-content", "children"),
    Input("trade-tabs", "value")
)
def render_tab(tab):
    if tab == "ranking":
        return dcc.Graph(id="percent-change-bar", config={"displayModeBar": False})
    elif tab == "dumbbell":
        return dcc.Graph(id="dumbbell-graph", config={"displayModeBar": False})
    elif tab == "bubble":
        return html.Div([html.H4("Bubble Chart Coming Soon!", className="text-center mt-4")])

# === DUMBBELL CALLBACKS ===
@app.callback(
    Output("filter-dropdown", "options"),
    Output("filter-dropdown", "placeholder"),
    Output("filter-dropdown", "value"),
    Input("view-toggle-switch", "on")
)
def update_dropdown_options(is_country_view):
    if is_country_view:
        options = [{"label": c, "value": c} for c in sorted(df_merged["Reporter"].unique())]
        return options, "Choose a specific country", options[0]["value"] if options else None
    else:
        options = [{"label": s, "value": s} for s in sorted(df_merged["Sector Group"].unique())]
        # Default to "Sector 1" if it's in the list
        default_value = "Sector 1" if any(s["value"] == "Sector 1" for s in options) else options[0]["value"] if options else None
        return options, "Choose a specific sector", default_value


def update_button_style(n_country, n_sector):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    clicked = ctx.triggered[0]["prop_id"].split(".")[0]

    if clicked == "btn-country":
        return "active", "inactive", [{"label": c, "value": c} for c in sorted(df_merged["Reporter"].unique())], "Choose a specific country", None
    else:
        return "inactive", "active", [{"label": s, "value": s} for s in sorted(df_merged["Sector Group"].unique())], "Choose a specific sector", None

@app.callback(
    Output("dumbbell-graph", "figure"),
    Input("filter-dropdown", "value"),
    Input("trade-type-dropdown", "value"),
    Input("view-toggle-switch", "on")  # this returns True (country options in dropdown2) or False (sector options in dropdown2)
)
def update_dumbbell_chart(selected_filter, trade_type, is_country_view):
    if not selected_filter or not trade_type:
        raise dash.exceptions.PreventUpdate

    change_col = f"{trade_type}"
    df_plot = df_merged.copy()

    if is_country_view:
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
        name="Before (grey)",
        marker=dict(color="gray", size=12),
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        y=df_positive[y_axis.name],
        x=df_positive[f"{trade_type}_2026b"],
        mode="markers",
        name="After (increase)",
        marker=dict(color="green", size=12),
        text=[f"% Change: {chg:.2f}%" for chg in df_positive[change_col]],
        hoverinfo="text"
    ))

    fig.add_trace(go.Scatter(
        y=df_negative[y_axis.name],
        x=df_negative[f"{trade_type}_2026b"],
        mode="markers",
        name="After (decrease)",
        marker=dict(color="red", size=12),
        text=[f"% Change: {chg:.2f}%" for chg in df_negative[change_col]],
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
        yaxis_title="" if is_country_view else "Country",
        height=600, 
        plot_bgcolor="#ebebeb",
        paper_bgcolor="#ffffff"
    )
    return fig


# === RANKING CALLBACK ===
@app.callback(
    Output("percent-change-bar", "figure"),
    Input("filter-dropdown", "value"),
    Input("trade-type-dropdown", "value"),
    Input("view-toggle-switch", "on")  # this returns True (country) or False (sector)
)
def update_ranking_chart(selected_filter, trade_type, is_country_view):
    if not is_country_view:
        if not selected_filter:
            df_sorted = percent_change.sort_values(by=trade_type, ascending=False)
            title_suffix = ""
            y_value = "Reporter"
        else:
            df_sorted = df_merged[df_merged["Sector Group"] == selected_filter].sort_values(by=trade_type, ascending=False)
            title_suffix = f" — {selected_filter}"
            y_value = "Reporter"

    if is_country_view:
        df_sorted = df_merged[df_merged["Reporter"] == selected_filter].sort_values(by=trade_type, ascending=False)
        title_suffix = f" — {selected_filter}"
        y_value = "Sector Group"

    fig = px.bar(
        df_sorted,
        y= y_value,
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
        xaxis_tickformat=".1f",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        height=450
    )
    return fig

sidebar_controls = html.Div([])