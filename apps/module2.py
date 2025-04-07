from dash import Dash, dcc, html, Input, Output, State, callback_context, get_app
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash

# Load and prepare data
df = pd.read_csv("priscilla_worldmap_data.csv")
df["Net Exports"] = df["Export Volume"] - df["Import Volume"]

years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())
sectors = sorted(df['Sector'].unique())

country_iso = df[['Country', 'Country Code']].drop_duplicates().set_index('Country').to_dict()['Country Code']
iso_to_country = {v: k for k, v in country_iso.items()}

layout = html.Div([
    html.H2("Singapore Total Trade Volume Map Viewer", style={"margin": "20px"}),

    html.Div([
        html.Div([
            html.Label("Select Base Year:"),
            dcc.Dropdown(
                id='base-year',
                options=[{'label': str(y), 'value': y} for y in years],
                value=2022,
                style={"width": "250px"}
            )
        ], style={"display": "flex", "flexDirection": "column"}),

        html.Div([
            html.Label("Select Year to Compare (Optional):"),
            dcc.Dropdown(
                id='compare-year',
                options=[{'label': str(y), 'value': y} for y in years],
                placeholder="Show base year if left empty",
                style={"width": "250px"}
            )
        ], style={"display": "flex", "flexDirection": "column"}),

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
        ], style={"display": "flex", "flexDirection": "column"}),

        html.Div([
            html.Label("Top N Range (optional):"),
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
        ], style={"width": "400px", "paddingTop": "10px"})
    ], style={"display": "flex", "gap": "25px", "flexWrap": "wrap", "margin": "10px"}),

    html.Div([
        html.Label("Select Sectors:"),
        dcc.Dropdown(
            id='sector-filter',
            options=[{'label': s, 'value': s} for s in sectors],
            value=sectors,
            multi=True,
            className="mb-3"
        ),

        html.Label("Select Countries:"),
        dcc.Dropdown(
            id='country-filter',
            options=[{'label': c, 'value': c} for c in countries],
            value=[],
            multi=True,
            className="mb-3"
        )
    ], style={"padding": "0 40px"}),

    # html.Div([
    #     dcc.Graph(id='map-heatmap')
    # ]),

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
    # === Hidden dummy components to make Dash recognize outputs ===
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
        Input('topn-range-slider', 'value')
    )
    def update_map(base_year, compare_year, selected_sectors, selected_countries, metric, topn_range):
        if not base_year:
            raise PreventUpdate

        year_filter = [base_year, compare_year] if compare_year else [base_year]
        filtered = df[
            (df['Year'].isin(year_filter)) &
            (df['Sector'].isin(selected_sectors))
        ]

        grouped = filtered.groupby(['Country', 'Country Code', 'Lat', 'Lon', 'Year'])['Total Volume'].sum().reset_index()
        pivoted = grouped.pivot(index=['Country', 'Country Code', 'Lat', 'Lon'], columns='Year', values='Total Volume').reset_index()

        if compare_year:
            pivoted['Change'] = pivoted.get(compare_year, 0) - pivoted.get(base_year, 0)
            pivoted['Percent Change'] = ((pivoted.get(compare_year, 0) - pivoted.get(base_year, 0)) / pivoted.get(base_year, 1)) * 100
        else:
            pivoted['Change'] = pivoted.get(base_year, 0)
            pivoted['Percent Change'] = 0

        # Combine selected countries and top-N countries
        all_countries = set(selected_countries or [])
        topn_text = ""
        if topn_range[1] > topn_range[0]:
            start_idx = max(0, topn_range[0] - 1)
            end_idx = topn_range[1]
            top_n_df = pivoted.sort_values(metric, ascending=False).iloc[start_idx:end_idx]
            top_n = top_n_df['Country']
            all_countries.update(top_n)
            topn_text = "Top N Countries: " + ", ".join(top_n.tolist())

        pivoted = pivoted[pivoted['Country'].isin(all_countries)]

        pivoted['hover'] = pivoted.apply(
            lambda row: f"Country: {row['Country']}<br>" +
                        (f"% Change: {row['Percent Change']:.2f}%<br>" if row['Percent Change'] else '') +
                        (f"Change in Trade Volume: {row['Change']:.2f}<br>" if row['Change'] else '') +
                        f"<extra></extra>", axis=1)

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
            fig = px.line(
                country_df,
                x='Year',
                y=['Total Volume', 'Export Volume', 'Import Volume'],
                markers=True,
                title=f"{country} Trade Volume Breakdown"
            )
        else:
            melted = country_df.melt(id_vars='Year', value_vars=['Total Volume', 'Export Volume', 'Import Volume'],
                                     var_name='Metric', value_name='Value')
            fig = px.bar(
                melted,
                x='Year',
                y='Value',
                color='Metric',
                barmode='group',
                title=f"{country} Trade Volume Breakdown"
            )

        fig.update_traces(hovertemplate='Year: %{x}<br>Value: %{y:.2f} Billion SGD<extra></extra>')
        fig.update_layout(yaxis_title="Billion SGD", legend_title="Metric")

        return fig, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}

@app.callback(
    Output("prediction-tab2", "disabled"),
    Input("input-uploaded", "data"),
    #prevent_initial_call=True
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

sidebar_controls  = html.Div([])