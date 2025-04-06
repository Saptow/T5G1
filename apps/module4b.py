from dash import Dash, dcc, html, Input, Output, State, callback_context, get_app
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd

# Load and prepare data
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

# Full layout including controls and graph
layout = html.Div([
    html.H2("Deviation from Baseline Forecast After News Input", className="mb-3"),

    html.Div([

        # Button Toggle
        html.Div([
            html.P("1. Select Country/Sector:", style={"marginBottom": "2px"}),
            html.Div([
                html.Button("By Country", id="btn-country", n_clicks=0, className="inactive", style={"marginRight": "5px"}),
                html.Button("By Sector", id="btn-sector", n_clicks=0, className="inactive")
            ])
        ], style={"marginRight": "30px"}),

        # Dropdown for filter
        html.Div([
            html.P("2. Specific Country/Sector:", style={"marginBottom": "2px"}),
            dcc.Dropdown(
                id="filter-dropdown",
                placeholder="",
                style={"width": "220px"}
            )
        ], style={"marginRight": "30px"}),

        # Trade Type Dropdown
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
    ], style={"display": "flex", "flexWrap": "wrap", "alignItems": "flex-end", "padding": "10px"}),

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

# Register callbacks
app.layout = layout 
register_callbacks(app)
