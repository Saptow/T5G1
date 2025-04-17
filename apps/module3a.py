## Module 3a for test

import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq

# === Load and Prepare Data ===
df_raw = pd.read_csv("data/final/historical_data.csv")

# Ensure year is numeric
df_raw['year'] = pd.to_numeric(df_raw['year'], errors='coerce')

# Get latest and previous year
latest_year = df_raw['year'].max()
#prev_year = view['year'][view['year'] < latest_year].max()
prev_year = df_raw['year'][df_raw['year'] < latest_year].max()

# Filter only the latest two years
df = df_raw[df_raw['year'].isin([latest_year, prev_year])].copy()

# Get unique list of countries from both A and B
COUNTRY_LIST = sorted(set(df['country_a'].unique()) | set(df['country_b'].unique()))

# Store sector mapping
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

# layout = html.Div([
#     #dcc.Store(id="input-uploaded"),
#     dcc.Store(id="trade-type-select1b", data='total'),
#     dcc.Store(id="display-type1b", data='percentage'),

#     html.H1("Countries' Trade Breakdown by Sector", className="text-center mb-4", style={'color': '#2c3e50'}),

#     html.Div([
#         html.Div([
#             html.Label("Select a Country", className="form-label fw-semibold mb-1"),
#             dcc.Dropdown(
#                 id='country-select1b',
#                 options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
#                 value= 'Singapore',
#                 placeholder='Select a Country',
#                 className="mb-3",
#                 style={"width": "100%"}
#             )
#         ], className="col-md-6"),

#         html.Div([
#             html.Label("Partner Country", className="form-label fw-semibold mb-1"),
#             dcc.Dropdown(
#                 id='country-select-alt21b',
#                 style={"color": "black", "backgroundColor": "white", "width": "100%"},
#                 placeholder="Select partner country",
#                 searchable=True,
#                 className="mb-3"
#             )
#         ], className="col-md-6")
#     ], className="row mb-3"),

#     html.Div([
#         html.Div([
#     html.Div([
#                 html.Label("Display Type", className="form-label fw-semibold mb-1 text-center w-100"),
#                 daq.ToggleSwitch(
#                     id='toggle-display1b',
#                     label='Volume / Percentage Share',
#                     value=True,
#                     className="mb-2",
#                     size=60)
#         ], className="col-md-6 d-flex flex-column align-items-center"),
#         html.Div([
#             html.Label("Trade Type", className="form-label fw-semibold mb-1 text-center w-100"),
#             dbc.ButtonGroup([
#                 dbc.Button("Trade Volume", id='btn-total1b', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc'}),
#                 dbc.Button("Exports", id='btn-export1b', n_clicks=0, outline=True, size='sm', style={'border': '1px solid #ccc'}),
#                 dbc.Button("Imports", id='btn-import1b', n_clicks=0, outline=True, size='sm', style={'border': '1px solid #ccc'})
#             ], className='w-100')
#         ], className="col-md-6"),

#         # html.Div([
#         #     html.Label("Display Type", className="form-label fw-semibold mb-1"),
#         #     daq.ToggleSwitch(
#         #         id='toggle-display1b',
#         #         label='Percentage / Volume',
#         #         value=True,
#         #         className="mb-2"
#         #     )
#         # ], className="col-md-6"),
        

#     ], className="row mb-4")
#     ]),

#     html.Div(id="tab-warning1b", className="text-danger mb-2 text-center"),

#     dcc.Tabs(id="module1b-tabs", value="historical", children=[
#         dcc.Tab(label="Historical", value="historical"),
#         dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1b", disabled=True),
#     ]),

#     html.Div(id="module1b-tab-content", className="mt-3"),

#     html.Div([
#         html.Div(id='country-title1b', style={'display': 'none'}),
#         dcc.Graph(id='country-treemap1b', style={'display': 'none'}),
#         dcc.Graph(id='country-bar1b', style={'display': 'none'})
#     ], style={'display': 'none'})
# ])
# new layout trial 
layout = html.Div([
    dcc.Store(id="trade-type-select1b", data='total'),
    dcc.Store(id="display-type1b", data='percentage'),

    html.H1("Sectoral Share Breakdown", className="mb-4 text-center"),
    html.Div(
        html.H6(
            """
            Analyze how different trading partners contribute to a selected sector’s trade for a given country. 
            Customize your view by choosing trade type (Total, Exports, Imports) and display mode (Volume or Percentage Share) to uncover shifts in trade concentration, evolving partner roles, and regional trade patterns across economic sectors.
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
                id='country-select1b',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value='Singapore',
                placeholder='Select a Country',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6"),

        html.Div([
            html.Label("Select Trading Partner:", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select-alt21b',
                style={"color": "black", "backgroundColor": "white", "width": "100%"},
                placeholder="Select partner country",
                searchable=True,
                className="mb-3"
            )
        ], className="col-md-6")
    ], className="row mb-3"),

    html.Div([
        html.Div([
            html.Label("Select Direction of Trade:", className="form-label fw-semibold mb-1"),
            html.Div([
                html.Div([
                    dbc.ButtonGroup([
                        dbc.Button("Total Trade", id='btn-total1b', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc'}),
                        dbc.Button("Exports", id='btn-export1b', n_clicks=0, outline=True, size='sm', style={'border': '1px solid #ccc'}),
                        dbc.Button("Imports", id='btn-import1b', n_clicks=0, outline=True, size='sm', style={'border': '1px solid #ccc'})
                    ], className='w-100')
                ], className="col-md-9"),

                html.Div([
                    html.Label("Select Visualisation Type", className="form-label fw-semibold mb-1"),
                    daq.ToggleSwitch(
                        id='toggle-display1b',
                        label='Bar Chart / Tree Map',
                        value=True,
                        className="mt-1",
                        size=60
                    )
                ], className="col-md-3 d-flex flex-column align-items-center justify-content-center")
            ], className="row")
        ], className="mb-4"),
        ]),

    html.Div(id="tab-warning1b", className="text-danger mb-2 text-center"),

    dcc.Tabs(id="module1b-tabs", value="historical", children=[
        dcc.Tab(label="Historical", value="historical"),
        dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1b", disabled=True),
    ]),

    html.Div(id="module1b-tab-content", className="mt-3"),

    html.Div([
        html.Div(id='country-title1b', style={'display': 'none'}),
        dcc.Graph(id='country-treemap1b', style={'display': 'none'}),
        dcc.Graph(id='country-bar1b', style={'display': 'none'})
    ], style={'display': 'none'})
])




app = get_app()

@app.callback(
    Output('trade-type-select1b', 'data'),
    Output('btn-total1b', 'color'),
    Output('btn-export1b', 'color'),
    Output('btn-import1b', 'color'),
    Input('btn-total1b', 'n_clicks'),
    Input('btn-export1b', 'n_clicks'),
    Input('btn-import1b', 'n_clicks'),
    prevent_initial_call=True
)
def update_trade_type(n_total, n_export, n_import):
    ctx = callback_context.triggered_id
    if ctx == 'btn-total1b':
        return 'total', 'primary', 'secondary', 'secondary'
    elif ctx == 'btn-export1b':
        return 'export', 'secondary', 'primary', 'secondary'
    elif ctx == 'btn-import1b':
        return 'import', 'secondary', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('display-type1b', 'data'),
    Input('toggle-display1b', 'value')
)
def update_display_type(value):
    return 'percentage' if value else 'volume'

@app.callback(
    Output("prediction-tab1b", "disabled"),
    Input("input-uploaded", "data")
)
def toggle_prediction_tab(uploaded):
    return not uploaded

@app.callback(
    Output("module1b-tabs", "value"),
    Input("input-uploaded", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(uploaded):
    if uploaded:
        return "prediction"
    return dash.no_update




# def render_tab_content(tab, display_type):
#     if tab == "historical":
#         return html.Div([
#             html.Div(style={'marginTop': '20px'}),
#             html.H5(id='country-title1b', className="text-center mb-2"),
#             dcc.Graph(id='country-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white", 'display': 'block' if display_type == 'percentage' else 'none'}),
#             dcc.Graph(id='country-bar1b', config={'displayModeBar': False}, style={"backgroundColor": "white", 'display': 'block' if display_type == 'volume' else 'none'})
#         ])
#     elif tab == "prediction":
#         return html.Div([
#             html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
#             html.P("This will show trade predictions based on uploaded news input.", className="text-center")
#         ])

# @app.callback(
#     Output("module1b-tab-content", "children"),
#     Input("module1b-tabs", "value"),
#     #State('display-type1b', 'data')
# )

# def render_tab_content(tab, display_type):
#     if tab == "historical":
#         treemap_style = {"backgroundColor": "white", 'display': 'block' if display_type == 'percentage' else 'none'}
#         bar_style = {"backgroundColor": "white", 'display': 'block' if display_type == 'volume' else 'none'}
#         return html.Div([
#             html.Div(style={'marginTop': '20px'}),
#             html.H5(id='country-title1b', className="text-center mb-2"),
#             dcc.Graph(id='country-treemap1b', config={'displayModeBar': False}, style=treemap_style),
#             dcc.Graph(id='country-bar1b', config={'displayModeBar': False}, style=bar_style)
#         ])
#     elif tab == "prediction":
#         return html.Div([
#             html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
#             html.P("This will show trade predictions based on uploaded news input.", className="text-center")
#         ])
@app.callback(
    Output("module1b-tab-content", "children"),
    Input("module1b-tabs", "value")
)
# def render_tab_content(tab):
#     if tab == "historical":
#         return html.Div([
#             html.Div(style={'marginTop': '20px'}),
#             html.H5(id='country-title1b', className="text-center mb-2"),
#             dcc.Graph(id='country-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
#             dcc.Graph(id='country-bar1b', config={'displayModeBar': False}, style={"backgroundColor": "white"})
#         ])
#     elif tab == "prediction":
#         return html.Div([
#             html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
#             html.P("This will show trade predictions based on uploaded news input.", className="text-center")
#         ])

def render_tab_content(tab):
    return html.Div([
        html.Div(style={'marginTop': '20px'}),
        html.H5(id='country-title1b', className="text-center mb-2"),
        dcc.Graph(id='country-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
        dcc.Graph(id='country-bar1b', config={'displayModeBar': False}, style={"backgroundColor": "white"})
    ])

# # Temp Comment Out   
# @app.callback(
#     Output('country-treemap1b', 'figure'),
#     Output('country-bar1b', 'figure'),
#     Output('country-select-alt21b', 'options'),
#     Output('country-title1b', 'children'),
#     Input('country-select1b', 'value'),
#     Input('trade-type-select1b', 'data'),
#     Input('country-select-alt21b', 'value')
# )
# def update_visualizations(selected_country, trade_type, selected_partner):

#     country_id = COUNTRY_NAMES[selected_country]

#     latest_year = df_raw['year'].max()
#     prev_year = df_raw['year'][df_raw['year'] < latest_year].max()

#     filtered = df[(df['country_a'] == country_id) | (df['country_b'] == country_id)].copy()

#     filtered['partner_country_code'] = filtered.apply(
#         lambda row: row['country_b'] if row['country_a'] == country_id else row['country_a'], axis=1
#     )

#     filtered['partner_country'] = filtered['partner_country_code'].map(COUNTRY_LABELS)

#     partner_options = [
#     {'label': name, 'value': name}
#     for name in sorted(filtered['partner_country'].unique())
#     if name != selected_country
#     ]  

#     if selected_partner:
#         view = filtered[filtered['partner_country'] == selected_partner]
#     else:
#         view = filtered

#     filtered['partner_country'] = filtered.apply(
#         lambda row: row['country_b'] if row['country_a'] == selected_country else row['country_a'], axis=1
#     )

#     view.attrs['trade_type'] = trade_type
#     view.attrs['direction'] = 'A_to_B'  # all data is from A to B, already included both ways

#     sector_agg = calculate_percentages(view, 'sector')

#     display_trade_type = "Trade Volume" if trade_type == "total" else trade_type.capitalize()
    
#     if selected_partner:
#         title = f"{display_trade_type} from {selected_country} to {selected_partner} by Sector in {latest_year}"
#     else:
#         title = f"{selected_country}'s {display_trade_type} by Sector in {latest_year}"

#     for df_agg in [sector_agg]:
#         df_agg['percentage'] = df_agg['percentage'].round(1)
#         df_agg['change_str'] = df_agg['change'].apply(lambda x: f"{x:+.2f}%")
#         df_agg['previous_pct'] = df_agg['previous_volume'] / df_agg['previous_volume'].sum() * 100
#         df_agg['previous_pct_str'] = df_agg['previous_pct'].round(1).astype(str) + '%'


#     max_change = sector_agg['change'].abs().max() * 5

#     hover_template = (
#     '<b>%{label}</b><br>'
#     'Current Share (' + str(latest_year) + '): %{customdata[0]}<br>'
#     'Previous Share (' + str(prev_year) + '): %{customdata[1]}<br>'
#     'Change in Percentage Share: %{customdata[2]}'
#     )


#     fig_treemap = px.treemap(
#         sector_agg, path=['sector'], values='percentage', color='change_clipped',
#         color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
#         range_color=[-max_change, max_change], color_continuous_midpoint=0,
#         custom_data=['percentage', 'previous_pct_str', 'change_str']
#         )
    
#     fig_treemap.update_traces(
#         hovertemplate=hover_template,
#         texttemplate='<b>%{label}</b><br>%{customdata[0]} (%{customdata[2]})'
#     )

#     fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

#     fig_bar = generate_bar_chart(sector_agg, 'sector', 'volume', 'previous_volume', latest_year, prev_year)

#     return fig_treemap, fig_bar, partner_options, title
## Comment End

@app.callback(
    Output('country-treemap1b', 'style'),
    Output('country-bar1b', 'style'),
    Input('display-type1b', 'data')
)
def toggle_graph_visibility(display_type):
    if display_type == 'percentage':
        return {'display': 'block'}, {'display': 'none'}
    return {'display': 'none'}, {'display': 'block'}


# === Helpers ===

# def calculate_percentages(data, group_by):
#     grouped = data.groupby(group_by, as_index=False).agg({
#         'volume': 'sum',
#         'previous_volume': 'sum'
#     })
#     total_current = data['volume'].sum()
#     total_previous = data['previous_volume'].sum()
#     grouped['percentage'] = 100 * grouped['volume'] / total_current if total_current else 0
#     grouped['change'] = (
#         100 * (grouped['volume'] / total_current - grouped['previous_volume'] / total_previous)
#         if total_current and total_previous else 0
#     )
#     max_abs_change = grouped['change'].abs().max()
#     dynamic_range = max(1, round(max_abs_change * 5, 2))
#     grouped['change_clipped'] = grouped['change'].clip(lower=-dynamic_range, upper=dynamic_range)
#     grouped['dynamic_range'] = dynamic_range
#     return grouped

# def calculate_percentages(data, group_by, latest_year, prev_year):
#     #latest_year = data['year'].max()
#     #prev_year = data['year'][data['year'] < latest_year].max()

#     trade_type = data.attrs.get('trade_type', 'total')

#     if trade_type == 'export':
#         sector_cols = [f"bec_{i}_export_A_to_B" for i in range(1, 9)]
#     elif trade_type == 'import':
#         sector_cols = [f"bec_{i}_import_A_from_B" for i in range(1, 9)]
#     else:  # total = export + import
#         sector_cols = [f"bec_{i}_export_A_to_B" for i in range(1, 9)] + \
#                       [f"bec_{i}_import_A_from_B" for i in range(1, 9)]

#     # Group by year
#     current = data[data['year'] == latest_year][sector_cols].sum()
#     previous = data[data['year'] == prev_year][sector_cols].sum()

#     sector_agg = pd.DataFrame({
#         'sector_code': sector_cols,
#         'volume': current.values,
#         'previous_volume': previous.values
#     })

#     # Combine duplicates if total (export + import)
#     if trade_type == 'total':
#         sector_agg['sector'] = sector_agg['sector_code'].str.extract(r'(bec_\d+)_')[0]
#         sector_agg = sector_agg.groupby('sector', as_index=False).agg({
#             'volume': 'sum',
#             'previous_volume': 'sum'
#         })
#     else:
#         sector_agg['sector'] = sector_agg['sector_code'].str.extract(r'(bec_\d+)_')[0]

#     total_volume = sector_agg['volume'].sum()
#     total_previous = sector_agg['previous_volume'].sum()

#     sector_agg['percentage'] = 100 * sector_agg['volume'] / total_volume if total_volume else 0
#     sector_agg['change'] = (
#         100 * (sector_agg['volume'] / total_volume - sector_agg['previous_volume'] / total_previous)
#         if total_volume and total_previous else 0
#     )
#     sector_agg['change_clipped'] = sector_agg['change'].clip(lower=-50, upper=50)
#     sector_agg['dynamic_range'] = 50
#     sector_agg['sector'] = sector_agg['sector'].map(SECTOR_LABELS)

#     return sector_agg

def calculate_percentages(data, group_by, latest_year, prev_year):
    trade_type = data.attrs.get('trade_type', 'total')

    if trade_type == 'export':
        sector_cols = [f"bec_{i}_export_A_to_B" for i in range(1, 9)]
    elif trade_type == 'import':
        sector_cols = [f"bec_{i}_import_A_from_B" for i in range(1, 9)]
    else:  # total = export + import from same A→B row
        sector_cols = [f"bec_{i}_export_A_to_B" for i in range(1, 9)] + \
                      [f"bec_{i}_import_A_from_B" for i in range(1, 9)]

    # Sum across years for those columns
    current = data[data['year'] == latest_year][sector_cols].sum()
    previous = data[data['year'] == prev_year][sector_cols].sum()

    sector_agg = pd.DataFrame({
        'sector_code': sector_cols,
        'volume': current.values,
        'previous_volume': previous.values
    })

    # Combine exports + imports under same sector name if total
    if trade_type == 'total':
        sector_agg['sector'] = sector_agg['sector_code'].str.extract(r'(bec_\d+)_')[0]
        sector_agg = sector_agg.groupby('sector', as_index=False).agg({
            'volume': 'sum',
            'previous_volume': 'sum'
        })
    else:
        sector_agg['sector'] = sector_agg['sector_code'].str.extract(r'(bec_\d+)_')[0]

    # Calculate percentage share and change
    total_volume = sector_agg['volume'].sum()
    total_previous = sector_agg['previous_volume'].sum()

    sector_agg['percentage'] = (
        100 * sector_agg['volume'] / total_volume if total_volume else 0
    )
    sector_agg['change'] = (
        100 * (sector_agg['volume'] / total_volume - sector_agg['previous_volume'] / total_previous)
        if total_volume and total_previous else 0
    )

    # Clip for treemap coloring and map labels
    sector_agg['change_clipped'] = sector_agg['change'].clip(lower=-50, upper=50)
    sector_agg['dynamic_range'] = 50
    sector_agg['sector'] = sector_agg['sector'].map(SECTOR_LABELS)

    return sector_agg

def generate_bar_chart(df, x_col, y_col, previous_col, latest_year, prev_year):
    df_sorted = df.sort_values(y_col, ascending=False)
    df_sorted['change'] = 100 * (df_sorted[y_col] - df_sorted[previous_col]) / df_sorted[previous_col].replace(0, 1)
    #df_sorted['hover'] = df_sorted.apply(lambda row: f"Current: {row[y_col]:,.0f}<br>Previous: {row[previous_col]:,.0f}<br>Change: {row['change']:+.2f}%", axis=1)
    df_sorted['hover'] = df_sorted.apply(
        lambda row: f"Current ({latest_year}): {row[y_col]:,.0f}<br>Previous ({prev_year}): {row[previous_col]:,.0f}<br>Change in Volume: {row['change']:+.2f}%",
        axis=1
    )

    fig = px.bar(df_sorted, x=x_col, y=y_col, text=df_sorted[y_col].apply(lambda x: f"{x:,.0f}"),
                 labels={x_col: x_col.title(), y_col: y_col.title()}, hover_data={'hover': True}, color_discrete_sequence=['#2c7bb6'])
    fig.add_bar(x=df_sorted[x_col], y=df_sorted[previous_col], opacity=0.5, name="Previous Period",
                marker_color='#a6bddb')
    fig.update_traces(hovertemplate=df_sorted['hover'])
    fig.update_layout(barmode='overlay', font=dict(family='Open Sans, sans-serif'),
                      legend=dict(x=0.99, y=0.99, xanchor='right', yanchor='top'),
                      plot_bgcolor='white', paper_bgcolor='white',
                      margin=dict(t=30, l=10, r=10, b=10))
    return fig


sidebar_controls = html.Div([])


### INSERT PREDICTION TAB CODE AND DATA MANGLING HERE

# # === PREDICTION DATA PREPARATION ===
# new_df = pd.read_csv('sample_2026.csv')

# Get only latest year from historical data
historical_latest = df_raw[df_raw['year'] == df_raw['year'].max()].copy()

# new_df = new_df[new_df['scenario'] == 'postshock'].copy()
# new_df.drop(columns=['scenario'], inplace=True)

# # Step 2: Ensure column alignment
# new_df = new_df[historical_latest.columns]

# # Step 3: Ensure all numeric columns are converted
# for col in new_df.columns:
#     if col not in ['country_a', 'country_b', 'year']:
#         new_df[col] = pd.to_numeric(new_df[col], errors='coerce')

# for col in historical_latest.columns:
#     if col not in ['country_a', 'country_b', 'year']:
#         historical_latest[col] = pd.to_numeric(historical_latest[col], errors='coerce')

# # Merge the two datasets
# merged_prediction_df = pd.concat([historical_latest, new_df], ignore_index=True)
# merged_prediction_df = merged_prediction_df.round(2)


# Commenting Out
# @app.callback(
#     Output('country-treemap1b', 'figure'),
#     Output('country-bar1b', 'figure'),
#     Output('country-select-alt21b', 'options'),
#     Output('country-title1b', 'children'),
#     Input('country-select1b', 'value'),
#     Input('trade-type-select1b', 'data'),
#     Input('country-select-alt21b', 'value'),
#     Input('module1b-tabs', 'value')
# )
# def update_visualizations_with_prediction(selected_country, trade_type, selected_partner, active_tab):
#     if active_tab == "prediction":
#         df_view = merged_prediction_df
#     else:
#         df_view = df

#     country_id = COUNTRY_NAMES[selected_country]

#     filtered = df_view[(df_view['country_a'] == country_id) | (df_view['country_b'] == country_id)].copy()

#     filtered['partner_country_code'] = filtered.apply(
#         lambda row: row['country_b'] if row['country_a'] == country_id else row['country_a'], axis=1
#     )
#     filtered['partner_country'] = filtered['partner_country_code'].map(COUNTRY_LABELS)

#     partner_options = [
#         {'label': name, 'value': name}
#         for name in sorted(filtered['partner_country'].unique())
#         if name != selected_country
#     ]

#     if selected_partner:
#         view = filtered[filtered['partner_country'] == selected_partner]
#     else:
#         view = filtered

#     latest_year = view['year'].max()
#     prev_year = view['year'][view['year'] < latest_year].max()

#     view.attrs['trade_type'] = trade_type

#     sector_agg = calculate_percentages(view, 'sector')

#     display_trade_type = "Trade Volume" if trade_type == "total" else trade_type.capitalize()
#     if selected_partner:
#         title = f"{display_trade_type} from {selected_country} to {selected_partner} by Sector in {latest_year}"
#     else:
#         title = f"{selected_country}'s {display_trade_type} by Sector in {latest_year}"

#     sector_agg['percentage'] = sector_agg['percentage'].round(1)
#     sector_agg['change_str'] = sector_agg['change'].apply(lambda x: f"{x:+.2f}%")
#     sector_agg['previous_pct'] = sector_agg['previous_volume'] / sector_agg['previous_volume'].sum() * 100
#     sector_agg['previous_pct_str'] = sector_agg['previous_pct'].round(1).astype(str) + '%'

#     max_change = sector_agg['change'].abs().max() * 5

#     hover_template = (
#         '<b>%{label}</b><br>'
#         'Current Share (' + str(latest_year) + '): %{customdata[0]}<br>'
#         'Previous Share (' + str(prev_year) + '): %{customdata[1]}<br>'
#         'Change in Percentage Share: %{customdata[2]}'
#     )

#     fig_treemap = px.treemap(
#         sector_agg, path=['sector'], values='percentage', color='change_clipped',
#         color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
#         range_color=[-max_change, max_change], color_continuous_midpoint=0,
#         custom_data=['percentage', 'previous_pct_str', 'change_str']
#     )
#     fig_treemap.update_traces(
#         hovertemplate=hover_template,
#         texttemplate='<b>%{label}</b><br>%{customdata[0]} (%{customdata[2]})'
#     )
#     fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

#     fig_bar = generate_bar_chart(sector_agg, 'sector', 'volume', 'previous_volume', latest_year, prev_year)

#     return fig_treemap, fig_bar, partner_options, title

# @app.callback(
#     Output('country-treemap1b', 'figure'),
#     Output('country-bar1b', 'figure'),
#     Output('country-select-alt21b', 'options'),
#     Output('country-title1b', 'children'),
#     Input('country-select1b', 'value'),
#     Input('trade-type-select1b', 'data'),
#     Input('country-select-alt21b', 'value'),
#     Input('module1b-tabs', 'value')  # this lets us switch dataset
# )
# def update_all_visualizations(selected_country, trade_type, selected_partner, tab):
#     # === Select dataset ===
#     if tab == 'prediction':
#         data_source = merged_prediction_df
#     else:
#         data_source = df

#     country_id = COUNTRY_NAMES[selected_country]

#     # keep data rows that contain selected country related data 
#     filtered = data_source[(data_source['country_a'] == country_id) | (data_source['country_b'] == country_id)].copy()

#     filtered['partner_country_code'] = filtered.apply(
#         lambda row: row['country_b'] if row['country_a'] == country_id else row['country_a'], axis=1
#     )
#     filtered['partner_country'] = filtered['partner_country_code'].map(COUNTRY_LABELS)

#     partner_options = [
#         {'label': name, 'value': name}
#         for name in sorted(filtered['partner_country'].unique())
#         if name != selected_country
#     ]

#     if selected_partner:
#         partner_id = COUNTRY_NAMES[selected_partner]

#         if trade_type == "export":
#             view = filtered[(filtered['country_a'] == country_id) & (filtered['country_b'] == partner_id)]
#         elif trade_type == "import":
#             view = filtered[(filtered['country_a'] == partner_id) & (filtered['country_b'] == country_id)]
#         else:  # total
#             view = filtered[
#                 ((filtered['country_a'] == country_id) & (filtered['country_b'] == partner_id)) |
#                 ((filtered['country_a'] == partner_id) & (filtered['country_b'] == country_id))
#             ]
#     else:
#         if trade_type == "export":
#           view = filtered[(filtered['country_a'] == country_id)]
#         elif trade_type == "import":
#             view = filtered[(filtered['country_b'] == country_id)]
#         else:
#             view = filtered


#     latest_year = view['year'].max()
#     prev_year = view['year'][view['year'] < latest_year].max()

#     view.attrs['trade_type'] = trade_type

#     sector_agg = calculate_percentages(view, 'sector', latest_year, prev_year)

#     display_trade_type = "Trade Volume" if trade_type == "total" else trade_type.capitalize()

#     is_prediction = tab == "prediction"
#     title_prefix = "Predicted " if is_prediction else ""
#     title_suffix = f"for {latest_year}" if is_prediction else f"in {latest_year}"

#     if selected_partner:
#         title = f"{title_prefix}{display_trade_type} from {selected_country} to {selected_partner} by Sector {title_suffix}"
#     else:
#         title = f"{title_prefix}{selected_country}'s {display_trade_type} by Sector {title_suffix}"


#     sector_agg['percentage'] = sector_agg['percentage'].round(1)
#     sector_agg['change_str'] = sector_agg['change'].apply(lambda x: f"{x:+.2f}%")
#     sector_agg['previous_pct'] = sector_agg['previous_volume'] / sector_agg['previous_volume'].sum() * 100
#     sector_agg['previous_pct_str'] = sector_agg['previous_pct'].round(1).astype(str) + '%'

#     max_change = sector_agg['change'].abs().max() * 5

#     hover_template = (
#         '<b>%{label}</b><br>'
#         'Current Share (' + str(latest_year) + '): %{customdata[0]}<br>'
#         'Previous Share (' + str(prev_year) + '): %{customdata[1]}<br>'
#         'Change in Percentage Share: %{customdata[2]}'
#     )

#     fig_treemap = px.treemap(
#         sector_agg, path=['sector'], values='percentage', color='change_clipped',
#         color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
#         range_color=[-max_change, max_change], color_continuous_midpoint=0,
#         custom_data=['percentage', 'previous_pct_str', 'change_str']
#     )
#     fig_treemap.update_traces(
#         hovertemplate=hover_template,
#         texttemplate='<b>%{label}</b><br>%{customdata[0]} (%{customdata[2]})'
#     )
#     fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

#     fig_bar = generate_bar_chart(sector_agg, 'sector', 'volume', 'previous_volume', latest_year, prev_year)

#     return fig_treemap, fig_bar, partner_options, title

@app.callback(
    Output('country-treemap1b', 'figure'),
    Output('country-bar1b', 'figure'),
    Output('country-select-alt21b', 'options'),
    Output('country-title1b', 'children'),
    Input('country-select1b', 'value'),
    Input('trade-type-select1b', 'data'),
    Input('country-select-alt21b', 'value'),
    Input('module1b-tabs', 'value'),
    Input('forecast-data', 'data')  # Add this input
)
def update_all_visualizations(selected_country, trade_type, selected_partner, tab, forecast_data):
    if tab == 'prediction':
        # Instead of reading from CSV, use the stored forecast data
        if forecast_data:
            # Convert the stored JSON data back to a DataFrame
            new_df = pd.DataFrame(forecast_data)
            
            # Apply any necessary transformations similar to what you did with the CSV data
            new_df = new_df[new_df['scenario'] == 'postshock'].copy() if 'scenario' in new_df.columns else new_df
            if 'scenario' in new_df.columns:
                new_df.drop(columns=['scenario'], inplace=True)
            
            # Ensure column alignment with historical data
            common_columns = list(set(new_df.columns).intersection(set(historical_latest.columns)))
            new_df = new_df[common_columns]
            
            # Convert numeric columns
            for col in new_df.columns:
                if col not in ['country_a', 'country_b', 'year']:
                    new_df[col] = pd.to_numeric(new_df[col], errors='coerce')
            
            # Merge with historical data
            merged_prediction_df = pd.concat([historical_latest, new_df], ignore_index=True)
            merged_prediction_df = merged_prediction_df.round(2)
            
            data_source = merged_prediction_df
        else:
            # If no forecast data available, fall back to historical
            data_source = df
    else:
        data_source = df

    # Rest of the visualization code remains the same
    country_id = COUNTRY_NAMES[selected_country]
    
    # Filter data: always treat selected_country as A
    filtered = data_source[data_source['country_a'] == country_id].copy()
    filtered['partner_country'] = filtered['country_b'].map(COUNTRY_LABELS)

    partner_options = [
        {'label': name, 'value': name}
        for name in sorted(filtered['partner_country'].unique())
        if name != selected_country
    ]

    if selected_partner:
        partner_id = COUNTRY_NAMES[selected_partner]
        view = filtered[filtered['country_b'] == partner_id]
    else:
        view = filtered

    latest_year = view['year'].max()
    prev_year = view['year'][view['year'] < latest_year].max()

    view.attrs['trade_type'] = trade_type

    sector_agg = calculate_percentages(view, 'sector', latest_year, prev_year)

    display_trade_type = "Trade Value" if trade_type == "total" else trade_type.capitalize()
    is_prediction = tab == "prediction"
    title_prefix = "Predicted " if is_prediction else ""
    title_suffix = f"for {latest_year}" if is_prediction else f"in {latest_year}"

    if selected_partner:
        title = f"{title_prefix}{display_trade_type} from {selected_country} to {selected_partner} by Sector {title_suffix}"
    else:
        title = f"{title_prefix}{selected_country}'s {display_trade_type} by Sector {title_suffix}"

    sector_agg['percentage'] = sector_agg['percentage'].round(1)
    sector_agg['change_str'] = sector_agg['change'].apply(lambda x: f"{x:+.2f}%")
    sector_agg['previous_pct'] = sector_agg['previous_volume'] / sector_agg['previous_volume'].sum() * 100
    sector_agg['previous_pct_str'] = sector_agg['previous_pct'].round(1).astype(str) + '%'

    max_change = sector_agg['change'].abs().max() * 5

    hover_template = (
        '<b>%{label}</b><br>'
        'Current Share (' + str(latest_year) + '): %{customdata[0]}<br>'
        'Previous Share (' + str(prev_year) + '): %{customdata[1]}<br>'
        'Change in Percentage Share: %{customdata[2]}'
    )

    fig_treemap = px.treemap(
        sector_agg, path=['sector'], values='percentage', color='change_clipped',
        color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
        range_color=[-max_change, max_change], color_continuous_midpoint=0,
        custom_data=['percentage', 'previous_pct_str', 'change_str']
    )
    fig_treemap.update_traces(
        hovertemplate=hover_template,
        texttemplate='<b>%{label}</b><br>%{customdata[0]} (%{customdata[2]})'
    )
    fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

    fig_bar = generate_bar_chart(sector_agg, 'sector', 'volume', 'previous_volume', latest_year, prev_year)

    return fig_treemap, fig_bar, partner_options, title

