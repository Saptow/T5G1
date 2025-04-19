


import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app, ctx
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import ALL

sidebar_controls = html.Div([])

import dash_daq as daq

# === Load and Prepare Data ===
df_raw = pd.read_csv("data/final/historical_data.csv")

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

app = get_app()

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

layout = html.Div([
    dcc.Store(id="selected-sectors-multi7abc", data=SECTOR_CODES[:2]),
    # Stores and Controls
    dcc.Store(id="selected-sector7abc", data=SECTOR_CODES[0]),
    dcc.Store(id="trade-type-select7abc", data='total'),
    dcc.Store(id="display-mode7abc", data='volume'),
    dcc.Store(id='processed-forecast-data7abc', storage_type='memory'),

    html.H1("Sector Share Trend", className="mb-4 text-center"),
    html.Div(
        html.H6(
            """
            Track how trade in a specific sector between an economy and its trading partner has evolved over time. 
            Select the sector, trade direction, and visualisation type to explore trends in trade value or percentage share. 
            Use this tool to uncover long-term patterns and understand how sectoral trade relationships have shifted over the years.

            """,
            style={
                'color': '#333333',
                'fontSize': '16px',
                'fontFamily': 'Lato, sans-serif',
                'lineHeight': '1.4', 
                'marginBottom': '24px'
            }
        )
    ),
    html.Div([
        html.Div([
            html.Label("Select Economy:", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select7abc',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value='Singapore',
                placeholder='Select an Economy',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6"),

        html.Div([
            html.Label("Select Trading Partner:", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select-alt27abc',
                value='Australia',
                style={"color": "black", "backgroundColor": "white", "width": "100%"},
                placeholder="Select a Trading Partner",
                searchable=True,
                className="mb-3")
        ], className="col-md-6")
    ], className="row mb-3"),
    html.Div([
        html.Div([
            html.Label("Select Direction of Trade:", className="form-label fw-semibold mb-1 text-center w-100"),
            dbc.ButtonGroup([
                dbc.Button("Total Trade", id='btn-total7abc', n_clicks=0, outline=False, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'}),
                dbc.Button("Exports", id='btn-export7abc', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'}),
                dbc.Button("Imports", id='btn-import7abc', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'})
            ], className='w-100')
        ], className="col-md-8"),

        html.Div([
            html.Label("Select Visualisation Type", className="form-label fw-semibold mb-1 text-center w-100"),
            daq.ToggleSwitch(
                id='toggle-display7abc',
                label='Trade Value / Percentage Share',
                value=True,
                size=80
            )
        ], className="col-md-4 d-flex flex-column align-items-center justify-content-center")
    ], className="row mb-4"),
  
    dcc.Tabs(id="module1c-tabs7abc", value="historical", className="mb-2", children=[
        dcc.Tab(label="Historical", value="historical"),
        dcc.Tab(label="Prediction", value="prediction", id="prediction-tab7abc", disabled=True)
    ]),
    

    dcc.Tabs(id="module1c-subtabs7abc", value="historical-bar7abc", className="mb-3"),
    
    html.Div(id="sector-button-container7abc"),

    html.Div(id="module1c-tab-content7abc", className="mt-3", children=[
        html.Div(id="module1c-graph-container7abc")
    ])
  ])
# Add callback to process the forecast data when it becomes available
@app.callback(
    Output("processed-forecast-data7abc", "data"),
    Input("forecast-data", "data"),
    prevent_initial_call=True
)
def process_forecast_data(forecast_data):
    if not forecast_data:
        return dash.no_update
        
    # Convert the forecast data to DataFrame
    prediction_df = pd.DataFrame(forecast_data)
    
    # Filter postshock scenario if available
    if "scenario" in prediction_df.columns:
        prediction_df = prediction_df[prediction_df["scenario"] == "postshock"].drop(columns=["scenario"])
    
    # Ensure year is numeric
    prediction_df['year'] = pd.to_numeric(prediction_df['year'], errors='coerce')
    
    # Merge with historical data
    df_combined_all = pd.concat([df_raw, prediction_df], ignore_index=True)
    
    # Return the processed data
    return df_combined_all.to_dict('records')

@app.callback(
    Output("module1c-graph-container7abc", "children"),
    Input("module1c-subtabs7abc", "value"),
    Input("country-select7abc", "value"),
    Input("country-select-alt27abc", "value"),
    Input("selected-sector7abc", "data"),
    Input("selected-sectors-multi7abc", "data"),
    Input("trade-type-select7abc", "data"),
    Input("display-mode7abc", "data"),
    Input("processed-forecast-data7abc", "data") 
)
def update_graph(subtab, country, partner, single_sector, multi_sectors, trade_type, display_mode, processed_forecast_data):
    if not country or not partner:
        return dash.no_update

    country_id = COUNTRY_NAMES[country]
    partner_id = COUNTRY_NAMES[partner]

    # Use the processed forecast data when available
    df_combined_all = pd.DataFrame(processed_forecast_data) if processed_forecast_data else df_raw.copy()

    if subtab.startswith("historical"):
        df_view_all = df_raw[
            (df_raw['country_a'] == country_id) & (df_raw['country_b'] == partner_id)
        ].copy()
    else:
        df_view_all = df_combined_all[
            (df_combined_all['country_a'] == country_id) & (df_combined_all['country_b'] == partner_id)
        ].copy()

    latest_year = df_view_all['year'].max()
    prev_year = df_view_all[df_view_all['year'] < latest_year]['year'].max()

    df_view = df_view_all.copy()

    if subtab.startswith("prediction"):
        df_view = df_view[~df_view["year"].isin([2024, 2025])]
    elif subtab.startswith("historical"):
        df_view = df_view[df_view["year"] <= 2023]

    if subtab in ["historical-bar7abc", "prediction-bar7abc"]:
        df_view = calculate_sector_shares(df_view, single_sector, trade_type)
        df_view = df_view[df_view["year"] >= 2015]
        if subtab.startswith("prediction"):
            df_view = df_view[~df_view["year"].isin([2024, 2025])]
        y_col = "value" if display_mode == "volume" else "percentage"
        y_title = "Trade Volume" if display_mode == "volume" else "Percentage Share"

        fig = px.bar(
            df_view, x="year", y=y_col,
            text=df_view[y_col].apply(lambda x: f"{x:,.2f}" if display_mode == "percentage" else f"{x:,.0f}"),
            hover_data={"percentage": ':.2f'},
            labels={y_col: f"{SECTOR_LABELS[single_sector]}"},
            title=f"{SECTOR_LABELS[single_sector]} {trade_type.capitalize()} from {country} to {partner} ({df_view['year'].min()}–{df_view['year'].max()})",
            color=df_view['year'].apply(lambda y: '#fdae61' if subtab.startswith("prediction") and y == latest_year else '#2c7bb6')
        )
        fig.update_traces(textposition="outside")
        if subtab.startswith("prediction"):
            fig.update_traces(
                line=dict(dash="dot", color="#fdae61"),
                selector=dict(mode="lines+markers")
            )

        fig.update_layout(
            showlegend=False,
            yaxis_title=y_title, xaxis_title="Year",
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=30, l=10, r=10, b=10)
        )
        return dcc.Graph(figure=fig)

    elif subtab in ["historical-line7abc", "prediction-line7abc"]:
        lines = []
        for code in multi_sectors:
            temp = calculate_sector_shares(df_view.copy(), code, trade_type)
            temp = temp.sort_values("year")
            if display_mode == "percentage":
                temp["change"] = temp["percentage"].diff()
                y_label = "% Point Change in Sector Share"
            else:
                temp["change"] = temp["value"].diff()
                y_label = "Change in Sector Volume"
            temp = temp[temp["year"] >= 2015].copy()
            temp["sector"] = SECTOR_LABELS[code]
            lines.append(temp)

        if not lines:
            return html.Div("Select at least one sector to display the line graph.", className="text-muted text-center")

        df_combined = pd.concat(lines)
        fig = px.line(
        df_combined,
        x="year",
            y="change",
            color="sector",
            markers=True,
            labels={"change": y_label},
            title=f"Year-on-Year Change by Sector ({trade_type.capitalize()}) from {country} to {partner}"
        )
        fig.update_layout(
            yaxis_title=y_label,
            xaxis_title="Year",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(t=30, l=10, r=10, b=10)
        )
        fig.update_traces(marker=dict(size=12),
                  selector=dict(mode='markers'))
        if subtab == "prediction-line7abc":
            for sector in df_combined["sector"].unique():
                df_sector = df_combined[df_combined["sector"] == sector].sort_values("year")
                if 2023 in df_sector["year"].values and 2026 in df_sector["year"].values:
                    fig.add_scatter(
                        x=[2023, 2026],
                        y=df_sector[df_sector["year"].isin([2023, 2026])]["change"],
                        mode="lines",
                        line=dict(dash="dot", color="#fdae61"),
                        showlegend=False,
                        name=f"{sector} Projection"
            )

        return dcc.Graph(figure=fig)

    return dash.no_update


from dash.exceptions import PreventUpdate

@app.callback(
    Output("sector-button-container7abc", "children"),
    Input("module1c-subtabs7abc", "value")
)
def render_sector_buttons(subtab):
    if subtab in ["historical-bar7abc", "prediction-bar7abc"]:
        return html.Div([
            html.Label("Select Sector", className="form-label fw-semibold mb-2"),
            html.Div([
                html.Button(
                    SECTOR_LABELS[code],
                    id={"type": "sector-btn_module1c", "index": code},
                    n_clicks_timestamp=0,
                    className="btn me-2 mb-2",
                    style={"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if code == SECTOR_CODES[0] else {}
                ) for code in SECTOR_CODES
            ], className="d-flex flex-wrap")
        ])
    elif subtab in ["historical-line7abc", "prediction-line7abc"]:
        return html.Div([
            html.Label("Select Sectors", className="form-label fw-semibold mb-2"),
            html.Div([
                html.Button(
                    SECTOR_LABELS[code],
                    id={"type": "sector-btn-multi_module1c", "index": code},
                    n_clicks=0,
                    className="btn me-2 mb-2"
                ) for code in SECTOR_CODES
            ], className="d-flex flex-wrap")
        ])

    

    return dash.no_update

@app.callback(
    Output("country-select-alt27abc", "options"),
    Input("country-select7abc", "value")
)
def update_partner_dropdown(selected_country):
    if not selected_country:
        return []
    country_id = COUNTRY_NAMES[selected_country]
    filtered = df_raw[df_raw['country_a'] == country_id]
    partner_ids = filtered['country_b'].dropna().unique()
    partner_names = [COUNTRY_LABELS.get(p) for p in partner_ids if p in COUNTRY_LABELS and p != country_id]
    return [{'label': name, 'value': name} for name in sorted(partner_names)]

@app.callback(
    Output("selected-sector7abc", "data"),
    Output({"type": "sector-btn_module1c", "index": ALL}, "style"),
    Input({"type": "sector-btn_module1c", "index": ALL}, "n_clicks_timestamp"),
    State("module1c-subtabs7abc", "value")
)
def update_selected_sector(n_clicks, subtab):
    if subtab not in ["historical-bar7abc", "prediction-bar7abc"]:
        raise dash.exceptions.PreventUpdate

    if not any(n_clicks):
        styles = [{"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if i == 0 else {} for i in range(len(n_clicks))]
        return SECTOR_CODES[0], styles

    selected_idx = n_clicks.index(max(n_clicks))
    styles = [{"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if i == selected_idx else {} for i in range(len(n_clicks))]
    return SECTOR_CODES[selected_idx], styles


# @app.callback(
#     Output("selected-sector7abc", "data"),
#     Output({"type": "sector-btn_module1c", "index": ALL}, "style"),
#     Input({"type": "sector-btn_module1c", "index": ALL}, "n_clicks_timestamp"),
#     State("module1c-subtabs7abc", "value")
# )
# def update_selected_sector(n_clicks, subtab):
#     if subtab not in ["historical-bar7abc", "prediction-bar7abc"]:
#         return dash.no_update, [{} for _ in SECTOR_CODES]
#     if not any(n_clicks):
#         styles = [{"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if i == 0 else {} for i in range(len(SECTOR_CODES))]
#         return SECTOR_CODES[0], styles
#     selected_idx = n_clicks.index(max(n_clicks))
#     styles = [{"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if i == selected_idx else {} for i in range(len(SECTOR_CODES))]
#     return SECTOR_CODES[selected_idx], styles

# @app.callback(
#     Output("selected-sectors-multi7abc", "data"),
#     Output({"type": "sector-btn-multi_module1c", "index": ALL}, "style"),
#     Input({"type": "sector-btn-multi_module1c", "index": ALL}, "n_clicks"),
#     State("selected-sectors-multi7abc", "data")
# )
# def toggle_multi_sector(n_clicks_list, selected_sectors):
#     ctx = callback_context.triggered_id
#     if not ctx:
#         raise PreventUpdate

#     code = ctx["index"]
#     if code in selected_sectors:
#         selected_sectors.remove(code)
#     else:
#         selected_sectors.append(code)

#     styles = [
#         {"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if code in selected_sectors else {}
#         for code in SECTOR_CODES
#     ]
#     return selected_sectors, styles

@app.callback(
    Output("selected-sectors-multi7abc", "data"),
    Output({"type": "sector-btn-multi_module1c", "index": ALL}, "style"),
    Input({"type": "sector-btn-multi_module1c", "index": ALL}, "n_clicks"),
    State("selected-sectors-multi7abc", "data")
)
def toggle_multi_sector(n_clicks_list, selected_sectors):
    triggered = callback_context.triggered_id
    if not triggered:
        raise dash.exceptions.PreventUpdate

    index_clicked = triggered["index"]
    if index_clicked in selected_sectors:
        selected_sectors.remove(index_clicked)
    else:
        selected_sectors.append(index_clicked)

    # Use SECTOR_CODES to ensure correct ordering and length
    styles = [
        {"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if code in selected_sectors else {}
        for code in SECTOR_CODES
    ]
    return selected_sectors, styles


@app.callback(
    Output("trade-type-select7abc", "data"),
    Output("btn-total7abc", "outline"),
    Output("btn-export7abc", "outline"),
    Output("btn-import7abc", "outline"),
    Input("btn-total7abc", "n_clicks"),
    Input("btn-export7abc", "n_clicks"),
    Input("btn-import7abc", "n_clicks"),
    prevent_initial_call=True
)
def update_trade_type(n_total, n_export, n_import):
    ctx = callback_context.triggered_id
    if ctx == 'btn-total7abc':
        return 'total', False, True, True
    elif ctx == 'btn-export7abc':
        return 'export', True, False, True
    elif ctx == 'btn-import7abc':
        return 'import', True, True, False
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("display-mode7abc", "data"),
    Input("toggle-display7abc", "value")
)
def update_display_mode(toggle_value):
    return 'percentage' if toggle_value else 'volume'

# Update the prediction tab enablement callback
@app.callback(
    Output("prediction-tab7abc", "disabled"),
    Input("forecast-data", "data")
)
def toggle_prediction_tab(forecast_data):
    return not forecast_data

@app.callback(
    Output("module1c-subtabs7abc", "children"),
    Output("module1c-subtabs7abc", "value"),
    Input("module1c-tabs7abc", "value")
)
def toggle_subtab_visibility(main_tab):
    if main_tab == "historical":
        return [
            dcc.Tab(label="Bar Chart", value="historical-bar7abc", disabled=False),
            dcc.Tab(label="Line Chart", value="historical-line7abc", disabled=False),
            dcc.Tab(label="Bar Chart", value="prediction-bar7abc", disabled=True),
            dcc.Tab(label="Line Chart", value="prediction-line7abc", disabled=True)
        ], "historical-bar7abc"
    else:
        return [
            dcc.Tab(label="Bar Chart", value="historical-bar7abc", disabled=True),
            dcc.Tab(label="Line Chart", value="historical-line7abc", disabled=True),
            dcc.Tab(label="Bar Chart", value="prediction-bar7abc", disabled=False),
            dcc.Tab(label="Line Chart", value="prediction-line7abc", disabled=False)
        ], "prediction-bar7abc"

# Update the tab switching callback
@app.callback(
    Output("module1c-tabs7abc", "value"),
    Input("forecast-data", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(forecast_data):
    if forecast_data:
        return "prediction"
    return dash.no_update









