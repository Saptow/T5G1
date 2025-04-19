## Module 3a 

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

# layout
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
            html.Div([
                html.Div([
                    html.Label("Trade Type:", className="form-label fw-semibold mb-1 text-center w-100"),
                    dbc.ButtonGroup([
                        dbc.Button("Total Trade", id='btn-total1b', n_clicks=0, outline=False, size='sm', color='primary', style={'border': '1px solid #ccc'}),
                        dbc.Button("Exports", id='btn-export1b', n_clicks=0, outline=True, size='sm', style={'border': '1px solid #ccc'}),
                        dbc.Button("Imports", id='btn-import1b', n_clicks=0, outline=True, size='sm', style={'border': '1px solid #ccc'})
                    ], className='w-100')
                ], className="col-md-6"),

                html.Div([
                    html.Label("Display Type", className="form-label fw-semibold mb-1 text-center w-100"),
                    daq.ToggleSwitch(
                        id='toggle-display1b',
                        label='Volume / Percentage Share',
                        value=True,
                        className="mt-1",
                        size=60
                    )
                ], className="col-md-6 d-flex flex-column align-items-center justify-content-center")
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
    Output('btn-total1b', 'outline'),
    Output('btn-export1b', 'outline'),
    Output('btn-import1b', 'outline'),
    Input('btn-total1b', 'n_clicks'),
    Input('btn-export1b', 'n_clicks'),
    Input('btn-import1b', 'n_clicks'),
    prevent_initial_call=True
)
def update_trade_type(n_total, n_export, n_import):
    ctx = callback_context.triggered_id
    if ctx == 'btn-total1b':
        return 'total', 'primary', 'secondary', 'secondary', False, True, True
    elif ctx == 'btn-export1b':
        return 'export', 'secondary', 'primary', 'secondary', True, False, True
    elif ctx == 'btn-import1b':
        return 'import', 'secondary', 'secondary', 'primary', True, True, False
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

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



@app.callback(
    Output("module1b-tab-content", "children"),
    Input("module1b-tabs", "value")
)

def render_tab_content(tab):
    return html.Div([
        html.Div(style={'marginTop': '20px'}),
        html.H5(id='country-title1b', className="text-center mb-2"),
        dcc.Graph(id='country-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
        dcc.Graph(id='country-bar1b', config={'displayModeBar': False}, style={"backgroundColor": "white"})
    ])

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



# Get only latest year from historical data
historical_latest = df_raw[df_raw['year'] == df_raw['year'].max()].copy()

@app.callback(
    Output('country-treemap1b', 'figure'),
    Output('country-bar1b', 'figure'),
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
    
    # filter data: always treat selected_country as A
    filtered = data_source[data_source['country_a'] == country_id].copy()
    filtered['partner_country'] = filtered['country_b'].map(COUNTRY_LABELS)

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
    sector_agg['percentage_str'] = sector_agg['percentage'].astype(str) + '%'
    
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
        custom_data=['percentage_str', 'previous_pct_str', 'change_str'] 
    )
    fig_treemap.update_traces(
        hovertemplate=hover_template,
        texttemplate='<b>%{label}</b><br>%{customdata[0]} (%{customdata[2]})'
    )
    fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

    fig_bar = generate_bar_chart(sector_agg, 'sector', 'volume', 'previous_volume', latest_year, prev_year)

    return fig_treemap, fig_bar, title

@app.callback(
    Output('country-select-alt21b', 'options'),
    Input('country-select1b', 'value'),
    State('module1b-tabs', 'value'),
    State('forecast-data', 'data')
)
def update_partner_options(selected_country, tab, forecast_data):
    country_id = COUNTRY_NAMES[selected_country]

    if tab == 'prediction' and forecast_data:
        df_forecast = pd.DataFrame(forecast_data)
        if 'scenario' in df_forecast.columns:
            df_forecast = df_forecast[df_forecast['scenario'] == 'postshock'].drop(columns=['scenario'])
        df_forecast['year'] = pd.to_numeric(df_forecast['year'], errors='coerce')
        latest_historical = df_raw[df_raw['year'] == df_raw['year'].max()]
        df_combined = pd.concat([latest_historical, df_forecast], ignore_index=True)
    else:
        df_combined = df.copy()

    # Filter rows where selected country is the exporter (A)
    filtered = df_combined[df_combined['country_a'] == country_id].copy()
    filtered['partner_country'] = filtered['country_b'].map(COUNTRY_LABELS)

    options = [
        {'label': name, 'value': name}
        for name in sorted(filtered['partner_country'].dropna().unique())
        if name != selected_country
    ]
    return options
