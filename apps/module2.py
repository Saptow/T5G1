from dash import Dash, dcc, html, Input, Output, State, callback_context, get_app
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash
import dash_daq as daq
import pycountry

# === Load and clean data ===
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

COUNTRY_COORDS = {
    "ARE": (23.4241, 53.8478),
    "AUS": (-25.2744, 133.7751),
    "CHE": (46.8182, 8.2275),
    "CHN": (35.8617, 104.1954),
    "DEU": (51.1657, 10.4515),
    "FRA": (46.6034, 1.8883),
    "HKG": (22.3193, 114.1694),
    "IDN": (-0.7893, 113.9213),
    "IND": (20.5937, 78.9629),
    "JPN": (36.2048, 138.2529),
    "KOR": (35.9078, 127.7669),
    "MYS": (4.2105, 101.9758),
    "NLD": (52.1326, 5.2913),
    "PHL": (12.8797, 121.7740),
    "SGP": (1.3521, 103.8198),
    "THA": (15.8700, 100.9925),
    "USA": (37.0902, -95.7129),
    "VNM": (14.0583, 108.2772)
}

df_raw = pd.read_csv("data/final/historical_data.csv")
df_raw['Country Code'] = df_raw['country_b']
df_raw['Country'] = df_raw['Country Code'].apply(lambda code: pycountry.countries.get(alpha_3=code).name if pycountry.countries.get(alpha_3=code) else code)
df_raw['Year'] = df_raw['year']
df_raw['Lat'] = df_raw['Country Code'].map(lambda code: COUNTRY_COORDS.get(code, (None, None))[0])
df_raw['Lon'] = df_raw['Country Code'].map(lambda code: COUNTRY_COORDS.get(code, (None, None))[1])

records = []
for sector, name in SECTOR_LABELS.items():
    export_col = f"{sector}_export_A_to_B"
    import_col = f"{sector}_import_A_from_B"
    temp = df_raw[['Year', 'Country', 'Country Code', 'Lat', 'Lon', export_col, import_col]].copy()
    temp['Sector'] = name
    temp['Export Volume'] = temp[export_col]
    temp['Import Volume'] = temp[import_col]
    temp['Total Volume'] = temp['Export Volume'] + temp['Import Volume']
    records.append(temp[['Year', 'Country', 'Country Code', 'Lat', 'Lon', 'Sector', 'Export Volume', 'Import Volume', 'Total Volume']])

df = pd.concat(records, ignore_index=True)
df["Net Exports"] = df["Export Volume"] - df["Import Volume"]
# === Placeholder for future prediction data ===
df_pred = None

# === Set up dropdown values ===
years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())
sectors = sorted(df['Sector'].unique())

country_iso = df[['Country', 'Country Code']].drop_duplicates().set_index('Country').to_dict()['Country Code']
iso_to_country = {v: k for k, v in country_iso.items()}

layout = html.Div([
    html.H1(
        "Who are Singapore's top trading partners by sector and trade value?", className="mb-4"),

    html.H5("Explore how Singapore’s trade relationships evolved over time."),

    # ==== Row 1 ====
    html.Div([
        #dcc.Store(id="input-uploaded", storage_type="session"),
        # Year Mode Toggle
        html.Div([
            html.Label("Year Filter:"),
            html.Div([
                html.Span("Select A Year", style={"marginRight": "10px"}),
                daq.BooleanSwitch(id='compare-toggle', on=True, color="#000000"),
                html.Span("Compare Across Two Years", style={"marginLeft": "10px"})
            ], style={"display": "flex", "alignItems": "center", "gap": "10px"})
        ]),

        # Base Year Dropdown
        html.Div([
            html.Label("Select Start Year:"),
            dcc.Dropdown(
                id='base-year',
                options=[{'label': str(y), 'value': y} for y in years],
                value = 2006,
                style={"width": "250px"}
            )
        ]),

        # Compare Year Dropdown
        html.Div([
            html.Label("Select End Year:"),
            dcc.Dropdown(
                id='compare-year',
                options=[{'label': str(y), 'value': y} for y in years],
                value= 2023,                
                style={"width": "250px"}
            )
        ], id='compare-year-container', style={"display": "none"}),

        # Trade Type Dropdown
        html.Div([
            html.Label("Direction of Trade:"),
            dcc.Dropdown(
                id='trade-type-dropdown',
                options=[
                    {'label': 'Total Trade', 'value': 'total'},
                    {'label': 'Exports', 'value': 'export'},
                    {'label': 'Imports', 'value': 'import'}
                ],
                value='total',
                style={"width": "250px"}
            )
        ]),

        # Metric Dropdown
        html.Div([
            html.Label("Metric:"),
            dcc.Dropdown(
                id='metric-toggle',
                options=[
                    {'label': 'Change in Trade Value', 'value': 'Change'},
                    {'label': '% Change from Base Year', 'value': 'Percent Change'}
                ],
                value='Change',
                style={"width": "275px"}
            )
        ], id='metric-container', style={"display": "none"})
    ], style={"display": "flex", "gap": "25px", "flexWrap": "wrap", "marginBottom": "20px"}),

    # ==== Row 2 ====
    html.Div([
        html.Div([
            html.Label("Economy Filter:"),
            html.Div([
                html.Span("Select Trading Partners", style={"marginRight": "10px"}),
                daq.BooleanSwitch(id='use-topn-toggle', on=True, color="#000000"),
                html.Span("Filter by Top N", style={"marginLeft": "10px"})
            ], style={"display": "flex", "alignItems": "center", "gap": "10px"})
        ]),

        html.Div([
            html.Label("Move slider to select the top N trading partners to be visualised below:"),
            dcc.RangeSlider(
                id='topn-range-slider',
                min=0,
                max=len(countries),
                value=[0, 5],
                marks={i: str(i) for i in range(0, len(countries)+1)},
                step=1,
                tooltip={"placement": "bottom"}
            ),
            html.Div(id="topn-preview", style={"marginTop": "10px", "fontSize": "14px", "color": "#555"})
        ], id="topn-container", style={"width": "400px", "paddingTop": "10px"}),

        html.Div([
            html.Label("Select Trading Partners:"),
            dcc.Dropdown(
                id='country-filter',
                options=[{'label': c, 'value': c} for c in countries],
                value=[],
                multi=True,
                className="mb-3",
                style={"width": "600px"}
            )
        ], id="country-dropdown-container", style={"paddingBottom": "10px", "display": "none"}),

        html.Div([
            html.Label("Select Sectors:"),
            dcc.Dropdown(
                id='sector-filter',
                options=[{'label': s, 'value': s} for s in sectors],
                value=sectors,
                multi=True,
                style={"width": "600px"}
            )
        ])
    ], style={"display": "flex", "gap": "25px", "flexWrap": "wrap"}),

    # ==== Tabs ====
    html.Div([
        dcc.Tabs(id="module2-tabs", value="historical", children=[
            dcc.Tab(label="Historical", value="historical"),
            dcc.Tab(label="Prediction", value="prediction", id="prediction-tab2", disabled=True),
        ]),
        html.Div(id="module2-tabs-container"),
        html.Div(id="module2-tab-content", className="mt-3")
    ]),

    # ==== Map & Trend ====
    html.Div([
        html.Div([
            dcc.Graph(id='map-heatmap')
        ], id='map-container', style={'display': 'block'}),

        html.Div([
            dcc.Tabs(id='chart-tabs', value='line', children=[
                dcc.Tab(label='Line Chart', value='line'),
                dcc.Tab(label='Bar Chart', value='bar'),
            ]),
            dcc.Graph(id='country-trend'),
            html.Div([
                html.Button(
                    "Return to map",
                    id="close-button",
                    n_clicks=0,
                    style={
                        'marginTop': '15px',
                        'padding': '10px 20px',
                        'backgroundColor': '#f0f0f0',
                        'border': '1px solid #ccc',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold',
                        'boxShadow': '1px 1px 3px rgba(0,0,0,0.1)'
                    }
                )
            ], style={'textAlign': 'left'})
        ], id='country-trend-container', style={'display': 'none'})
    ])
])



app = get_app()

# === Callback registration ===
def register_callbacks(app):
    @app.callback(
        Output('map-heatmap', 'figure'),
        Output('topn-preview', 'children'),
        Input('base-year', 'value'),
        Input('compare-year', 'value'),
        Input('sector-filter', 'value'),
        Input('country-filter', 'value'),
        Input('metric-toggle', 'value'),
        Input('trade-type-dropdown', 'value'),
        Input('topn-range-slider', 'value'),
        Input('use-topn-toggle', 'on'),
        Input('compare-toggle', 'on')
    )
    def update_map(base_year, compare_year, selected_sectors, selected_countries, metric, trade_type, topn_range, use_topn, compare_on):
        global df_pred  # For 2026 postshock data

        if not base_year:
            raise PreventUpdate

        # Combine years
        years_used = [base_year]
        if compare_on and compare_year:
            years_used.append(compare_year)

        use_pred = 2026 in years_used
        current_df = pd.concat([df, df_pred]) if use_pred and df_pred is not None else df

        # Choose volume type
        volume_col = {
            'total': 'Total Volume',
            'export': 'Export Volume',
            'import': 'Import Volume'
        }[trade_type]

        # Filter
        filtered = current_df[
            (current_df['Year'].isin(years_used)) &
            (current_df['Sector'].isin(selected_sectors))
        ]

        grouped = filtered.groupby(['Country', 'Country Code', 'Lat', 'Lon', 'Year'])[volume_col].sum().reset_index()
        pivoted = grouped.pivot(index=['Country', 'Country Code', 'Lat', 'Lon'], columns='Year', values=volume_col).reset_index()

        # Metric calculation
        if not compare_on:
            pivoted['Change'] = pivoted.get(base_year, 0)
            pivoted['Percent Change'] = 0
            metric_used = 'Change'
        else:
            if compare_year:
                pivoted['Change'] = pivoted.get(compare_year, 0) - pivoted.get(base_year, 0)
                pivoted['Percent Change'] = (
                    (pivoted.get(compare_year, 0) - pivoted.get(base_year, 0)) / pivoted.get(base_year, 1)
                ) * 100
            else:
                pivoted['Change'] = pivoted.get(base_year, 0)
                pivoted['Percent Change'] = 0
            metric_used = metric

        # Top N logic
        all_countries = set(selected_countries or [])
        topn_text = ""
        if topn_range[1] > topn_range[0]:
            start_idx = max(0, topn_range[0] - 1)
            end_idx = topn_range[1]
            top_n_df = pivoted.sort_values(metric_used, ascending=False).iloc[start_idx:end_idx]
            top_n = top_n_df['Country']
            if use_topn:
                all_countries.update(top_n)
            topn_text = "Top N Countries: " + ", ".join(top_n.tolist())

        pivoted = pivoted[pivoted['Country'].isin(all_countries)]

        volume_label = {
            'total': 'Total Trade Volume',
            'export': 'Export Volume',
            'import': 'Import Volume'
        }[trade_type]

        pivoted['hover'] = pivoted.apply(
            lambda row: (
                f"Country: {row['Country']}<br>"
                f"{volume_label}: {row['Change']:.2f}<br>"
                + (f"% Change: {row['Percent Change']:.2f}%<br>" if compare_on else "")
                + "<i>Click on the country to see detailed trade volume breakdown over time.</i><br>"
                + "<extra></extra>"
            ), axis=1
        )


        fig = px.choropleth(
            pivoted,
            locations="Country Code",
            color=metric_used,
            locationmode="ISO-3",
            color_continuous_scale=['red', 'orange', 'green'],
            custom_data=['hover']
        )
        fig.update_traces(hovertemplate='%{customdata[0]}')
        fig.update_geos(fitbounds="locations")
        fig.update_layout(height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0})
        fig.update_coloraxes(colorbar_title=metric_used)

        return fig, topn_text


    @app.callback(
        Output('compare-year-container', 'style'),
        Output('metric-container', 'style'),
        Input('compare-toggle', 'on')
    )
    def toggle_compare_mode(compare_on):
        if compare_on:
            return {"display": "block"}, {"display": "block"}
        return {"display": "none"}, {"display": "none"}

    @app.callback(
        Output('topn-container', 'style'),
        Output('country-dropdown-container', 'style'),
        Input('use-topn-toggle', 'on')
    )
    def toggle_filter_visibility(use_topn):
        if use_topn:
            return {"width": "400px", "paddingTop": "10px", "display": "block"}, {"display": "none"}
        return {"display": "none"}, {"paddingBottom": "10px", "display": "block"}

    @app.callback(
    Output('country-trend', 'figure'),
    Output('country-trend-container', 'style'),
    Output('map-container', 'style'),
    Input('map-heatmap', 'clickData'),
    Input('close-button', 'n_clicks'),
    Input('chart-tabs', 'value')
)
    def toggle_country_trend(clickData, close_clicks, chart_type):
        ctx = callback_context

        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'close-button.n_clicks':
            return px.line(title=""), {'display': 'none'}, {'display': 'block'}

        if not clickData:
            return px.line(title="Click on a country to see its trends"), {'display': 'none'}, {'display': 'block'}

        iso = clickData['points'][0].get('location')
        if not iso or iso not in iso_to_country:
            return px.line(title="Click on a country to see its trends"), {'display': 'none'}, {'display': 'block'}

        country = iso_to_country[iso]
            
        if df_pred is not None:
            combined_df = pd.concat([df, df_pred])
        else:
            combined_df = df

        country_df = combined_df[combined_df['Country'] == country].groupby('Year').agg({
            'Total Volume': 'mean',
            'Export Volume': 'mean',
            'Import Volume': 'mean'
        }).reset_index()


        if chart_type == 'line':
            fig = px.line(country_df, x='Year', y=['Total Volume', 'Export Volume', 'Import Volume'],
                        markers=True, title=f"{country} Trade Volume Breakdown")
        else:
            melted = country_df.melt(id_vars='Year', value_vars=['Total Volume', 'Export Volume', 'Import Volume'],
                                    var_name='Metric', value_name='Value')
            fig = px.bar(melted, x='Year', y='Value', color='Metric', barmode='group',
                        title=f"{country} Trade Volume Breakdown")

        fig.update_traces(hovertemplate='Year: %{x}<br>Value: %{y:.2f} Billion SGD<extra></extra>')
        fig.update_layout(yaxis_title="Billion SGD", legend_title="Metric")

        return fig, {'display': 'block'}, {'display': 'none'}


@app.callback(
    Output("prediction-tab2", "disabled"),
    Output("base-year", "options"),
    Output("compare-year", "options"),
    Output("base-year", "value"),
    Output("compare-year", "value"),
    Output("compare-toggle", "on"),  
    Input("input-uploaded", "data"),
    State("forecast-data", "data"),  # Add this to get the forecast data from the store
    prevent_initial_call=True
)
def handle_prediction_upload(uploaded, forecast_data):
    global df_pred, years

    if not uploaded or not forecast_data:
        raise PreventUpdate

    # Convert the JSON data from the store to a DataFrame
    pred_df = pd.DataFrame.from_dict(forecast_data)
    
    # === Clean prediction data ===
    # Assuming forecast_data contains the same structure as the sample_2026.csv
    pred_df = pred_df[pred_df["scenario"] == "postshock"].copy()
    pred_df.drop(columns=["scenario"], inplace=True)

    records = []
    for sector, name in SECTOR_LABELS.items():
        export_col = f"{sector}_export_A_to_B"
        import_col = f"{sector}_import_A_from_B"
        temp = pred_df[['year', 'country_b', export_col, import_col]].copy()
        temp['Country Code'] = temp['country_b']
        temp['Country'] = temp['Country Code'].apply(lambda code: pycountry.countries.get(alpha_3=code).name if pycountry.countries.get(alpha_3=code) else code)
        temp['Year'] = temp['year']
        temp['Lat'] = temp['Country Code'].map(lambda code: COUNTRY_COORDS.get(code, (None, None))[0])
        temp['Lon'] = temp['Country Code'].map(lambda code: COUNTRY_COORDS.get(code, (None, None))[1])
        temp['Sector'] = name
        temp['Export Volume'] = temp[export_col]
        temp['Import Volume'] = temp[import_col]
        temp['Total Volume'] = temp['Export Volume'] + temp['Import Volume']
        records.append(temp[['Year', 'Country', 'Country Code', 'Lat', 'Lon', 'Sector', 'Export Volume', 'Import Volume', 'Total Volume']])

    df_pred = pd.concat(records, ignore_index=True)
    df_pred["Net Exports"] = df_pred["Export Volume"] - df_pred["Import Volume"]

    # === Update dropdown options with 2026 ===
    updated_years = sorted(set(df['Year'].unique()).union(df_pred['Year'].unique()))
    options = [{'label': str(y), 'value': y} for y in updated_years]

    return False, options, options, 2026, 2026, True

@app.callback(
    Output("module2-tabs", "value"),
    Input("input-uploaded", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(uploaded):
    if uploaded:
        return "prediction"
    return dash.no_update

@app.callback(
    Output("module2-tab-content", "children"),
    Input("module2-tabs", "value")
)
def render_tab_content(tab):
    global df_pred

def toggle_prediction_tab(uploaded):
    return not uploaded

app.layout = layout
register_callbacks(app)

sidebar_controls = html.Div([])
