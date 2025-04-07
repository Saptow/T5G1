from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
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



# Data processing for total trade volume by sector
reporter_total_sector_df = df.groupby(["Reporter", "Time Period", "Sector Group"])["Total Trade Volume"].sum().reset_index()
reporter_total_sector_df.rename(columns={"Reporter": "Country", "Total Trade Volume": "Reporter Total"}, inplace=True)

partner_total_sector_df = df.groupby(["Partner", "Time Period", "Sector Group"])["Total Trade Volume"].sum().reset_index()
partner_total_sector_df.rename(columns={"Partner": "Country", "Total Trade Volume": "Partner Total"}, inplace=True)

# Data processing for exports by sector
reporter_export_sector_df = df.groupby(["Reporter", "Time Period", "Sector Group"])["Export Value"].sum().reset_index()
reporter_export_sector_df.rename(columns={"Reporter": "Country", "Export Value": "Reporter Export"}, inplace=True)

partner_export_sector_df = df.groupby(["Partner", "Time Period", "Sector Group"])["Import Value"].sum().reset_index()
partner_export_sector_df.rename(columns={"Partner": "Country", "Import Value": "Partner Export"}, inplace=True)

# Data processing for imports by sector
reporter_import_sector_df = df.groupby(["Reporter", "Time Period", "Sector Group"])["Import Value"].sum().reset_index()
reporter_import_sector_df.rename(columns={"Reporter": "Country", "Import Value": "Reporter Import"}, inplace=True)

partner_import_sector_df = df.groupby(["Partner", "Time Period", "Sector Group"])["Export Value"].sum().reset_index()
partner_import_sector_df.rename(columns={"Partner": "Country", "Export Value": "Partner Import"}, inplace=True)

# Start with reporter_total_df
combined_sector_df = reporter_total_sector_df.copy()

# # Merge in each of the other dataframes
combined_sector_df = combined_sector_df.merge(partner_total_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df = combined_sector_df.merge(reporter_export_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df = combined_sector_df.merge(partner_export_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df = combined_sector_df.merge(reporter_import_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df = combined_sector_df.merge(partner_import_sector_df, on=["Country", "Time Period", "Sector Group"], how="outer")
combined_sector_df["Total Trade"] = combined_sector_df["Reporter Total"] + combined_sector_df["Partner Total"]
combined_sector_df["Exports"] = combined_sector_df["Reporter Export"] + combined_sector_df["Partner Export"]
combined_sector_df["Imports"] = combined_sector_df["Reporter Import"] + combined_sector_df["Partner Import"]

combined_sector_df = combined_sector_df.drop(["Reporter Total", "Partner Total", "Reporter Export", "Partner Export", "Reporter Import", "Partner Import"], axis =1)

# Melt the dataframe to long format
melted = combined_sector_df.melt(id_vars=['Country', 'Time Period', 'Sector Group'], 
                 var_name='Metric_Year', 
                 value_name='Value')

# Separate the Metric and Year
melted[['Metric', 'Year']] = melted['Metric_Year'].str.extract(r'(\w+)\s?(\d{4}\w)?$')
# For any metrics without year (like Total Trade), assign the Time Period
melted['Year'] = melted['Year'].fillna(melted['Time Period'])

# Pivot to get the desired structure
pivoted = melted.pivot_table(
    index=['Country', 'Sector Group'],
    columns=['Metric', 'Year'],
    values='Value',
    aggfunc='first'  
).reset_index()


# Flatten the multi-index columns and rename
pivoted.columns = ['_'.join(col).strip('_') for col in pivoted.columns.values]
pivoted = pivoted.rename(columns={
    'Country_': 'Country',
    'Sector Group_': 'Sector Group',
    'Exports_2026a': 'Export_2026a',
    'Imports_2026a': 'Import_2026a',
    'Total_Trade_2026a': 'Total_Trade_2026a',
    'Exports_2026b': 'Export_2026b',
    'Imports_2026b': 'Import_2026b',
    'Total_Trade_2026b': 'Total_Trade_2026b'
})


for col in ["Export", "Import", "Trade"]:
    pivoted[f"{col}"] = (
        (pivoted[f"{col}_2026b"] - pivoted[f"{col}_2026a"]) / pivoted[f"{col}_2026a"]
    ) * 100
pivoted.rename(columns={"Reporter": "Country", "Export": "Exports", "Import": "Imports", "Trade": "Total Trade"}, inplace =True)

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

#####################################

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
        if not selected_filter:
            selected_filter = df_merged['Reporter'].unique()[0]
            trade_type = 'Total Trade Volume'
            class_country = 'active'
            class_sector = 'inactive'
        if not selected_filter or not trade_type:
            return go.Figure()

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