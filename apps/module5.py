# module 5 new 

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash

app = get_app()

# === SHARED DATA PREPARATION ===
df = pd.read_csv("bilateral_trade_data_2026.csv")

# Dumbbell data

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

# Ranking data
reporter_total_df = df.groupby(["Reporter", "Time Period"])["Total Trade Volume"].sum().reset_index()
reporter_total_df.rename(columns={"Reporter": "Country", "Total Trade Volume": "Reporter Total"}, inplace=True)
partner_total_df = df.groupby(["Partner", "Time Period"])["Total Trade Volume"].sum().reset_index()
partner_total_df.rename(columns={"Partner": "Country", "Total Trade Volume": "Partner Total"}, inplace=True)
reporter_export_df = df.groupby(["Reporter", "Time Period"])["Export Value"].sum().reset_index()
reporter_export_df.rename(columns={"Reporter": "Country", "Export Value": "Reporter Export"}, inplace=True)
partner_export_df = df.groupby(["Partner", "Time Period"])["Import Value"].sum().reset_index()
partner_export_df.rename(columns={"Partner": "Country", "Import Value": "Partner Export"}, inplace=True)
reporter_import_df = df.groupby(["Reporter", "Time Period"])["Import Value"].sum().reset_index()
reporter_import_df.rename(columns={"Reporter": "Country", "Import Value": "Reporter Import"}, inplace=True)
partner_import_df = df.groupby(["Partner", "Time Period"])["Export Value"].sum().reset_index()
partner_import_df.rename(columns={"Partner": "Country", "Export Value": "Partner Import"}, inplace=True)

combined_df = reporter_total_df.copy()
combined_df = combined_df.merge(partner_total_df, on=["Country", "Time Period"], how="outer")
combined_df = combined_df.merge(reporter_export_df, on=["Country", "Time Period"], how="outer")
combined_df = combined_df.merge(partner_export_df, on=["Country", "Time Period"], how="outer")
combined_df = combined_df.merge(reporter_import_df, on=["Country", "Time Period"], how="outer")
combined_df = combined_df.merge(partner_import_df, on=["Country", "Time Period"], how="outer")

combined_df.fillna(0, inplace=True)
combined_df["Total Trade"] = combined_df["Reporter Total"] + combined_df["Partner Total"]
combined_df["Exports"] = combined_df["Reporter Export"] + combined_df["Partner Export"]
combined_df["Imports"] = combined_df["Reporter Import"] + combined_df["Partner Import"]

pivot = combined_df.pivot(index="Country", columns="Time Period", values=["Total Trade", "Exports", "Imports"])
percent_change = (pivot.xs("2026b", level=1, axis=1) - pivot.xs("2026a", level=1, axis=1)) / pivot.xs("2026a", level=1, axis=1)
percent_change.reset_index(inplace=True)

# === Create pivoted for sector-based ranking view ===

# Group by sector and country to prepare detailed trade change breakdowns
reporter_total_sector_df = df.groupby(["Reporter", "Time Period", "Sector Group"])["Total Trade Volume"].sum().reset_index()
reporter_total_sector_df.rename(columns={"Reporter": "Country", "Total Trade Volume": "Reporter Total"}, inplace=True)

partner_total_sector_df = df.groupby(["Partner", "Time Period", "Sector Group"])["Total Trade Volume"].sum().reset_index()
partner_total_sector_df.rename(columns={"Partner": "Country", "Total Trade Volume": "Partner Total"}, inplace=True)

reporter_export_sector_df = df.groupby(["Reporter", "Time Period", "Sector Group"])["Export Value"].sum().reset_index()
reporter_export_sector_df.rename(columns={"Reporter": "Country", "Export Value": "Reporter Export"}, inplace=True)

partner_export_sector_df = df.groupby(["Partner", "Time Period", "Sector Group"])["Import Value"].sum().reset_index()
partner_export_sector_df.rename(columns={"Partner": "Country", "Import Value": "Partner Export"}, inplace=True)

reporter_import_sector_df = df.groupby(["Reporter", "Time Period", "Sector Group"])["Import Value"].sum().reset_index()
reporter_import_sector_df.rename(columns={"Reporter": "Country", "Import Value": "Reporter Import"}, inplace=True)

partner_import_sector_df = df.groupby(["Partner", "Time Period", "Sector Group"])["Export Value"].sum().reset_index()
partner_import_sector_df.rename(columns={"Partner": "Country", "Export Value": "Partner Import"}, inplace=True)

combined_sector_df = reporter_total_sector_df.copy()
combined_sector_df = combined_sector_df.merge(partner_total_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df = combined_sector_df.merge(reporter_export_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df = combined_sector_df.merge(partner_export_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df = combined_sector_df.merge(reporter_import_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df = combined_sector_df.merge(partner_import_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")

combined_sector_df.fillna(0, inplace=True)
combined_sector_df["Total Trade"] = combined_sector_df["Reporter Total"] + combined_sector_df["Partner Total"]
combined_sector_df["Exports"] = combined_sector_df["Reporter Export"] + combined_sector_df["Partner Export"]
combined_sector_df["Imports"] = combined_sector_df["Reporter Import"] + combined_sector_df["Partner Import"]

# Melt and pivot to calculate percentage change
melted = combined_sector_df.melt(id_vars=['Country', 'Time Period', 'Sector Group'], 
                 var_name='Metric_Year', 
                 value_name='Value')
melted[['Metric', 'Year']] = melted['Metric_Year'].str.extract(r'([A-Za-z ]+)\\s?(\\d{4}\\w)?')
melted['Year'] = melted['Year'].fillna(melted['Time Period'])

pivoted = melted.pivot_table(
    index=['Country', 'Sector Group'],
    columns=['Metric', 'Year'],
    values='Value',
    aggfunc='first'
).reset_index()

# Flatten and calculate percentage change
pivoted.columns = ['_'.join(col).strip('_') for col in pivoted.columns.values]
pivoted = pivoted.rename(columns={
    'Country_': 'Country',
    'Sector Group_': 'Sector Group',
    'Exports_2026a': 'Export_2026a',
    'Imports_2026a': 'Import_2026a',
    'Total Trade_2026a': 'Total_Trade_2026a',
    'Exports_2026b': 'Export_2026b',
    'Imports_2026b': 'Import_2026b',
    'Total Trade_2026b': 'Total_Trade_2026b'
})

for col in ["Export", "Import", "Trade"]:
    pivoted[f"{col}s"] = (
        (pivoted[f"{col}_2026b"] - pivoted[f"{col}_2026a"]) / pivoted[f"{col}_2026a"].replace(0, 1)
    ) * 100


# === LAYOUT ===
layout = html.Div([
    dcc.Store(id="view-toggle", data='country'),

    html.H2("Sectoral Growth Opportunities After Geopolitical Shock", className="text-center mb-3"),

    html.Div([
        html.Div([
            html.P("1. Select Country/Sector:", style={"marginBottom": "2px"}),
            html.Div([
                html.Button("By Country", id="btn-country", n_clicks=0, className="inactive", style={"marginRight": "5px"}),
                html.Button("By Sector", id="btn-sector", n_clicks=0, className="inactive")
            ])
        ], style={"marginRight": "30px"}),

        html.Div([
            html.P("2. Specific Country/Sector:", style={"marginBottom": "2px"}),
            dcc.Dropdown(id="filter-dropdown", placeholder="", style={"width": "220px"})
        ], style={"marginRight": "30px"}),

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
    ], style={"display": "flex", "flexWrap": "wrap", "alignItems": "flex-end"}, className="mb-4"),

    dcc.Tabs(id="trade-tabs", value="ranking", children=[
        dcc.Tab(label="Ranking", value="ranking"),
        dcc.Tab(label="Dumbbell", value="dumbbell"),
        dcc.Tab(label="Bubble", value="bubble")
    ]),

    html.Div(id="tab-content")
])

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
    State("btn-country", "className"),
    State("btn-sector", "className")
)
def update_dumbbell_chart(selected_filter, trade_type, class_country, class_sector):
    if not selected_filter or not trade_type:
        raise dash.exceptions.PreventUpdate

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
        yaxis_title="" if class_country == "active" else "Country",
        height=600
    )
    return fig

# === RANKING CALLBACK ===
@app.callback(
    Output("percent-change-bar", "figure"),
    Input("trade-type-dropdown", "value"),
    Input("filter-dropdown", "value")
)
def update_ranking_chart(trade_type, selected_sector):
    if selected_sector is None:
        df_sorted = percent_change.sort_values(by=trade_type, ascending=False)
        title_suffix = ""
    else:
        df_sorted = pivoted[pivoted["Sector Group"] == selected_sector].sort_values(by=trade_type, ascending=False)
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
        height=450
    )
    return fig

sidebar_controls = html.Div([])