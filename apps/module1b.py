# from dash import html, dcc, Input, Output, State, ctx, callback
# import pandas as pd
# import plotly.graph_objects as go
# import dash
# import dash_bootstrap_components as dbc
# from dash.dependencies import ALL

# # === Data Loading ===
# df_raw = pd.read_csv("historical_data.csv")
# df_new = pd.read_csv("sample_2026.csv")

# # Split into historical (2015–2024) and prediction (2026 only)
# historical_df = df_raw[df_raw["year"].between(2015, 2023)].copy()


# prediction_df = df_new[df_new["scenario"] == 'postshock'].copy()
# prediction_df = prediction_df.drop(columns=['scenario'], inplace=True)


# # === Sector mapping ===
# SECTOR_LABELS = {
#     "bec_1": "Food and Agriculture",
#     "bec_2": "Energy and Mining",
#     "bec_3": "Construction and Housing",
#     "bec_4": "Textile and Footwear",
#     "bec_5": "Transport and Travel",
#     "bec_6": "ICT and Business",
#     "bec_7": "Health and Education",
#     "bec_8": "Government and Others"
# }
# SECTOR_CODES = list(SECTOR_LABELS.keys())

# # === Country List ===
# COUNTRY_LIST = sorted(set(df_raw["country_a"].unique()))



# @callback(
#     Output("partner-dropdown_module1c", "options"),
#     Output("partner-dropdown_module1c", "value"),
#     Input("country-dropdown_module1c", "value")
# )
# def update_partner_options_1c(selected_country):
#     options = [{"label": c, "value": c} for c in COUNTRY_LIST if c != selected_country]
#     value = options[0]["value"] if options else None
#     return options, value

# # === Layout ===
# layout = html.Div([
#     #dcc.Store(id="input-uploaded"),
#     dcc.Store(id="selected-sector_module1c", data="bec_1"),
#     dcc.Store(id="trade-type_module1c", data="total"),

#     html.H2("Module 1B: Yearly percentage share of sectors", className="mb-4"),

#     html.Div([
#         html.Div([
#             html.Label("Select a Country", className="form-label fw-semibold mb-1"),
#             dcc.Dropdown(
#                 id="country-dropdown_module1c",
#                 options=[{"label": c, "value": c} for c in COUNTRY_LIST],
#                 value=COUNTRY_LIST[0],
#                 className="mb-3"
#             )
#         ], className="col-md-6"),

#         html.Div([
#             html.Label("Select a Partner", className="form-label fw-semibold mb-1"),
#             dcc.Dropdown(id="partner-dropdown_module1c",
#                     className="mb-3")
#         ], className="col-md-6")
#     ], className="row mb-3"),

#     html.Div([
#         html.Label("Select Trade Type", className="form-label fw-semibold mb-2"),
#         dbc.ButtonGroup([
#             dbc.Button("Trade Volume", id="btn-total_module1c", n_clicks=0, color="primary", outline=True, size="sm"),
#             dbc.Button("Exports", id="btn-export_module1c", n_clicks=0, outline=True, size="sm"),
#             dbc.Button("Imports", id="btn-import_module1c", n_clicks=0, outline=True, size="sm")
#         ], className="mb-4")
#     ]),

#     html.Div([
#         html.Label("Select Sector", className="form-label fw-semibold mb-2"),
#         html.Div([
#             html.Button(
#                 SECTOR_LABELS[code],
#                 id={"type": "sector-btn_module1c", "index": code},
#                 n_clicks=0,
#                 className="btn me-2 mb-2"
#             ) for code in SECTOR_CODES
#         ], className="d-flex flex-wrap")
#     ]),

#     dcc.Tabs(id="module1c-tabs_module1c", value="historical", children=[
#         dcc.Tab(label="Historical", value="historical"),
#         dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1c_module1c", disabled=True)
#     ]),

#     #html.Div(id="module1c-tab-content_module1c")
#     html.Div([
#     dcc.Tabs(id="subtabs_module1c", value="percent-tab", children=[
#         dcc.Tab(label="Sector Percentage Share", value="percent-tab"),
#         dcc.Tab(label="Year-on-Year Changes", value="change-tab")
#     ], className="mb-3"),
    
#     html.Div([
#         html.Div(id='country-title1c', style={'display': 'none'}),
#         dcc.Graph(id='sector-line1c', style={'display': 'none'}),
#         dcc.Graph(id='sector-bar1c', style={'display': 'none'})
#     ], style={'display': 'none'}),
#     # html.Div([
#     #     html.H5(id='country-title1c', className="text-center mb-3"),
#     #     dcc.Graph(id='sector-bar1c', config={'displayModeBar': False}),
#     #     dcc.Graph(id='sector-line1c', config={'displayModeBar': False})
#     # ]),


#     html.Div(id="subtab-content_module1c")  # This was missing!
# ])

# ])

# # === Callbacks ===

# @callback(
#     Output("prediction-tab1c_module1c", "disabled"),
#     Input("input-uploaded", "data")
# )
# def toggle_prediction_tab(uploaded):
#     return not uploaded

# @callback(
#     Output("module1c-tabs_module1c", "value"),
#     Input("input-uploaded", "data"),
#     prevent_initial_call=True
# )
# def switch_to_prediction_tab(uploaded):
#     return "prediction" if uploaded else dash.no_update

# @callback(
#     Output("selected-sector_module1c", "data"),
#     Input({"type": "sector-btn_module1c", "index": ALL}, "n_clicks"),
#     prevent_initial_call=True
# )
# def select_sector(n_clicks):
#     triggered = ctx.triggered_id
#     if isinstance(triggered, dict):
#         return triggered["index"]
#     return dash.no_update

# @callback(
#     Output({"type": "sector-btn_module1c", "index": ALL}, "className"),
#     Input("selected-sector_module1c", "data"),
#     [State({"type": "sector-btn_module1c", "index": ALL}, "id")]
# )
# def style_sector_buttons(selected, all_ids):
#     return [
#         "btn btn-primary me-2 mb-2" if b["index"] == selected else "btn btn-outline-primary me-2 mb-2"
#         for b in all_ids
#     ]

# @callback(
#     Output("trade-type_module1c", "data"),
#     Output("btn-total_module1c", "color"),
#     Output("btn-export_module1c", "color"),
#     Output("btn-import_module1c", "color"),
#     Input("btn-total_module1c", "n_clicks"),
#     Input("btn-export_module1c", "n_clicks"),
#     Input("btn-import_module1c", "n_clicks"),
#     prevent_initial_call=True
# )
# def update_trade_type_1c(n_total, n_export, n_import):
#     ctx_id = ctx.triggered_id
#     if ctx_id == "btn-total_module1c":
#         return "total", "primary", "secondary", "secondary"
#     elif ctx_id == "btn-export_module1c":
#         return "export", "secondary", "primary", "secondary"
#     elif ctx_id == "btn-import_module1c":
#         return "import", "secondary", "secondary", "primary"
#     return dash.no_update, dash.no_update, dash.no_update, dash.no_update








# # @callback(
# #     Output("subtab-content_module1c", "children"),
# #     Input("country-dropdown_module1c", "value"),
# #     Input("partner-dropdown_module1c", "value"),
# #     Input("selected-sector_module1c", "data"),
# #     Input("trade-type_module1c", "data"),
# #     Input("module1c-tabs_module1c", "value"),
# #     Input("subtabs_module1c", "value")
# # )
# # def update_graph(selected_country, selected_partner, selected_sector, trade_type, active_tab, subtab):
# #     # Only handle historical for now
# #     if active_tab != "historical":
# #         return html.Div("Prediction graph logic coming next!")

# #     df_view = historical_df
# #     filtered = df_view[df_view["country_a"] == selected_country].copy()
# #     if selected_partner:
# #         filtered = filtered[filtered["country_b"] == selected_partner]

# #     if filtered.empty:
# #         return html.Div("No data for selection", className="text-center text-muted")

# #     included_years = list(range(2015, 2024))
# #     filtered = filtered[filtered["year"].isin(included_years)]

# #     def get_sector_cols(trade_type):
# #         if trade_type == "export":
# #             return [f"{selected_sector}_export_A_to_B"]
# #         elif trade_type == "import":
# #             return [f"{selected_sector}_import_A_from_B"]
# #         else:
# #             return [f"{selected_sector}_export_A_to_B", f"{selected_sector}_import_A_from_B"]

# #     cols = get_sector_cols(trade_type)

# #     grouped = filtered.groupby("year", as_index=False)[cols].sum()
# #     grouped["Total"] = grouped[cols].sum(axis=1)

# #     total_all = grouped["Total"].sum()
# #     grouped["percentage"] = 100 * grouped["Total"] / total_all if total_all else 0
# #     grouped["change"] = grouped["percentage"].diff().fillna(0).round(1)

# #     title = f"{SECTOR_LABELS[selected_sector]} - {trade_type.capitalize()} ({selected_country} → {selected_partner or 'All'})"

# #     if subtab == "percent-tab":
# #         bar_fig = go.Figure()
# #         bar_fig.add_trace(go.Bar(
# #             x=grouped["year"],
# #             y=grouped["percentage"],
# #             marker_color='#00BFC4',
# #             text=grouped["percentage"].round(1).astype(str) + '%',
# #             textposition='auto'
# #         ))
# #         bar_fig.update_layout(
# #             title=title,
# #             yaxis_title="Percentage Share",
# #             xaxis=dict(tickmode='linear'),
# #             plot_bgcolor='white',
# #             paper_bgcolor='white'
# #         )
# #         return dcc.Graph(figure=bar_fig)

# #     elif subtab == "change-tab":
# #         line_fig = go.Figure()
# #         line_fig.add_trace(go.Scatter(
# #             x=grouped["year"],
# #             y=grouped["change"],
# #             mode='lines+markers',
# #             line=dict(color='#636EFA'),
# #             marker=dict(size=10),
# #             text=grouped["change"].astype(str) + '%',
# #             hovertemplate='%{x}: %{y:+.1f}%',
# #             showlegend=False
# #         ))
# #         line_fig.update_layout(
# #             title=title + " (YoY Change)",
# #             yaxis_title="% Change from Previous Year",
# #             xaxis=dict(tickmode='linear'),
# #             plot_bgcolor='white',
# #             paper_bgcolor='white'
# #         )
# #         return dcc.Graph(figure=line_fig)

# #     return html.Div("Unknown sub-tab")

# # @callback(
# #     Output("module1c-tab-content_module1c", "children"),
# #     Input("module1c-tabs_module1c", "value")
# # )
# # def render_main_tab(tab):
# #     if tab == "historical":
# #         return html.Div([
# #             dcc.Tabs(id="subtabs_module1c", value="percent-tab", children=[
# #                 dcc.Tab(label="Sector Percentage Share", value="percent-tab"),
# #                 dcc.Tab(label="Year-on-Year Changes", value="change-tab")
# #             ], className="mb-3"),
# #             html.Div(id="subtab-content_module1c")
# #         ])
# #     elif tab == "prediction":
# #         return html.Div("Prediction graph logic coming next!")


# @callback(
#     Output("module1c-tab-content_module1c", "children"),
#     Input("module1c-tabs_module1c", "value")
# )
# def render_main_tab_1c(tab):
#     if tab == "historical":
#         return html.Div([
#             html.Div(style={'marginTop': '20px'}),
#             html.H5(id='country-title1c', className="text-center mb-2"),
#             dcc.Graph(id='sector-bar1c', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
#             dcc.Graph(id='sector-line1c', config={'displayModeBar': False}, style={"backgroundColor": "white"})
#         ])
#     elif tab == "prediction":
#         return html.Div("Prediction graph logic coming next!")


# sidebar_controls = html.Div([])

# @callback(
#     Output('sector-bar1c', 'figure'),
#     Output('sector-line1c', 'figure'),
#     Output('country-title1c', 'children'),
#     Input('country-dropdown_module1c', 'value'),
#     Input('partner-dropdown_module1c', 'value'),
#     Input('selected-sector_module1c', 'data'),
#     Input('trade-type_module1c', 'data'),
#     Input('module1c-tabs_module1c', 'value'),
# )
# def update_sector_graphs(selected_country, selected_partner, selected_sector, trade_type, active_tab):
#     # Pick historical or prediction
#     df_view = historical_df if active_tab == "historical" else prediction_df

#     # Filter
#     df_filtered = df_view[df_view['country_a'] == selected_country].copy()
#     if selected_partner:
#         df_filtered = df_filtered[df_filtered['country_b'] == selected_partner]

#     if df_filtered.empty:
#         return go.Figure(), go.Figure(), f"No data for selection"

#     # Get years
#     latest_year = df_filtered['year'].max()
#     prev_year = df_filtered['year'][df_filtered['year'] < latest_year].max()

#     # Aggregate
#     def get_cols(trade_type):
#         if trade_type == 'export':
#             return [f"{selected_sector}_export_A_to_B"]
#         elif trade_type == 'import':
#             return [f"{selected_sector}_import_A_from_B"]
#         else:
#             return [f"{selected_sector}_export_A_to_B", f"{selected_sector}_import_A_from_B"]

#     cols = get_cols(trade_type)

#     yearly = df_filtered.groupby('year', as_index=False)[cols].sum()
#     yearly['Total'] = yearly[cols].sum(axis=1)

#     # Bar chart: show share
#     total_all = yearly['Total'].sum()
#     yearly['percentage'] = 100 * yearly['Total'] / total_all if total_all else 0
#     yearly['percentage'] = yearly['percentage'].round(1)
#     yearly['change'] = yearly['percentage'].diff().round(1)

#     # Build bar graph
#     bar_fig = go.Figure()
#     bar_fig.add_trace(go.Bar(
#         x=yearly['year'], y=yearly['percentage'],
#         text=yearly['percentage'].astype(str) + '%',
#         textposition='auto',
#         marker_color='#00BFC4'
#     ))
#     bar_fig.update_layout(
#         title=f"{SECTOR_LABELS[selected_sector]} - {trade_type.capitalize()} Share",
#         yaxis_title="Percentage Share", xaxis=dict(tickmode='linear'),
#         plot_bgcolor='white', paper_bgcolor='white'
#     )

#     # Line chart: year-on-year change
#     line_fig = go.Figure()
#     line_fig.add_trace(go.Scatter(
#         x=yearly['year'],
#         y=yearly['change'],
#         mode='lines+markers',
#         text=yearly['change'].astype(str) + '%',
#         hovertemplate='%{x}: %{y:+.1f}%',
#         line=dict(color='#636EFA')
#     ))
#     line_fig.update_layout(
#         title=f"{SECTOR_LABELS[selected_sector]} - YoY Change",
#         yaxis_title="% Change from Previous Year",
#         xaxis=dict(tickmode='linear'),
#         plot_bgcolor='white', paper_bgcolor='white'
#     )

#     # Title
#     title = f"{selected_country}'s {SECTOR_LABELS[selected_sector]} {trade_type.capitalize()}"

#     return bar_fig, line_fig, title







import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import ALL

sidebar_controls = html.Div([])

# # comment in 

# import pandas as pd
# import plotly.express as px
# from dash import dcc, html, Input, Output, State, callback_context, get_app
# import dash
# import dash_bootstrap_components as dbc
# from dash.dependencies import ALL
# import dash_daq as daq

# # === Load and Prepare Data ===
# df_raw = pd.read_csv("data/final/historical_data.csv")
# df_raw['year'] = pd.to_numeric(df_raw['year'], errors='coerce')

# SECTOR_LABELS = {
#     "bec_1": "Food and Agriculture",
#     "bec_2": "Energy and Mining",
#     "bec_3": "Construction and Housing",
#     "bec_4": "Textile and Footwear",
#     "bec_5": "Transport and Travel",
#     "bec_6": "ICT and Business",
#     "bec_7": "Health and Education",
#     "bec_8": "Government and Others"
# }
# SECTOR_CODES = list(SECTOR_LABELS.keys())

# COUNTRY_LABELS = {
#     "ARE": "United Arab Emirates",
#     "AUS": "Australia",
#     "CHE": "Switzerland",
#     "CHN": "China",
#     "DEU": "Germany",
#     "FRA": "France",
#     "HKG": "Hong Kong",
#     "IDN": "Indonesia",
#     "IND": "India",
#     "JPN": "Japan",
#     "KOR": "South Korea",
#     "MYS": "Malaysia",
#     "NLD": "Netherlands",
#     "PHL": "Philippines",
#     "SGP": "Singapore",
#     "THA": "Thailand",
#     "USA": "United States",
#     "VNM": "Vietnam"
# }
# COUNTRY_NAMES = {v: k for k, v in COUNTRY_LABELS.items()}
# COUNTRY_LIST = sorted(COUNTRY_LABELS.values())

# app = get_app()

# def calculate_volume(df_view, sector_code, trade_type):
#     if trade_type == "export":
#         col = f"{sector_code}_export_A_to_B"
#         df_view["value"] = df_view[col]
#     elif trade_type == "import":
#         col = f"{sector_code}_import_A_from_B"
#         df_view["value"] = df_view[col]
#     else:
#         exp_col = f"{sector_code}_export_A_to_B"
#         imp_col = f"{sector_code}_import_A_from_B"
#         df_view["value"] = df_view[exp_col] + df_view[imp_col]
#     return df_view

# def calculate_percentage(df_view, trade_type):
#     if trade_type == "export":
#         trade_cols = [f"{code}_export_A_to_B" for code in SECTOR_CODES]
#     elif trade_type == "import":
#         trade_cols = [f"{code}_import_A_from_B" for code in SECTOR_CODES]
#     else:
#         trade_cols = [f"{code}_export_A_to_B" for code in SECTOR_CODES] + \
#                       [f"{code}_import_A_from_B" for code in SECTOR_CODES]

#     df_view["total"] = df_view[trade_cols].sum(axis=1)
#     df_view["percentage"] = 100 * df_view["value"] / df_view["total"].replace(0, 1)
#     return df_view

# def calculate_sector_shares(df_view, sector_code, trade_type):
#     df_view = calculate_volume(df_view, sector_code, trade_type)
#     df_view = calculate_percentage(df_view, trade_type)
#     return df_view

# layout = html.Div([
#     dcc.Store(id="selected-sectors-multi7abc", data=SECTOR_CODES[:2]),
#     # Stores and Controls
#     dcc.Store(id="selected-sector7abc", data=SECTOR_CODES[0]),
#     dcc.Store(id="trade-type-select7abc", data='total'),
#     dcc.Store(id="display-mode7abc", data='volume'),

#     html.H2("Sector Trade Trends Over Time", className="text-center mb-4"),

#     html.Div([
#         html.Div([
#             html.Label("Select a Country", className="form-label fw-semibold mb-1"),
#             dcc.Dropdown(
#                 id='country-select7abc',
#                 options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
#                 value='Singapore',
#                 placeholder='Select a Country',
#                 className="mb-3",
#                 style={"width": "100%"}
#             )
#         ], className="col-md-6"),

#         html.Div([
#             html.Label("Partner Country", className="form-label fw-semibold mb-1"),
#             dcc.Dropdown(
#                 id='country-select-alt27abc',
#                 value='Australia',
#                 style={"color": "black", "backgroundColor": "white", "width": "100%"},
#                 placeholder="Select partner country",
#                 searchable=True,
#                 className="mb-3")
#         ], className="col-md-6")
#     ], className="row mb-3"),


#     html.Div([
#         html.Label("Trade Type", className="form-label fw-semibold mb-1 text-center w-100"),
#         dbc.ButtonGroup([
#             dbc.Button("Trade Volume", id='btn-total7abc', n_clicks=0, outline=False, size='sm', color='primary'),
#             dbc.Button("Exports", id='btn-export7abc', n_clicks=0, outline=True, size='sm', color='primary'),
#             dbc.Button("Imports", id='btn-import7abc', n_clicks=0, outline=True, size='sm', color='primary')
#         ], className='w-100')
#     ], className="mb-4"),

#     html.Div([
#         html.Label("Display Mode", className="form-label fw-semibold mb-2"),
#         daq.ToggleSwitch(
#             id='toggle-display7abc',
#             label='Volume / Percentage Share',
#             value=True,
#             className="mb-2",
#             size=60
#         )
#     ], className="mb-4 d-flex flex-column align-items-center"),
  
#     dcc.Tabs(id="module1c-tabs7abc", value="historical", className="mb-2", children=[
#         dcc.Tab(label="Historical", value="historical"),
#         dcc.Tab(label="Prediction", value="prediction")
#     ]),

#     dcc.Tabs(id="module1c-subtabs7abc", value="historical-bar7abc", className="mb-3"),
    
#     html.Div(id="sector-button-container7abc"),

#     html.Div(id="module1c-tab-content7abc", className="mt-3", children=[
#         html.Div(id="module1c-graph-container7abc")
#     ])
#   ])

# @app.callback(
#     Output("module1c-graph-container7abc", "children"),
#     Input("module1c-subtabs7abc", "value"),
#     Input("country-select7abc", "value"),
#     Input("country-select-alt27abc", "value"),
#     Input("selected-sector7abc", "data"),
#     Input("selected-sectors-multi7abc", "data"),
#     Input("trade-type-select7abc", "data"),
#     Input("display-mode7abc", "data")
# )
# def update_graph(subtab, country, partner, single_sector, multi_sectors, trade_type, display_mode):
#     if not country or not partner:
#         return dash.no_update

#     country_id = COUNTRY_NAMES[country]
#     partner_id = COUNTRY_NAMES[partner]

#     df_view = df_raw[
#         (df_raw['country_a'] == country_id) & (df_raw['country_b'] == partner_id) &
#         (df_raw['year'] >= 2014) & (df_raw['year'] <= 2023)
#     ].copy()

#     if subtab == "historical-bar7abc":
#         df_view = calculate_sector_shares(df_view, single_sector, trade_type)
#         df_view = df_view[df_view["year"] >= 2015]
#         y_col = "value" if display_mode == "volume" else "percentage"
#         y_title = "Trade Volume" if display_mode == "volume" else "Percentage Share"

#         fig = px.bar(
#             df_view, x="year", y=y_col,
#             text=df_view[y_col].apply(lambda x: f"{x:,.2f}" if display_mode == "percentage" else f"{x:,.0f}"),
#             hover_data={"percentage": ':.2f'},
#             labels={y_col: f"{SECTOR_LABELS[single_sector]}"},
#             title=f"{SECTOR_LABELS[single_sector]} {trade_type.capitalize()} from {country} to {partner} (2015–2023)",
#             color_discrete_sequence=["#2c7bb6"]
#         )
#         fig.update_traces(textposition="outside")
#         fig.update_layout(
#             yaxis_title=y_title, xaxis_title="Year",
#             plot_bgcolor="white", paper_bgcolor="white",
#             margin=dict(t=30, l=10, r=10, b=10)
#         )
#         return dcc.Graph(figure=fig)

#     elif subtab == "historical-line7abc":
#         lines = []
#         for code in multi_sectors:
#             temp = calculate_sector_shares(df_view.copy(), code, trade_type)
#             temp = temp.sort_values("year")
#             if display_mode == "percentage":
#                 temp["change"] = temp["percentage"].diff()
#                 y_label = "% Point Change in Sector Share"
#             else:
#                 temp["change"] = temp["value"].diff()
#                 y_label = "Change in Sector Volume"
#             temp = temp[temp["year"] >= 2015].copy()
#             temp["sector"] = SECTOR_LABELS[code]
#             lines.append(temp)

#         if not lines:
#             return html.Div("Select at least one sector to display the line graph.", className="text-muted text-center")

#         df_combined = pd.concat(lines)
#         fig = px.line(
#         df_combined,
#             x="year",
#             y="change",
#             color="sector",
#             markers=True,
#             labels={"change": y_label},
#             title=f"Year-on-Year Change by Sector ({trade_type.capitalize()}) from {country} to {partner}"
#         )
#         fig.update_layout(
#             yaxis_title=y_label,
#             xaxis_title="Year",
#             plot_bgcolor="white",
#             paper_bgcolor="white",
#             margin=dict(t=30, l=10, r=10, b=10)
#         )
#         fig.update_traces(marker=dict(size=12),
#                   selector=dict(mode='markers'))
        
#         return dcc.Graph(figure=fig)

#     return dash.no_update

# from dash.exceptions import PreventUpdate

# @app.callback(
#     Output("sector-button-container7abc", "children"),
#     Input("module1c-subtabs7abc", "value")
# )
# def render_sector_buttons(subtab):
#     if subtab == "historical-bar7abc":
#         return html.Div([
#             html.Label("Select Sector", className="form-label fw-semibold mb-2"),
#             html.Div([
#                 html.Button(
#                     SECTOR_LABELS[code],
#                     id={"type": "sector-btn_module1c", "index": code},
#                     n_clicks_timestamp=0,
#                     className="btn me-2 mb-2",
#                     style={"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if code == SECTOR_CODES[0] else {}
#                 ) for code in SECTOR_CODES
#             ], className="d-flex flex-wrap")
#         ])
#     elif subtab == "historical-line7abc":
#         return html.Div([
#             html.Label("Select Sectors", className="form-label fw-semibold mb-2"),
#             html.Div([
#                 html.Button(
#                     SECTOR_LABELS[code],
#                     id={"type": "sector-btn-multi_module1c", "index": code},
#                     n_clicks=0,
#                     className="btn me-2 mb-2"
#                 ) for code in SECTOR_CODES
#             ], className="d-flex flex-wrap")
#         ])

    

#     return dash.no_update

# @app.callback(
#     Output("country-select-alt27abc", "options"),
#     Input("country-select7abc", "value")
# )
# def update_partner_dropdown(selected_country):
#     if not selected_country:
#         return []
#     country_id = COUNTRY_NAMES[selected_country]
#     filtered = df_raw[df_raw['country_a'] == country_id]
#     partner_ids = filtered['country_b'].dropna().unique()
#     partner_names = [COUNTRY_LABELS.get(p) for p in partner_ids if p in COUNTRY_LABELS and p != country_id]
#     return [{'label': name, 'value': name} for name in sorted(partner_names)]

# @app.callback(
#     Output("selected-sector7abc", "data"),
#     Output({"type": "sector-btn_module1c", "index": ALL}, "style"),
#     Input({"type": "sector-btn_module1c", "index": ALL}, "n_clicks_timestamp"),
#     State("module1c-subtabs7abc", "value")
# )
# def update_selected_sector(n_clicks, subtab):
#     if subtab != "historical-bar7abc":
#         return dash.no_update, []
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


# @app.callback(
#     Output("trade-type-select7abc", "data"),
#     Output("btn-total7abc", "outline"),
#     Output("btn-export7abc", "outline"),
#     Output("btn-import7abc", "outline"),
#     Input("btn-total7abc", "n_clicks"),
#     Input("btn-export7abc", "n_clicks"),
#     Input("btn-import7abc", "n_clicks"),
#     prevent_initial_call=True
# )
# def update_trade_type(n_total, n_export, n_import):
#     ctx = callback_context.triggered_id
#     if ctx == 'btn-total7abc':
#         return 'total', False, True, True
#     elif ctx == 'btn-export7abc':
#         return 'export', True, False, True
#     elif ctx == 'btn-import7abc':
#         return 'import', True, True, False
#     return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# @app.callback(
#     Output("display-mode7abc", "data"),
#     Input("toggle-display7abc", "value")
# )
# def update_display_mode(toggle_value):
#     return 'percentage' if toggle_value else 'volume'

# @app.callback(
#     Output("prediction-tab7abc", "disabled"),
#     Input("input-uploaded", "data")
# )
# def toggle_prediction_tab(uploaded):
#     return not uploaded

# @app.callback(
#     Output("module1c-subtabs7abc", "children"),
#     Output("module1c-subtabs7abc", "value"),
#     Input("module1c-tabs7abc", "value")
# )
# def toggle_subtab_visibility(main_tab):
#     if main_tab == "historical":
#         return [
#             dcc.Tab(label="Bar Chart", value="historical-bar7abc", disabled=False),
#             dcc.Tab(label="Line Chart", value="historical-line7abc", disabled=False),
#             dcc.Tab(label="Bar Chart", value="prediction-bar7abc", disabled=True),
#             dcc.Tab(label="Line Chart", value="prediction-line7abc", disabled=True)
#         ], "historical-bar7abc"
#     else:
#         return [
#             dcc.Tab(label="Bar Chart", value="historical-bar7abc", disabled=True),
#             dcc.Tab(label="Line Chart", value="historical-line7abc", disabled=True),
#             dcc.Tab(label="Bar Chart", value="prediction-bar7abc", disabled=False),
#             dcc.Tab(label="Line Chart", value="prediction-line7abc", disabled=False)
#         ], "prediction-bar7abc"

# # comment out
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
import dash_daq as daq

# === Load and Prepare Data ===
df_raw = pd.read_csv("data/final/historical_data.csv")

# === Load and Prepare Prediction Data ===
prediction_df = pd.read_csv("sample_2026.csv")
prediction_df = prediction_df[prediction_df["scenario"] == "postshock"].drop(columns=["scenario"])
prediction_df['year'] = pd.to_numeric(prediction_df['year'], errors='coerce')

# Merge historical and prediction data
df_combined_all = pd.concat([df_raw, prediction_df], ignore_index=True)
df_raw['year'] = pd.to_numeric(df_raw['year'], errors='coerce')

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

    html.H2("Sector Trade Trends Over Time", className="text-center mb-4"),

    html.Div([
        html.Div([
            html.Label("Select a Country", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select7abc',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value='Singapore',
                placeholder='Select a Country',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6"),

        html.Div([
            html.Label("Partner Country", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select-alt27abc',
                value='Australia',
                style={"color": "black", "backgroundColor": "white", "width": "100%"},
                placeholder="Select partner country",
                searchable=True,
                className="mb-3")
        ], className="col-md-6")
    ], className="row mb-3"),


    # html.Div([
    #     html.Label("Trade Type", className="form-label fw-semibold mb-1 text-center w-100"),
    #     dbc.ButtonGroup([
    #         dbc.Button("Trade Volume", id='btn-total7abc', n_clicks=0, outline=False, size='sm', color='primary'),
    #         dbc.Button("Exports", id='btn-export7abc', n_clicks=0, outline=True, size='sm', color='primary'),
    #         dbc.Button("Imports", id='btn-import7abc', n_clicks=0, outline=True, size='sm', color='primary')
    #     ], className='w-100')
    # ], className="mb-4"),

    # html.Div([
    #     html.Label("Display Mode", className="form-label fw-semibold mb-2"),
    #     daq.ToggleSwitch(
    #         id='toggle-display7abc',
    #         label='Volume / Percentage Share',
    #         value=True,
    #         className="mb-2",
    #         size=60
    #     )
    # ], className="mb-4 d-flex flex-column align-items-center"),
    html.Div([
        html.Div([
            html.Label("Trade Type", className="form-label fw-semibold mb-1 text-center w-100"),
            dbc.ButtonGroup([
                dbc.Button("Trade Volume", id='btn-total7abc', n_clicks=0, outline=False, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'}),
                dbc.Button("Exports", id='btn-export7abc', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'}),
                dbc.Button("Imports", id='btn-import7abc', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc', 'padding': '6px 20px', 'fontSize': '12px'})
            ], className='w-100')
        ], className="col-md-8"),

        html.Div([
            html.Label("Display Mode", className="form-label fw-semibold mb-1 text-center w-100"),
            daq.ToggleSwitch(
                id='toggle-display7abc',
                label='Volume / Percentage Share',
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

@app.callback(
    Output("module1c-graph-container7abc", "children"),
    Input("module1c-subtabs7abc", "value"),
    Input("country-select7abc", "value"),
    Input("country-select-alt27abc", "value"),
    Input("selected-sector7abc", "data"),
    Input("selected-sectors-multi7abc", "data"),
    Input("trade-type-select7abc", "data"),
    Input("display-mode7abc", "data")
)
def update_graph(subtab, country, partner, single_sector, multi_sectors, trade_type, display_mode):
    if not country or not partner:
        return dash.no_update

    country_id = COUNTRY_NAMES[country]
    partner_id = COUNTRY_NAMES[partner]

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
        return dash.no_update, [{} for _ in SECTOR_CODES]
    if not any(n_clicks):
        styles = [{"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if i == 0 else {} for i in range(len(SECTOR_CODES))]
        return SECTOR_CODES[0], styles
    selected_idx = n_clicks.index(max(n_clicks))
    styles = [{"border": "2px solid #007bff", "backgroundColor": "#e7f1ff"} if i == selected_idx else {} for i in range(len(SECTOR_CODES))]
    return SECTOR_CODES[selected_idx], styles

@app.callback(
    Output("selected-sectors-multi7abc", "data"),
    Output({"type": "sector-btn-multi_module1c", "index": ALL}, "style"),
    Input({"type": "sector-btn-multi_module1c", "index": ALL}, "n_clicks"),
    State("selected-sectors-multi7abc", "data")
)
def toggle_multi_sector(n_clicks_list, selected_sectors):
    ctx = callback_context.triggered_id
    if not ctx:
        raise PreventUpdate

    code = ctx["index"]
    if code in selected_sectors:
        selected_sectors.remove(code)
    else:
        selected_sectors.append(code)

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

@app.callback(
    Output("prediction-tab7abc", "disabled"),
    Input("input-uploaded", "data")
)
def toggle_prediction_tab(uploaded):
    return not uploaded

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

@app.callback(
    Output("module1c-tabs7abc", "value"),
    Input("input-uploaded", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(uploaded):
    if uploaded:
        return "prediction"
    return dash.no_update









