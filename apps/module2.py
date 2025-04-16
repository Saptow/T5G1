from dash import Dash, dcc, html, Input, Output, State, callback_context, get_app
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash
import dash_daq as daq

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

# === Set up dropdown values ===
years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())
sectors = sorted(df['Sector'].unique())

country_iso = df[['Country', 'Country Code']].drop_duplicates().set_index('Country').to_dict()['Country Code']
iso_to_country = {v: k for k, v in country_iso.items()}

layout = html.Div([
    html.H2("Singapore Total Trade Volume Map Viewer", style={"margin": "20px"}),

    html.Div([  # Wrapper for rows

        # Row 1 – Switch on far left, followed by dropdowns
        html.Div([
            html.Div([
                html.Label("Year Mode:"),
                html.Div([
                    html.Span("Base Year Only", style={"marginRight": "10px"}),
                    daq.BooleanSwitch(
                        id='compare-toggle',
                        on=False,
                        color="#000000"
                    ),
                    html.Span("Compare Years", style={"marginLeft": "10px"})
                ], style={"display": "flex", "alignItems": "center", "gap": "10px"})
            ]),

            html.Div([
                html.Label("Select Base Year:"),
                dcc.Dropdown(
                    id='base-year',
                    options=[{'label': str(y), 'value': y} for y in years],
                    value=2022,
                    style={"width": "250px"}
                )
            ]),

            html.Div([
                html.Label("Select Year to Compare:"),
                dcc.Dropdown(
                    id='compare-year',
                    options=[{'label': str(y), 'value': y} for y in years],
                    placeholder="",
                    style={"width": "250px"}
                )
            ], id='compare-year-container', style={"display": "none"}),

            html.Div([
                html.Label("Metric:"),
                dcc.Dropdown(
                    id='metric-toggle',
                    options=[
                        {'label': 'Change in Total Trade Volume', 'value': 'Change'},
                        {'label': '% Change from Base Year', 'value': 'Percent Change'}
                    ],
                    value='Change',
                    style={"width": "275px"}
                )
            ], id='metric-container', style={"display": "none"})
        ], style={"display": "flex", "gap": "25px", "flexWrap": "wrap", "marginBottom": "20px"}),

        # Row 2 – Country Filter Mode, Top N / Countries, Sector
        html.Div([
            html.Div([
                html.Label("Country Mode:"),
                html.Div([
                    html.Span("Custom Countries", style={"marginRight": "10px"}),
                    daq.BooleanSwitch(
                        id='use-topn-toggle',
                        on=True,
                        color="#000000"
                    ),
                    html.Span("Top N", style={"marginLeft": "10px"})
                ], style={"display": "flex", "alignItems": "center", "gap": "10px"})
            ]),

            html.Div([
                html.Label("Top N Range:"),
                dcc.RangeSlider(
                    id='topn-range-slider',
                    min=0,
                    max=len(countries),
                    value=[0, 0],
                    marks={i: str(i) for i in range(0, len(countries)+1)},
                    step=1,
                    tooltip={"placement": "bottom"}
                ),
                html.Div(id="topn-preview", style={"marginTop": "10px", "fontSize": "14px", "color": "#555"})
            ], id="topn-container", style={"width": "400px", "paddingTop": "10px", "display": "block"}),

            html.Div([
                html.Label("Select Countries:"),
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
        ], style={"display": "flex", "gap": "25px", "flexWrap": "wrap"})
    ], style={"margin": "20px"}),  # Close wrapper

    html.Div([
        dcc.Tabs(id='chart-tabs', value='line', children=[
            dcc.Tab(label='Line Chart', value='line'),
            dcc.Tab(label='Bar Chart', value='bar'),
        ]),
        dcc.Graph(id='country-trend')
    ], id='country-trend-container', style={'display': 'none'}),

    html.Button("Return to map", id="close-button", n_clicks=0,
                style={'display': 'none', 'position': 'fixed', 'top': '10px', 'right': '10px', 'zIndex': '9999',
                       "color": "black", "backgroundColor": "white"}),

    html.Div(id="tab-warning2", className="text-danger mb-2 text-center"),

    dcc.Tabs(id="module2-tabs", value="historical", children=[
        dcc.Tab(label="Historical", value="historical"),
        dcc.Tab(label="Prediction", value="prediction", id="prediction-tab4a", disabled=True),
    ]),

    html.Div(id="module2-tabs-container"),
    html.Div(id="module2-tab-content", className="mt-3"),

    html.Div([
        html.Div(id='sector-title2', style={'display': 'none'}),
        dcc.Graph(id='map-heatmap', style={'display': 'none'}),
    ], style={'display': 'none'})
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
        Input('topn-range-slider', 'value'),
        Input('use-topn-toggle', 'on'),
        Input('compare-toggle', 'on')
    )
    def update_map(base_year, compare_year, selected_sectors, selected_countries, metric, topn_range, use_topn, compare_on):
        if not base_year:
            raise PreventUpdate

        year_filter = [base_year, compare_year] if compare_year else [base_year]
        filtered = df[
            (df['Year'].isin(year_filter)) &
            (df['Sector'].isin(selected_sectors))
        ]

        grouped = filtered.groupby(['Country', 'Country Code', 'Lat', 'Lon', 'Year'])['Total Volume'].sum().reset_index()
        pivoted = grouped.pivot(index=['Country', 'Country Code', 'Lat', 'Lon'], columns='Year', values='Total Volume').reset_index()

        if not compare_on:
            pivoted['Change'] = pivoted.get(base_year, 0)
            pivoted['Percent Change'] = 0
            metric = 'Change'
        else:
            if compare_year:
                pivoted['Change'] = pivoted.get(compare_year, 0) - pivoted.get(base_year, 0)
                pivoted['Percent Change'] = (
                    (pivoted.get(compare_year, 0) - pivoted.get(base_year, 0)) / pivoted.get(base_year, 1)
                ) * 100
            else:
                pivoted['Change'] = pivoted.get(base_year, 0)
                pivoted['Percent Change'] = 0

        all_countries = set(selected_countries or [])
        topn_text = ""
        if topn_range[1] > topn_range[0]:
            start_idx = max(0, topn_range[0] - 1)
            end_idx = topn_range[1]
            top_n_df = pivoted.sort_values(metric, ascending=False).iloc[start_idx:end_idx]
            top_n = top_n_df['Country']
            if use_topn:
                all_countries.update(top_n)
            topn_text = "Top N Countries: " + ", ".join(top_n.tolist())

        pivoted = pivoted[pivoted['Country'].isin(all_countries)]

        pivoted['hover'] = pivoted.apply(
            lambda row: (
                f"Country: {row['Country']}<br>" +
                (f"Total Trade Volume: {row['Change']:.2f}<br>" if not compare_on else "") +
                (f"% Change: {row['Percent Change']:.2f}%<br>" if compare_on else "") +
                (f"Change in Trade Volume: {row['Change']:.2f}<br>" if compare_on else "") +
                "<extra></extra>"
            ), axis=1
        )

        fig = px.choropleth(
            pivoted,
            locations="Country Code",
            color=metric,
            locationmode="ISO-3",
            color_continuous_scale=['red', 'orange', 'green'],
            custom_data=['hover']
        )
        fig.update_traces(hovertemplate='%{customdata[0]}')
        fig.update_geos(fitbounds="locations")
        fig.update_layout(height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0})
        fig.update_coloraxes(colorbar_title=metric)

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
        Output('map-heatmap', 'style'),
        Output('close-button', 'style'),
        Input('map-heatmap', 'clickData'),
        Input('close-button', 'n_clicks'),
        Input('chart-tabs', 'value')
    )
    def toggle_country_trend(clickData, close_clicks, chart_type):
        ctx = callback_context
        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'close-button.n_clicks':
            return px.line(title=""), {'display': 'none'}, {'display': 'block'}, {'display': 'none'}

        if not clickData:
            return px.line(title="Click on a country to see its trends"), {'display': 'none'}, {'display': 'block'}, {'display': 'none'}

        iso = clickData['points'][0].get('location')
        if not iso or iso not in iso_to_country:
            return px.line(title="Click on a country to see its trends"), {'display': 'none'}, {'display': 'block'}, {'display': 'none'}

        country = iso_to_country[iso]
        country_df = df[df['Country'] == country].groupby('Year').agg({
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

        return fig, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}

@app.callback(
    Output("prediction-tab2", "disabled"),
    Input("input-uploaded", "data"),
)
def toggle_prediction_tab(uploaded):
    return not uploaded

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
    if tab == "historical":
        return html.Div([
            html.Div(style={'marginTop': '20px'}),
            html.H5(id="sector-title2", className="text-center mb-2"),
            dcc.Graph(id='map-heatmap', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
        ])
    elif tab == "prediction":
        return html.Div([
            html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
            html.P("This will show trade predictions based on uploaded news input.", className="text-center")
        ])

app.layout = layout
register_callbacks(app)

sidebar_controls = html.Div([])
