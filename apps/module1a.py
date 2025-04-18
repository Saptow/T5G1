



import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq

app = get_app()

# === Load Data ===
df_raw = pd.read_csv("data/final/historical_data.csv")
df_raw['year'] = pd.to_numeric(df_raw['year'], errors='coerce')
latest_year = df_raw['year'].max()
prev_year = df_raw['year'][df_raw['year'] < latest_year].max()
df = df_raw[df_raw['year'].isin([latest_year, prev_year])].copy()

COUNTRY_LABELS = {
    "AUS": "Australia", "CHE": "Switzerland", "CHN": "China",
    "DEU": "Germany", "FRA": "France", "HKG": "Hong Kong", "IDN": "Indonesia", "IND": "India",
    "JPN": "Japan", "KOR": "South Korea", "MYS": "Malaysia", "NLD": "Netherlands",
    "PHL": "Philippines", "SGP": "Singapore", "THA": "Thailand", "USA": "United States",
    "VNM": "Vietnam"
}
COUNTRY_NAMES = {v: k for k, v in COUNTRY_LABELS.items()}
SECTOR_LABELS = {
    "bec_1": "Food and Agriculture", "bec_2": "Energy and Mining", "bec_3": "Construction and Housing",
    "bec_4": "Textile and Footwear", "bec_5": "Transport and Travel", "bec_6": "ICT and Business",
    "bec_7": "Health and Education", "bec_8": "Government and Others"
}

layout = html.Div([
    dcc.Store(id="trade-type-select1c", data='total'),
    dcc.Store(id="display-type1c", data='percentage'),

    html.H1("Country Share Breakdown", className="text-center mb-4", style={'color': '#2c3e50'}),

    html.Div(
        html.H6(
            """
            Dive into detailed sector-level trade flows between a selected country and its trading partners. 
            Customize your view by choosing specific sectors, trade types (Total, Exports, Imports), and how trade is measured—by absolute volume or percentage share. 
            Use this tool to identify key contributors and shifts in bilateral trade relationships across different economic sectors.
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
            html.Label("Select a Country", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select1c',
                options=[{'label': name, 'value': name} for name in COUNTRY_LABELS.values()],
                value='Singapore',
                placeholder='Select a Country',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6"),

        html.Div([
            html.Label("Select Sector", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='sector-select1c',
                options=[{'label': name, 'value': code} for code, name in SECTOR_LABELS.items()],
                value='bec_1',
                placeholder="Select sector",
                searchable=True,
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6")
    ], className="row mb-3"),

    html.Div([
        html.Div([
            html.Label("Display Type", className="form-label fw-semibold mb-1 text-center w-100"),
            daq.ToggleSwitch(
                id='toggle-display1c',
                label='Volume / Percentage Share',
                value=True,
                className="mb-2",
                size=60
            )
        ], className="col-md-6 d-flex flex-column align-items-center"),
        html.Div([
            html.Label("Trade Type", className="form-label fw-semibold mb-1 text-center w-100"),
            dbc.ButtonGroup([
                dbc.Button("Trade Volume", id='btn-total1c', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc'}),
                dbc.Button("Exports", id='btn-export1c', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc'}),
                dbc.Button("Imports", id='btn-import1c', n_clicks=0, outline=True, size='sm', color='primary', style={'border': '1px solid #ccc'})
            ], className='w-100')
        ], className="col-md-6")
    ], className="row mb-4"),

    dcc.Tabs(id="module1c-tabs", value="historical", children=[
        dcc.Tab(label="Historical", value="historical"),
        dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1c", disabled=True),
    ]),

    html.Div(id="module1c-tab-content", className="mt-3"),

    html.Div([
        html.Div(id='country-title1c'),
        dcc.Graph(id='country-treemap1c', style={'display': 'none'}),
        dcc.Graph(id='country-bar1c', style={'display': 'none'})
    ])
])

# --- CALLBACKS ---
app = get_app()

@app.callback(
    Output("module1c-tab-content", "children"),
    Input("module1c-tabs", "value")
)
def render_tab_content(tab):
    return html.Div([
        html.Div(style={'marginTop': '20px'}),
        html.H5(id='country-title1c', className="text-center mb-2"),
        dcc.Graph(id='country-treemap1c', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
        dcc.Graph(id='country-bar1c', config={'displayModeBar': False}, style={"backgroundColor": "white"})
    ])

@app.callback(
    Output('country-treemap1c', 'style'),
    Output('country-bar1c', 'style'),
    Input('display-type1c', 'data')
)
def toggle_graph_visibility(display_type):
    if display_type == 'percentage':
        return {'display': 'block'}, {'display': 'none'}
    return {'display': 'none'}, {'display': 'block'}

@app.callback(
    Output('display-type1c', 'data'),
    Input('toggle-display1c', 'value')
)
def update_display_type(value):
    return 'percentage' if value else 'volume'

@app.callback(
    Output('trade-type-select1c', 'data'),
    Output('btn-total1c', 'color'),
    Output('btn-export1c', 'color'),
    Output('btn-import1c', 'color'),
    Input('btn-total1c', 'n_clicks'),
    Input('btn-export1c', 'n_clicks'),
    Input('btn-import1c', 'n_clicks'),
    prevent_initial_call=True
)
def update_trade_type(n_total, n_export, n_import):
    ctx = callback_context.triggered_id
    if ctx == 'btn-total1c':
        return 'total', 'primary', 'secondary', 'secondary'
    elif ctx == 'btn-export1c':
        return 'export', 'secondary', 'primary', 'secondary'
    elif ctx == 'btn-import1c':
        return 'import', 'secondary', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("prediction-tab1c", "disabled"),
    Input("input-uploaded", "data")
)
def toggle_prediction_tab(uploaded):
    return not uploaded

@app.callback(
    Output("module1c-tabs", "value"),
    Input("input-uploaded", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(uploaded):
    if uploaded:
        return "prediction"
    return dash.no_update

@app.callback(
    Output('country-treemap1c', 'figure'),
    Output('country-bar1c', 'figure'),
    Output('sector-select1c', 'options'),
    Output('country-title1c', 'children'),
    Input('country-select1c', 'value'),
    Input('trade-type-select1c', 'data'),
    Input('sector-select1c', 'value'),
    Input('module1c-tabs', 'value'),
    State('forecast-data', 'data')
)
def update_all_visualizations(selected_country, trade_type, selected_sector, tab, forecast_data):
    if tab == 'prediction':
        if not forecast_data:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        prediction_df = pd.DataFrame(forecast_data)

        if "scenario" in prediction_df.columns:
            prediction_df = prediction_df[prediction_df["scenario"] == "postshock"].drop(columns=["scenario"])

        prediction_df["year"] = pd.to_numeric(prediction_df["year"], errors='coerce')

        df_combined = pd.concat([df_raw, prediction_df], ignore_index=True)

        forecast_year = df_combined["year"].max()
        prev_year = df_combined[df_combined["year"] < forecast_year]["year"].max()
        data_source = df_combined[df_combined["year"].isin([forecast_year, prev_year])].copy()
    else:
        forecast_year = df_raw["year"].max()
        prev_year = df_raw[df_raw["year"] < forecast_year]["year"].max()
        data_source = df


    country_id = COUNTRY_NAMES[selected_country]
    filtered = data_source[data_source['country_a'] == country_id].copy()
    filtered['partner_country'] = filtered['country_b'].map(COUNTRY_LABELS)

    if selected_sector is None:
        return dash.no_update, dash.no_update, [{'label': v, 'value': k} for k, v in SECTOR_LABELS.items()], dash.no_update

    if trade_type == 'export':
        col = f"{selected_sector}_export_A_to_B"
    elif trade_type == 'import':
        col = f"{selected_sector}_import_A_from_B"
    else:
        col_export = f"{selected_sector}_export_A_to_B"
        col_import = f"{selected_sector}_import_A_from_B"
        filtered['trade_value'] = filtered[col_export] + filtered[col_import]
        col = 'trade_value'

    #latest_year = filtered['year'].max()
    latest_year = forecast_year
    prev_year = filtered['year'][filtered['year'] < latest_year].max()

    latest = filtered[filtered['year'] == latest_year]
    previous = filtered[filtered['year'] == prev_year]

    agg = latest.groupby('partner_country')[col].sum().reset_index(name='volume')
    prev_agg = previous.groupby('partner_country')[col].sum().reset_index(name='previous_volume')
    sector_agg = pd.merge(agg, prev_agg, on='partner_country', how='outer').fillna(0)

    sector_agg['percentage'] = 100 * sector_agg['volume'] / sector_agg['volume'].sum()
    sector_agg['previous_pct'] = 100 * sector_agg['previous_volume'] / sector_agg['previous_volume'].sum()
    sector_agg['change'] = sector_agg['percentage'] - sector_agg['previous_pct']
    sector_agg['change_clipped'] = sector_agg['change'].clip(-50, 50)
    sector_agg['change_str'] = sector_agg['change'].apply(lambda x: f"{x:+.2f}%")
    sector_agg['previous_pct_str'] = sector_agg['previous_pct'].round(1).astype(str) + '%'

    display_trade_type = "Trade Volume" if trade_type == "total" else trade_type.capitalize()
    is_prediction = tab == "prediction"
    title_prefix = "Predicted " if is_prediction else ""
    title_suffix = f"for {forecast_year}" if is_prediction else f"in {latest_year}"
    title = f"{title_prefix}{display_trade_type} from {selected_country} by Partner Country ({SECTOR_LABELS[selected_sector]}) {title_suffix}"

    hover_template = (
        '<b>%{label}</b><br>'
        'Current Share (' + str(latest_year) + '): %{customdata[0]:.1f}%<br>'
        'Previous Share (' + str(prev_year) + '): %{customdata[1]}<br>'
        'Change in Share: %{customdata[2]}'
    )

    fig_treemap = px.treemap(
        sector_agg, path=['partner_country'], values='percentage', color='change_clipped',
        color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
        range_color=[-50, 50],
        custom_data=['percentage', 'previous_pct_str', 'change_str']
    )
    fig_treemap.update_traces(
        hovertemplate=hover_template,
        texttemplate='<b>%{label}</b><br>%{customdata[0]:.1f}% (%{customdata[2]})'
    )
    fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

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

    fig_bar = generate_bar_chart(sector_agg, 'partner_country', 'volume', 'previous_volume', latest_year, prev_year)

    return fig_treemap, fig_bar, [{'label': v, 'value': k} for k, v in SECTOR_LABELS.items()], title


sidebar_controls = html.Div([])
