from dash import Dash, dcc, html, Input, Output, State, callback_context, get_app
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Load and prepare data
df = pd.read_csv("priscilla_worldmap_data.csv")

years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())
sectors = sorted(df['Sector'].unique())

country_iso = df[['Country', 'Country Code']].drop_duplicates().set_index('Country').to_dict()['Country Code']
iso_to_country = {v: k for k, v in country_iso.items()}

layout = html.Div([
    html.H2("Singapore Total Trade Volume Map Viewer", style={"margin": "20px"}),

    dcc.Tabs(id="view-tabs", value='topn', children=[
        # --- Top N Countries tab ---
        dcc.Tab(label='Top N Countries', value='topn', children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.Label("Select Base Year:"),
                        dcc.Dropdown(
                            id='base-year-topn',
                            options=[{'label': str(y), 'value': y} for y in years],
                            value=2022,
                            style={"width": "250px"}
                        )
                    ], style={"display": "flex", "flexDirection": "column"}),

                    html.Div([
                        html.Label("Select Year to Compare (Optional):"),
                        dcc.Dropdown(
                            id='compare-year-topn',
                            options=[{'label': str(y), 'value': y} for y in years],
                            placeholder="Show base year if left empty",
                            style={"width": "250px"}
                        )
                    ], style={"display": "flex", "flexDirection": "column"}),

                    html.Div([
                        html.Label("Metric:"),
                        dcc.Dropdown(
                            id='metric-toggle-topn',
                            options=[
                                {'label': 'Change in Total Trade Volume', 'value': 'Change'},
                                {'label': '% Change from Base Year', 'value': 'Percent Change'}
                            ],
                            value='Change',
                            style={"width": "275px"}
                        )
                    ], style={"display": "flex", "flexDirection": "column"})
                ], style={"display": "flex", "gap": "25px", "flexWrap": "wrap", "marginTop": "5px"}),

                html.Div([
                    html.Label("Top N Range:", style={"marginTop": "15px"}),
                    dcc.RangeSlider(
                        id='topn-range-slider',
                        min=1,
                        max=len(countries),
                        value=[1, 15],
                        marks={i: str(i) for i in range(1, len(countries)+1)},
                        step=1,
                        tooltip={"placement": "bottom"}
                    )
                ], style={"marginTop": "15px"})
            ], style={"margin": "20px"})
        ]),

        # --- Customise Countries tab ---
        dcc.Tab(label='Customise Countries', value='customise', children=[
            html.Div([
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
                    ], style={"display": "flex", "flexDirection": "column"})
                ], style={"display": "flex", "gap": "25px", "flexWrap": "wrap", "marginTop": "5px"}),

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
                    value=countries,
                    multi=True,
                    className="mb-3"
                )
            ], style={"padding": "0 40px"})
        ])
    ]),

    # Map output
    html.Div([
        dcc.Graph(id='map-heatmap')
    ]),

    # Country trend view
    html.Div([
        dcc.Tabs(id='chart-tabs', value='line', children=[
            dcc.Tab(label='Line Chart', value='line'),
            dcc.Tab(label='Bar Chart', value='bar'),
        ]),
        dcc.Graph(id='country-trend')
    ], id='country-trend-container', style={'display': 'none'}),

    # Close button
    html.Button("Return to map", id="close-button", n_clicks=0,
                style={'display': 'none', 'position': 'fixed', 'top': '10px', 'right': '10px', 'zIndex': '9999',
                       "color": "black", "backgroundColor": "white"})
])


app = get_app()

# === Callback registration ===
def register_callbacks(app):
    @app.callback(
        Output('map-heatmap', 'figure'),
        Input('view-tabs', 'value'),
        Input('base-year', 'value'),
        Input('compare-year', 'value'),
        Input('sector-filter', 'value'),
        Input('country-filter', 'value'),
        Input('metric-toggle', 'value'),
        Input('base-year-topn', 'value'),
        Input('compare-year-topn', 'value'),
        Input('metric-toggle-topn', 'value'),
        Input('topn-range-slider', 'value')
    )
    def update_map(view_tab, base_year, compare_year, selected_sectors, selected_countries, metric, 
                   base_year_topn, compare_year_topn, metric_topn, topn_range):

        if view_tab == 'customise':
            if not base_year:
                raise PreventUpdate

            filtered = df[
                (df['Year'].isin([base_year, compare_year] if compare_year else [base_year])) &
                (df['Sector'].isin(selected_sectors)) &
                (df['Country'].isin(selected_countries))
            ]
            selected_metric = metric
        else:
            if not base_year_topn:
                raise PreventUpdate

            filtered = df[
                (df['Year'].isin([base_year_topn, compare_year_topn] if compare_year_topn else [base_year_topn]))
            ]
            selected_metric = metric_topn

        grouped = filtered.groupby(['Country', 'Country Code', 'Lat', 'Lon', 'Year'])['Total Volume'].sum().reset_index()
        pivoted = grouped.pivot(index=['Country', 'Country Code', 'Lat', 'Lon'], columns='Year', values='Total Volume').reset_index()

        if view_tab == 'customise':
            if compare_year:
                pivoted['Change'] = pivoted.get(compare_year, 0) - pivoted.get(base_year, 0)
                pivoted['Percent Change'] = ((pivoted.get(compare_year, 0) - pivoted.get(base_year, 0)) / pivoted.get(base_year, 1)) * 100
            else:
                pivoted['Change'] = pivoted.get(base_year, 0)
                pivoted['Percent Change'] = 0
        else:
            if compare_year_topn:
                pivoted['Change'] = pivoted.get(compare_year_topn, 0) - pivoted.get(base_year_topn, 0)
                pivoted['Percent Change'] = ((pivoted.get(compare_year_topn, 0) - pivoted.get(base_year_topn, 0)) / pivoted.get(base_year_topn, 1)) * 100
            else:
                pivoted['Change'] = pivoted.get(base_year_topn, 0)
                pivoted['Percent Change'] = 0

        pivoted['hover'] = pivoted.apply(
            lambda row: f"Country: {row['Country']}<br>" +
                        (f"% Change: {row['Percent Change']:.2f}%<br>" if row['Percent Change'] else '') +
                        (f"Change in Trade Volume: {row['Change']:.2f}<br>" if row['Change'] else '') +
                        f"<extra></extra>", axis=1)

        country_list = ""
        if view_tab == 'topn':
            sort_col = 'Change' if selected_metric == 'Change' else 'Percent Change'
            pivoted = pivoted.sort_values(sort_col, ascending=False)
            pivoted = pivoted.iloc[topn_range[0]-1:topn_range[1]]
            country_list = html.Ul([html.Li(c) for c in pivoted['Country']])

        fig = px.choropleth(
            pivoted,
            locations="Country Code",
            color=selected_metric,
            locationmode="ISO-3",
            color_continuous_scale=['red', 'orange', 'green'],
            custom_data=['hover']
        )
        fig.update_traces(hovertemplate='%{customdata[0]}')
        fig.update_geos(fitbounds="locations")
        fig.update_layout(height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0})
        fig.update_coloraxes(colorbar_title=selected_metric)

        return fig

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

app.layout = layout
register_callbacks(app)
