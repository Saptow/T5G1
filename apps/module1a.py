import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq


# === Load and Prepare Data ===
df_raw = pd.read_csv("data/final/historical_data.csv")
df_raw['year'] = pd.to_numeric(df_raw['year'], errors='coerce')

# Get latest and previous year
latest_year = df_raw['year'].max()
prev_year = df_raw['year'][df_raw['year'] < latest_year].max()

# Filter only the latest two years
df = df_raw[df_raw['year'].isin([latest_year, prev_year])].copy()

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
SECTOR_LIST = list(SECTOR_LABELS.values())

# === Fix: Correct Treemap Share Calculation ===
def calculate_country_shares(data, trade_type, selected_sector):
    sector_code = [k for k, v in SECTOR_LABELS.items() if v == selected_sector][0]

    if trade_type == "export":
        col = f"{sector_code}_export_A_to_B"
    elif trade_type == "import":
        col = f"{sector_code}_import_A_from_B"
    else:
        export_col = f"{sector_code}_export_A_to_B"
        import_col = f"{sector_code}_import_A_from_B"
        data[col] = data[export_col] + data[import_col]

    pivot = data.groupby(["country_b", "year"])[col].sum().unstack().fillna(0)
    pivot.columns = ['Previous', 'Current']
    pivot['Total_Current'] = pivot['Current'].sum()
    pivot['Total_Previous'] = pivot['Previous'].sum()

    pivot['current_share'] = 100 * pivot['Current'] / pivot['Total_Current']
    pivot['previous_share'] = 100 * pivot['Previous'] / pivot['Total_Previous']
    pivot['change'] = pivot['current_share'] - pivot['previous_share']
    pivot['share_change_clipped'] = pivot['change'].clip(-50, 50)

    pivot = pivot.reset_index().rename(columns={"country_b": "Country"})
    pivot['Country'] = pivot['Country'].map(COUNTRY_LABELS)
    pivot = pivot.dropna(subset=["Country"])

    return pivot

layout = html.Div([
    dcc.Store(id="trade-type-select1a", data='total'),
    dcc.Store(id="display-type1a", data='percentage'),
    html.H1("Trade by Sector and Partner Country", className="text-center mb-4", style={'color': '#2c3e50'}),

    html.Div([
        html.Div([
            html.Label("Select Country A", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='reporter-country-dropdown',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value='Singapore',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6"),

        html.Div([
            html.Label("Select Sector", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='sector-dropdown',
                options=[{'label': s, 'value': s} for s in SECTOR_LIST],
                value='Food and Agriculture',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6")
    ], className="row mb-3"),

    html.Div([
        html.Div([
            html.Label("Trade Type", className="form-label fw-semibold mb-1 text-center w-100"),
            dbc.ButtonGroup([
                dbc.Button("Total", id='btn-total1a', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc'}),
                dbc.Button("Exports", id='btn-export1a', n_clicks=0, outline=True, size='sm', style={'border': '1px solid #ccc'}),
                dbc.Button("Imports", id='btn-import1a', n_clicks=0, outline=True, size='sm', style={'border': '1px solid #ccc'})
            ], className='w-100')
        ], className="col-md-6"),

        html.Div([
            html.Label("Display Type", className="form-label fw-semibold mb-1 text-center w-100"),
            daq.ToggleSwitch(
                id='toggle-display1a',
                label='Volume / Percentage Share',
                value=True,
                className="mb-2",
                size=60)
        ], className="col-md-6 d-flex flex-column align-items-center"),
    ], className="row mb-4"),

    html.Div(id="tab-warning1a", className="text-danger mb-2 text-center"),

    dcc.Tabs(id="module1a-tabs", value="historical", children=[
        dcc.Tab(label="Historical", value="historical"),
        dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1a", disabled=True),
    ]),

    html.Div(id="module1a-tab-content", className="mt-3"),

    html.Div([
        html.Div(id='country-title1a', style={'display': 'none'}),
        dcc.Graph(id='bar-chart-sector-country', style={'display': 'none'}),
        dcc.Graph(id='treemap-sector-country', style={'display': 'none'})
    ])
])

app = get_app()

@app.callback(
    Output('trade-type-select1a', 'data'),
    Output('btn-total1a', 'color'),
    Output('btn-export1a', 'color'),
    Output('btn-import1a', 'color'),
    Input('btn-total1a', 'n_clicks'),
    Input('btn-export1a', 'n_clicks'),
    Input('btn-import1a', 'n_clicks'),
    prevent_initial_call=True
)
def update_trade_type(n_total, n_export, n_import):
    ctx = callback_context.triggered_id
    if ctx == 'btn-total1a':
        return 'total', 'primary', 'secondary', 'secondary'
    elif ctx == 'btn-export1a':
        return 'export', 'secondary', 'primary', 'secondary'
    elif ctx == 'btn-import1a':
        return 'import', 'secondary', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('display-type1a', 'data'),
    Input('toggle-display1a', 'value')
)
def update_display_type(value):
    return 'percentage' if value else 'volume'

@app.callback(
    Output("prediction-tab1a", "disabled"),
    Input("forecast-data", "data")
)
def toggle_prediction_tab(forecast_data):
    return not forecast_data

@app.callback(
    Output("module1a-tabs", "value"),
    Input("input-uploaded", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(uploaded):
    if uploaded:
        return "prediction"
    return dash.no_update

def render_tab_content(tab):
    return html.Div([
        html.Div(style={'marginTop': '20px'}),
        html.H5(id='country-title1a', className="text-center mb-2"),
        dcc.Graph(id='country-treemap1a', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
        dcc.Graph(id='country-bar1a', config={'displayModeBar': False}, style={"backgroundColor": "white"})
    ])

@app.callback(
    Output('country-treemap1a', 'style'),
    Output('country-bar1a', 'style'),
    Input('display-type1a', 'data')
)
def toggle_graph_visibility(display_type):
    if display_type == 'percentage':
        return {'display': 'block'}, {'display': 'none'}
    return {'display': 'none'}, {'display': 'block'}

@app.callback(
    Output('bar-chart-sector-country', 'figure'),
    Output('treemap-sector-country', 'figure'),
    Output('bar-chart-sector-country', 'style'),
    Output('treemap-sector-country', 'style'),
    Input('reporter-country-dropdown', 'value'),
    Input('sector-dropdown', 'value'),
    Input('trade-type-select1a', 'data'),
    Input('display-type1a', 'data'),
    Input('module1a-tabs', 'value'),
    Input('merged-prediction-df-store', 'data')  
)
def update_charts(reporter, sector, trade_type, display_type, tab, prediction_data):
    if tab == 'prediction' and prediction_data:
        data_source = pd.DataFrame(prediction_data)
    else:
        data_source = df

    df_filtered = data_source[data_source['country_a'] == COUNTRY_NAMES[reporter]].copy()
    sector_code = [k for k, v in SECTOR_LABELS.items() if v == sector][0]

    if trade_type == 'export':
        col = f"{sector_code}_export_A_to_B"
    elif trade_type == 'import':
        col = f"{sector_code}_import_A_from_B"
    else:  # total
        df_filtered["Total"] = df_filtered[f"{sector_code}_export_A_to_B"] + df_filtered[f"{sector_code}_import_A_from_B"]
        col = "Total"

    df_filtered = df_filtered[['year', 'country_b', col]].copy()
    df_filtered = df_filtered.rename(columns={'country_b': 'partner_country', col: 'value'})
    df_filtered['partner_country'] = df_filtered['partner_country'].map(COUNTRY_LABELS)

    pivot = df_filtered.pivot_table(index="partner_country", columns="year", values="value").reset_index()
    pivot.columns.name = None
    pivot = pivot.rename(columns={
        latest_year: "Current",
        prev_year: "Previous"
    })

    pivot['change'] = 100 * (pivot['Current'] - pivot['Previous']) / pivot['Previous'].replace(0, 1)
    pivot['hover'] = pivot.apply(
        lambda row: f"Current ({latest_year}): {row['Current']:.0f}<br>Previous ({prev_year}): {row['Previous']:.0f}<br>Change: {row['change']:+.2f}%",
        axis=1
    )

    fig_bar = px.bar(
        pivot,
        x='partner_country',
        y='Current',
        text=pivot['Current'].apply(lambda x: f"{x:,.0f}"),
        hover_data={'hover': True},
        color_discrete_sequence=['#2c7bb6']
    )
    fig_bar.add_bar(x=pivot['partner_country'], y=pivot['Previous'], opacity=0.5, name="Previous Period",
                    marker_color='#a6bddb')
    fig_bar.update_traces(hovertemplate=pivot['hover'])
    fig_bar.update_layout(barmode='overlay', title=f"{reporter}'s {trade_type.capitalize()} Volume in {sector}",
                          yaxis_title="Trade Volume", xaxis_title="Partner Country",
                          font=dict(family='Open Sans, sans-serif'),
                          legend=dict(x=0.99, y=0.99, xanchor='right', yanchor='top'),
                          plot_bgcolor='white', paper_bgcolor='white',
                          margin=dict(t=30, l=10, r=10, b=10))

    pivot['percentage'] = pivot['Current'] / pivot['Current'].sum() * 100
    pivot['label'] = pivot['partner_country']

    fig_treemap = px.treemap(
        pivot,
        path=['label'],
        values='Current',
        color='change',
        color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
        range_color=[-50, 50],
        custom_data=['percentage', 'change']
    )
    fig_treemap.update_traces(
        hovertemplate=(
        "<b>%{label}</b><br>" +
        "Current Share: %{customdata[0]:.1f}%<br>" +
        "Previous Share: %{customdata[1]:.1f}%<br>" +
        "Change in Share: %{customdata[2]:+.1f}%<extra></extra>"
    )
)
    fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

    if display_type == 'percentage':
        return fig_bar, fig_treemap, {'display': 'none'}, {'display': 'block'}
    else:
        return fig_bar, fig_treemap, {'display': 'block'}, {'display': 'none'}


# # === PREDICTION DATA PREPARATION ===
# new_df = pd.read_csv('sample_2026.csv')

# # Get only latest year from historical data
# historical_latest = df_raw[df_raw['year'] == df_raw['year'].max()].copy()

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


# Replace the PREDICTION DATA PREPARATION section with this:
@app.callback(
    Output("merged-prediction-df-store", "data"),
    Input("forecast-data", "data"),
    prevent_initial_call=True
)
def prepare_prediction_data(forecast_data):
    if not forecast_data:
        return dash.no_update
        
    # Convert the stored JSON data back to DataFrame
    new_df = pd.DataFrame(forecast_data)
    
    # Get only latest year from historical data
    historical_latest = df_raw[df_raw['year'] == df_raw['year'].max()].copy()
    
    # Filter to postshock scenario if available
    if 'scenario' in new_df.columns:
        new_df = new_df[new_df['scenario'] == 'postshock'].copy()
        new_df.drop(columns=['scenario'], inplace=True)
    
    # Ensure column alignment
    common_columns = list(set(historical_latest.columns).intersection(set(new_df.columns)))
    new_df = new_df[common_columns]
    historical_latest = historical_latest[common_columns]
    
    # Ensure all numeric columns are converted
    for col in new_df.columns:
        if col not in ['country_a', 'country_b', 'year']:
            new_df[col] = pd.to_numeric(new_df[col], errors='coerce')
    
    for col in historical_latest.columns:
        if col not in ['country_a', 'country_b', 'year']:
            historical_latest[col] = pd.to_numeric(historical_latest[col], errors='coerce')
    
    # Merge the two datasets
    merged_prediction_df = pd.concat([historical_latest, new_df], ignore_index=True)
    merged_prediction_df = merged_prediction_df.round(2)
    
    return merged_prediction_df.to_dict('records')

# Add a store to hold the processed prediction data
dcc.Store(id="merged-prediction-df-store", storage_type="memory"),

sidebar_controls = html.Div([])
