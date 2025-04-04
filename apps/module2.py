# module2.py , Trade World Map

from dash import dcc, html, Input, Output, State, callback_context, get_app, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Load data from CSV 
df = pd.read_csv("priscilla_worldmap_data.csv")

# Static data for dropdowns 
years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())
sectors = sorted(df['Sector'].unique())

# Mapping from ISO3 to Country Name 
country_iso = df[['Country', 'Country Code']].drop_duplicates().set_index('Country').to_dict()['Country Code']
iso_to_country = {v: k for k, v in country_iso.items()}

app = get_app()
app.title = "Singapore Trade Intensity Map"



# layout = html.Div([
#     html.H2("Singapore Total Trade Volume Map Viewer"),

#     html.Label("Select Year Range:"),
#     dcc.RangeSlider(
#         id='year-range', min=min(years), max=max(years), value=[2022, 2024],
#         marks={str(year): str(year) for year in years}, step=1
#     ),

#     html.Label("Select Sectors:"),
#     dcc.Dropdown(
#         id='sector-filter',
#         options=[{'label': sector, 'value': sector} for sector in sectors],
#         value=sectors, multi=True
#     ),

#     html.Label("Select Countries:"),
#     dcc.Dropdown(
#         id='country-filter',
#         options=[{'label': country, 'value': country} for country in countries],
#         value=countries, multi=True
#     ),

#     html.Div([
#         html.Label("Top N Countries by Trade Volume:"),
#         dcc.Input(id='top-n', type='number', min=1, step=1, placeholder='(optional)'),
#     ], style={'margin-bottom': '10px'}),

#     html.Div([
#         html.Label("Metric:"),
#         dcc.Dropdown(
#             id='metric-toggle',
#             options=[
#                 {'label': 'Total Trade Volume', 'value': 'Avg_Trade_Volume'},
#                 {'label': '% Change from Base Year', 'value': '% Change from Base'}
#             ],
#             value='Avg_Trade_Volume'
#         )
#     ]),

#     html.Div(id='main-graph-container', children=[
#         dcc.Graph(id='map-heatmap'),
#         dcc.Graph(id='country-trend', style={'display': 'none'}),
#         html.Button("Return to map", id="close-button", n_clicks=0,
#                     style={'display': 'none', 'position': 'fixed', 'top': '10px', 'right': '10px', 'zIndex': '9999'})
#     ]),
# ])

# === Sidebar Controls for Module 2 ===
sidebar_controls = html.Div([
    html.H5("Trade Map Filters", className="text-muted mb-3"),

    html.Label("Select Year Range:"),
    dcc.RangeSlider(
        id='year-range', min=min(years), max=max(years), value=[2022, 2024],
        marks={str(year): str(year) for year in years}, step=1,
        className="mb-3"
    ),

    html.Label("Select Sectors:"),
    dcc.Dropdown(
        id='sector-filter',
        options=[{'label': sector, 'value': sector} for sector in sectors],
        value=sectors, multi=True, style={"color": "black", "backgroundColor": "white"}, className="mb-3"
    ),

    html.Label("Select Countries:"),
    dcc.Dropdown(
        id='country-filter',
        options=[{'label': country, 'value': country} for country in countries],
        value=countries, multi=True, style={"color": "black", "backgroundColor": "white"}, className="mb-3"
    ),

    html.Label("Top N Countries by Trade Volume:"),
    dcc.Input(id='top-n', type='number', min=1, step=1, style={"color": "black", "backgroundColor": "white"}, className="mb-3"),

    html.Label("Metric:"),
    dcc.Dropdown(
        id='metric-toggle',
        options=[
            {'label': 'Total Trade Volume', 'value': 'Avg_Trade_Volume'},
            {'label': '% Change from Base Year', 'value': '% Change from Base'}
        ],
        style={"color": "black", "backgroundColor": "white"}, className="mb-3"
    )
])

# === Main Layout (Graphs only) ===
layout = html.Div([
    html.H2("Singapore Total Trade Volume Map Viewer"),

    html.Div(id='main-graph-container', children=[
        dcc.Graph(id='map-heatmap'),
        dcc.Graph(id='country-trend', style={'display': 'none'}),
        html.Button("Return to map", id="close-button", n_clicks=0,
                    style={'display': 'none', 'position': 'fixed', 'top': '10px', 'right': '10px', 'zIndex': '9999'})
    ]),
])

def register_callbacks(app):
    @app.callback(
        Output('map-heatmap', 'figure'),
        Input('year-range', 'value'),
        Input('sector-filter', 'value'),
        Input('country-filter', 'value'),
        Input('metric-toggle', 'value'),
        Input('top-n', 'value')
    )
    def update_map(year_range, selected_sectors, selected_countries, selected_metric, top_n):
        start_year, end_year = year_range
        filtered = df[
            (df['Year'] >= start_year) & (df['Year'] <= end_year) &
            (df['Sector'].isin(selected_sectors)) & (df['Country'].isin(selected_countries))
        ]

        grouped = filtered.groupby(['Country', 'Country Code', 'Lat', 'Lon', 'Year']).agg({
            'Total Volume': 'first', 'SG GDP': 'first', 'Trade Intensity': 'first'
        }).reset_index()

        summary = grouped.groupby(['Country', 'Country Code', 'Lat', 'Lon']).agg(
            Avg_Trade_Volume=('Total Volume', 'mean'),
            Avg_GDP=('SG GDP', 'mean'),
            Avg_Intensity=('Trade Intensity', 'mean'),
            Base_Trade_Volume=('Total Volume', lambda x: x.iloc[0])
        ).reset_index()

        summary['% Change from Base'] = (
            (summary['Avg_Trade_Volume'] - summary['Base_Trade_Volume']) / summary['Base_Trade_Volume']
        ).round(4)

        summary['Hover Text'] = summary.apply(
            lambda row: f"Country: {row['Country']}<br>"
                        f"Total Volume: {row['Avg_Trade_Volume']:.2f} Billion SGD<br>"
                        f"Trade Intensity: {row['Avg_Intensity']:.2%}", axis=1
        )

        if top_n:
            summary = summary.nlargest(top_n, 'Avg_Trade_Volume')

        fig = px.choropleth(
            summary,
            locations="Country Code",
            color=selected_metric,
            hover_name="Country",
            hover_data=None,
            color_continuous_scale=['green', 'orange', 'red'],
            locationmode="ISO-3"
        )
        fig.update_traces(hovertemplate=summary['Hover Text'])
        fig.update_geos(fitbounds="locations")
        fig.update_layout(
            height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0}, mapbox_style="carto-positron"
        )
        fig.update_coloraxes(colorbar_title="Selected Metric")
        return fig

    @app.callback(
        Output('country-trend', 'figure'),
        Output('country-trend', 'style'),
        Output('map-heatmap', 'style'),
        Output('close-button', 'style'),
        Input('map-heatmap', 'clickData'),
        Input('close-button', 'n_clicks')
    )
    def toggle_country_trend(clickData, close_clicks):
        ctx = dash.callback_context
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

        fig = px.line(
            country_df,
            x='Year',
            y=['Total Volume', 'Export Volume', 'Import Volume'],
            markers=True,
            title=f"{country} Trade Volume Breakdown"
        )

        fig.update_traces(
            hovertemplate='Year: %{x}<br>Value: %{y:.2f} Billion SGD<extra></extra>'
        )
        fig.update_layout(yaxis_title="Billion SGD", legend_title="Metric")

        return fig, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}

app.layout = layout    
register_callbacks(app)
