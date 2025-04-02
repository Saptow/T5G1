import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import os

# === Load Pre-generated Data ===
csv_path = "generated_trade_data_with_country_code.csv"
df = pd.read_csv(csv_path)

# Ensure proper types
df['Year'] = df['Year'].astype(int)
df['Total Volume'] = df['Total Volume'].astype(float)
df['Import Volume'] = df['Import Volume'].astype(float)
df['Export Volume'] = df['Export Volume'].astype(float)

# Extract distinct values for controls
years = sorted(df['Year'].unique())
countries = sorted(df['Country'].unique())
sectors = sorted(df['Sector'].unique())

country_iso = {
    'China': 'CHN', 'USA': 'USA', 'Malaysia': 'MYS', 'Indonesia': 'IDN', 'Germany': 'DEU',
    'India': 'IND', 'Vietnam': 'VNM', 'Australia': 'AUS', 'Japan': 'JPN', 'UK': 'GBR',
    'France': 'FRA', 'Brazil': 'BRA', 'South Korea': 'KOR', 'Mexico': 'MEX', 'Russia': 'RUS',
    'Canada': 'CAN', 'Italy': 'ITA', 'Spain': 'ESP', 'Thailand': 'THA', 'Netherlands': 'NLD'
}

app = dash.Dash(__name__)
app.title = "Singapore Trade Intensity Map"

app.layout = html.Div([
    html.H2("Singapore Total Trade Volume Map Viewer"),

    html.Label("Select Year Range:"),
    dcc.RangeSlider(
        id='year-range', min=min(years), max=max(years), value=[2022, 2024],
        marks={str(year): str(year) for year in years}, step=1
    ),

    html.Label("Select Sectors:"),
    dcc.Dropdown(
        id='sector-filter',
        options=[{'label': sector, 'value': sector} for sector in sectors],
        value=sectors, multi=True
    ),

    html.Label("Select Countries:"),
    dcc.Dropdown(
        id='country-filter',
        options=[{'label': country, 'value': country} for country in countries],
        value=countries, multi=True
    ),

    html.Div([
        html.Label("Top N Countries by Trade Volume:"),
        dcc.Input(id='top-n', type='number', min=1, step=1, placeholder='(optional)'),
    ], style={'margin-bottom': '10px'}),

    html.Div([
        html.Label("Metric:"),
        dcc.Dropdown(
            id='metric-toggle',
            options=[
                {'label': 'Total Trade Volume', 'value': 'Avg_Trade_Volume'},
                {'label': '% Change from Base Year', 'value': '% Change from Base'}
            ],
            value='Avg_Trade_Volume'
        )
    ]),

    html.Div(id='main-graph-container', children=[
        dcc.Graph(id='map-heatmap'),
        dcc.Graph(id='country-trend', style={'display': 'none'}),
        html.Button("Return to map", id="close-button", n_clicks=0, style={'display': 'none', 'position': 'fixed', 'top': '10px', 'right': '10px', 'zIndex': '9999'})
    ]),
])

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
    Output('close
