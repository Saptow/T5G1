import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
import dash_daq as daq
from dash.exceptions import PreventUpdate

# === Load and Prepare Data ===
df_raw = pd.read_csv("data/final/historical_data.csv")
prediction_df = pd.read_csv("sample_2026.csv")
prediction_df = prediction_df[prediction_df["scenario"] == "postshock"].drop(columns=["scenario"])
prediction_df['year'] = pd.to_numeric(prediction_df['year'], errors='coerce')
df_raw['year'] = pd.to_numeric(df_raw['year'], errors='coerce')

# Merge historical and prediction data
df_combined_all = pd.concat([df_raw, prediction_df], ignore_index=True)

app = get_app()
# === Dictionaries ===
SECTOR_LABELS = {
    "bec_1": "Food and Agriculture",
    "bec_2": "Energy and Mining",
    "bec_3": "Construction and Housing",
    "bec_4": "Textile and Footwear",
    "bec_5": "Transport and Travel",
    "bec_6": "ICT and Business",
    "bec_7": "Health and Education",
    "bec_8": "Government and Others"
}
SECTOR_CODES = list(SECTOR_LABELS.keys())

COUNTRY_LABELS = {
    "ARE": "United Arab Emirates",
    "AUS": "Australia",
    "CHE": "Switzerland",
    "CHN": "China",
    "DEU": "Germany",
    "FRA": "France",
    "HKG": "Hong Kong",
    "IDN": "Indonesia",
    "IND": "India",
    "JPN": "Japan",
    "KOR": "South Korea",
    "MYS": "Malaysia",
    "NLD": "Netherlands",
    "PHL": "Philippines",
    "SGP": "Singapore",
    "THA": "Thailand",
    "USA": "United States",
    "VNM": "Vietnam"
}
COUNTRY_NAMES = {v: k for k, v in COUNTRY_LABELS.items()}
COUNTRY_LIST = sorted(COUNTRY_LABELS.values())

# === Helper Functions ===
def calculate_volume(df_view, sector_code, trade_type):
    if trade_type == "export":
        col = f"{sector_code}_export_A_to_B"
        df_view["value"] = df_view[col]
    elif trade_type == "import":
        col = f"{sector_code}_import_A_from_B"
        df_view["value"] = df_view[col]
    else:
        exp_col = f"{sector_code}_export_A_to_B"
        imp_col = f"{sector_code}_import_A_from_B"
        df_view["value"] = df_view[exp_col] + df_view[imp_col]
    return df_view

def calculate_percentage(df_view, trade_type):
    if trade_type == "export":
        trade_cols = [f"{code}_export_A_to_B" for code in SECTOR_CODES]
    elif trade_type == "import":
        trade_cols = [f"{code}_import_A_from_B" for code in SECTOR_CODES]
    else:
        trade_cols = [f"{code}_export_A_to_B" for code in SECTOR_CODES] + \
                      [f"{code}_import_A_from_B" for code in SECTOR_CODES]

    df_view["total"] = df_view[trade_cols].sum(axis=1)
    df_view["percentage"] = 100 * df_view["value"] / df_view["total"].replace(0, 1)
    return df_view

def calculate_sector_shares(df_view, sector_code, trade_type):
    df_view = calculate_volume(df_view, sector_code, trade_type)
    df_view = calculate_percentage(df_view, trade_type)
    return df_view


# === New Sector-as-Main-Input Module with ID suffix "8abc" ===

# --- Only changes are: input param becomes sector; sector buttons are now partner country buttons ---
# --- All other logic (data loading, tab layout, toggle, graphs, etc.) remain the same ---

layout = html.Div([
    dcc.Store(id="selected-sector8abc", data=SECTOR_CODES[0]),
    dcc.Store(id="selected-partners-multi8abc", data=["AUS", "CHN"]),
    dcc.Store(id="trade-type-select8abc", data='total'),
    dcc.Store(id="display-mode8abc", data='volume'),

    html.H2("Sector Trade Trends Over Time (Partner-Centric View)", className="text-center mb-4"),

    html.Div([
        html.Div([
            html.Label("Select a Country", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select8abc',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value='Singapore',
                placeholder='Select a Country',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6"),

        html.Div([
            html.Label("Select Sector", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='sector-select8abc',
                options=[{'label': v, 'value': k} for k, v in SECTOR_LABELS.items()],
                value=SECTOR_CODES[0],
                placeholder='Select a Sector',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6")
    ], className="row mb-3"),

    html.Div([
        html.Div([
            html.Label("Trade Type", className="form-label fw-semibold mb-1 text-center w-100"),
            dbc.ButtonGroup([
                dbc.Button("Trade Volume", id='btn-total8abc', n_clicks=0, outline=False, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'}),
                dbc.Button("Exports", id='btn-export8abc', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'}),
                dbc.Button("Imports", id='btn-import8abc', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'})
            ], className='w-100')
        ], className="col-md-8"),

        html.Div([
            html.Label("Display Mode", className="form-label fw-semibold mb-1 text-center w-100"),
            daq.ToggleSwitch(
                id='toggle-display8abc',
                label='Volume / Percentage Share',
                value=True,
                size=80
            )
        ], className="col-md-4 d-flex flex-column align-items-center justify-content-center")
    ], className="row mb-4"),

    dcc.Tabs(id="module1c-tabs8abc", value="historical", className="mb-2", children=[
        dcc.Tab(label="Historical", value="historical"),
        dcc.Tab(label="Prediction", value="prediction", id="prediction-tab8abc", disabled=True)
    ]),

    dcc.Tabs(id="module1c-subtabs8abc", value="historical-bar8abc", className="mb-3"),

    html.Div(id="partner-button-container8abc"),

    html.Div(id="module1c-tab-content8abc", className="mt-3", children=[
        html.Div(id="module1c-graph-container8abc")
    ])
])

# === Partner Country Buttons ===
@app.callback(
    Output("partner-button-container8abc", "children"),
    Input("module1c-subtabs8abc", "value")
)
def render_partner_buttons(subtab):
    return html.Div([
        html.Label("Select Partner Countries", className="form-label fw-semibold mb-2"),
        html.Div([
            html.Button(
                COUNTRY_LABELS[code],
                id={"type": "partner-btn8abc", "index": code},
                n_clicks=0,
                className="btn me-2 mb-2"
            ) for code in COUNTRY_LABELS
        ], className="d-flex flex-wrap")
    ])

# @app.callback(
#     Output("selected-partners-multi8abc", "data"),
#     Output({"type": "partner-btn8abc", "index": ALL}, "style"),
#     Input({"type": "partner-btn8abc", "index": ALL}, "n_clicks"),
#     State("selected-partners-multi8abc", "data")
# )
# def toggle_selected_partners(n_clicks, selected_partners):
#     ctx = callback_context.triggered_id
#     if not ctx:
#         raise dash.exceptions.PreventUpdate
#     partner = ctx["index"]
#     if partner in selected_partners:
#         selected_partners.remove(partner)
#     else:
#         selected_partners.append(partner)
#     styles = [{"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if code in selected_partners else {} for code in COUNTRY_LABELS]
#     return selected_partners, styles

@app.callback(
    Output("selected-partners-multi8abc", "data"),
    Output({"type": "partner-btn8abc", "index": ALL}, "style"),
    Input({"type": "partner-btn8abc", "index": ALL}, "n_clicks"),
    State("selected-partners-multi8abc", "data")
)
def toggle_selected_partners(n_clicks, selected_partners):
    ctx = callback_context.triggered_id

    # Initial load: no click event, just show default selected styles
    if not ctx:
        styles = [
            {"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if code in selected_partners else {}
            for code in COUNTRY_LABELS
        ]
        return selected_partners, styles

    # User click event
    code = ctx["index"]
    if code in selected_partners:
        selected_partners.remove(code)
    else:
        selected_partners.append(code)

    styles = [
        {"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if code in selected_partners else {}
        for code in COUNTRY_LABELS
    ]
    return selected_partners, styles


# === Graph Update Callback ===
@app.callback(
    Output("module1c-graph-container8abc", "children"),
    Input("module1c-subtabs8abc", "value"),
    Input("country-select8abc", "value"),
    Input("sector-select8abc", "value"),
    Input("selected-partners-multi8abc", "data"),
    Input("trade-type-select8abc", "data"),
    Input("display-mode8abc", "data")
)
def update_graph(subtab, country, sector_code, partner_codes, trade_type, display_mode):
    if not country or not sector_code:
        return dash.no_update

    country_id = COUNTRY_NAMES[country]
    df_view_all = df_combined_all[df_combined_all['country_a'] == country_id].copy()

    if subtab.startswith("historical"):
        df_view_all = df_view_all[df_view_all["year"] <= 2023]
    elif subtab.startswith("prediction"):
        df_view_all = df_view_all[~df_view_all["year"].isin([2024, 2025])]

    df_view_all = df_view_all[df_view_all['country_b'].isin(partner_codes)]

    if subtab in ["historical-bar8abc", "prediction-bar8abc"]:
        df_view = calculate_sector_shares(df_view_all.copy(), sector_code, trade_type)
        df_view = df_view[df_view["year"] >= 2015]
        y_col = "value" if display_mode == "volume" else "percentage"
        y_title = "Trade Volume" if display_mode == "volume" else "Percentage Share"

        fig = px.bar(
            df_view, x="year", y=y_col, color=df_view["country_b"].map(COUNTRY_LABELS),
            labels={y_col: f"{SECTOR_LABELS[sector_code]}", "color": "Partner Country"},
            title=f"{SECTOR_LABELS[sector_code]} {trade_type.capitalize()} from {country} by Partner Country",
        )
        fig.update_layout(showlegend=True, yaxis_title=y_title, xaxis_title="Year", plot_bgcolor="white", paper_bgcolor="white")
        return dcc.Graph(figure=fig)

    elif subtab in ["historical-line8abc", "prediction-line8abc"]:
        lines = []
        for partner_code in partner_codes:
            temp = df_view_all[df_view_all["country_b"] == partner_code].copy()
            temp = calculate_sector_shares(temp, sector_code, trade_type)
            temp = temp.sort_values("year")
            if display_mode == "percentage":
                temp["change"] = temp["percentage"].diff()
                y_label = "% Point Change"
            else:
                temp["change"] = temp["value"].diff()
                y_label = "Change in Volume"
            temp = temp[temp["year"] >= 2015]
            temp["partner"] = COUNTRY_LABELS[partner_code]
            lines.append(temp)

        if not lines:
            return html.Div("Select at least one partner country.", className="text-muted text-center")

        df_combined = pd.concat(lines)
        fig = px.line(df_combined, x="year", y="change", color="partner", markers=True, 
                      labels={"change": y_label, "partner": "Partner Country"},
                      title=f"Year-on-Year Change in {SECTOR_LABELS[sector_code]} {trade_type.capitalize()} from {country}")
        fig.update_layout(yaxis_title=y_label, xaxis_title="Year", plot_bgcolor="white", paper_bgcolor="white")
        return dcc.Graph(figure=fig)

    return dash.no_update

# === Store & Control Callbacks ===
@app.callback(
    Output("selected-sector8abc", "data"),
    Input("sector-select8abc", "value")
)
def store_sector_dropdown(val):
    return val

@app.callback(
    Output("trade-type-select8abc", "data"),
    Output("btn-total8abc", "outline"),
    Output("btn-export8abc", "outline"),
    Output("btn-import8abc", "outline"),
    Input("btn-total8abc", "n_clicks"),
    Input("btn-export8abc", "n_clicks"),
    Input("btn-import8abc", "n_clicks"),
    prevent_initial_call=True
)
def update_trade_type(n_total, n_export, n_import):
    ctx = callback_context.triggered_id
    if ctx == 'btn-total8abc':
        return 'total', False, True, True
    elif ctx == 'btn-export8abc':
        return 'export', True, False, True
    elif ctx == 'btn-import8abc':
        return 'import', True, True, False
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("display-mode8abc", "data"),
    Input("toggle-display8abc", "value")
)
def update_display_mode(toggle_value):
    return 'percentage' if toggle_value else 'volume'

@app.callback(
    Output("prediction-tab8abc", "disabled"),
    Input("input-uploaded", "data")
)
def toggle_prediction_tab(uploaded):
    return not uploaded

@app.callback(
    Output("module1c-subtabs8abc", "children"),
    Output("module1c-subtabs8abc", "value"),
    Input("module1c-tabs8abc", "value")
)
def toggle_subtab_visibility(main_tab):
    if main_tab == "historical":
        return [
            dcc.Tab(label="Bar Chart", value="historical-bar8abc", disabled=False),
            dcc.Tab(label="Line Chart", value="historical-line8abc", disabled=False),
            dcc.Tab(label="Bar Chart", value="prediction-bar8abc", disabled=True),
            dcc.Tab(label="Line Chart", value="prediction-line8abc", disabled=True)
        ], "historical-bar8abc"
    else:
        return [
            dcc.Tab(label="Bar Chart", value="historical-bar8abc", disabled=True),
            dcc.Tab(label="Line Chart", value="historical-line8abc", disabled=True),
            dcc.Tab(label="Bar Chart", value="prediction-bar8abc", disabled=False),
            dcc.Tab(label="Line Chart", value="prediction-line8abc", disabled=False)
        ], "prediction-bar8abc"

@app.callback(
    Output("module1c-tabs8abc", "value"),
    Input("input-uploaded", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(uploaded):
    if uploaded:
        return "prediction"
    return dash.no_update

# @app.callback(
#     Output({"type": "partner-btn8abc", "index": ALL}, "style"),
#     Input("selected-partners-multi8abc", "data")
# )
# def sync_button_styles_with_store(selected_partners):
#     return [
#         {"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if code in selected_partners else {}
#         for code in COUNTRY_LABELS
#     ]

sidebar_controls = html.Div([])

