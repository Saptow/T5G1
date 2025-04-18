# Module4a.py Bubble Chart 

from dash import dcc, html, Input, Output, State, callback_context, get_app, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Load historical data
data = pd.read_csv('FBIC_sentiment_comtrade_un.csv') 

# Convert to DataFrame
df = pd.DataFrame(data)
df= df.rename(columns= {"exportsallgoodatob_alldata": "Exports", "importsallgoodafromb_alldata": 
                        "Imports", "totaltradeawithb": "Total Trade", "year": "Year", "iso3a": "CountryA", 
                        "iso3b": "CountryB", "IdealPointDistance": "Geopolitical Distance"})
df = df[["CountryA","CountryB", "Year", "Exports", "Imports", "Total Trade", "Geopolitical Distance"]]
df.drop(df[df['Year'] == 2024].index, inplace=True)
df = df[~((df["CountryA"] == "ARE") | (df["CountryB"] == "ARE"))]

# List of years
years = sorted(df['Year'].unique())

# Compute the average geopolitical distance
#avg_geopolitical_distance = df["Geopolitical Distance"].mean()

df["Trade Balance"] = df["Exports"] - df["Imports"]

# Generate Surplus/Deficit Label
df["Balance of Trade"] = df["Trade Balance"].apply(lambda x: "Surplus" if x > 0 else "Deficit")

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

# Get unique list of countries from both A and B
COUNTRY_LIST = sorted(set(df['CountryA'].unique()) | set(df['CountryB'].unique()))
COUNTRY_LIST = sorted(COUNTRY_LABELS.values())

df['CountryA'] = df['CountryA'].map(COUNTRY_LABELS)
df['CountryB'] = df['CountryB'].map(COUNTRY_LABELS)

# Generate Surplus/Deficit Label
df["Balance of Trade"] = df["Trade Balance"].apply(lambda x: "Surplus" if x > 0 else "Deficit")

# === Placeholder for future prediction data ===
df_pred = None

# CHANGED
app = get_app()

def get_filtered_countries(df, reporter_country, num_countries, order, metric, selected_year):
    global df_pred
    df = pd.concat([df, df_pred]) if df_pred is not None else df
    
    df = df[(df["CountryA"] == reporter_country) & (df["Year"] == selected_year)].copy()
    df = df.rename(columns={"CountryB": "Country"})

    if order == "smallest":
        return df.nsmallest(num_countries, "Geopolitical Distance")["Country"].tolist()
    elif order == "largest":
        if metric == "Geopolitical Distance":
            return df.nlargest(num_countries, "Geopolitical Distance")["Country"].tolist()
        elif metric == "Trade Deficit":
            return df.nsmallest(num_countries, "Trade Balance")["Country"].tolist()
        elif metric == "Trade Surplus":
            return df.nlargest(num_countries, "Trade Balance")["Country"].tolist()
    return []



# === Main Layout (Graph only) ===
layout = html.Div([

    # Title
    html.H1(
        "Geopolitical Distance vs Trade Balance by Year",  
        className="mb-4 text-center"
    ),

    # Description box
    html.Div(
        html.H6(
            """
            Explore how an economy’s trade balance and geopolitical alignment vary across its different trading partners. 
            This visualisation assesses alignment based on annual UN voting records, following the methodology of Bailey et al. (2017). 
            Each country’s political stance is estimated yearly, and the geopolitical distance reflects how closely aligned two countries are—greater distance indicates less alignment. 
            Use the chart to examine how political proximity correlates with trade surplus or deficit across top trading partners. Important Note: Geopolitical distance values in the 
            predicted visualisations are based on the latest available scores from 2023 and are not forecasted.
            """,
            style={
                'color': '#333333',
                'fontSize': '16px',
                'fontFamily': 'Lato, sans-serif',
                'lineHeight': '1.4',
                'marginBottom': '24px'
            }
        ),
        className="mb-4"
    ),

    # Year selector + Economy & Partner dropdowns + Slider
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{"label": str(year), "value": year} for year in years],
            value=max(years),
            clearable=False,
            style={"width": "100%"},
            className="mb-3"
        ),

        html.Div([
            html.Div([
                html.Label("Select Economy:"),
                dcc.Dropdown(
                    id='reporter-selector',
                    options=[{'label': c, 'value': c} for c in sorted(df["CountryA"].unique())],
                    value="Singapore",
                    clearable=False,
                    style={"width": "100%"}
                )
            ], className="me-3", style={"width": "49%", "display": "inline-block"}),

            html.Div([
                html.Label("Select Trading Partners:"),
                dcc.Dropdown(
                    id='country-selector',
                    options=[{'label': c, 'value': c} for c in sorted(df["CountryB"].unique())],
                    multi=True,
                    value=["China", "United States", "Malaysia", "Indonesia", "South Korea"],
                    style={"width": "100%"}
                )
            ], style={"width": "49%", "display": "inline-block"}),
        ], className="mb-3"),

        html.Label(
            "Move slider to select the top N trading partners to be visualised below "
            "(Clear the Select Trading Partners filter first):"
        ),
        dcc.Slider(
            id='num-countries',
            min=0, max=10, step=1, value=0,
            marks={i: str(i) for i in range(11)},
            tooltip={"placement": "bottom", "always_visible": True},
            className="mb-4"
        ),
    ]),

    # Buttons row
    dbc.Row([
        dbc.Col(
            html.Div([
                html.Label("Select Magnitude:", className="me-2"),
                dbc.ButtonGroup([
                    dbc.Button("Smallest", id="btn-smallest", n_clicks=0, color="secondary", outline=True),
                    dbc.Button("Largest", id="btn-largest", n_clicks=0, color="primary", outline=True)
                ], id="order-btn-group")
            ]),
            width=6
        ),

        dbc.Col(
            html.Div([
                # label + buttons on one line
                html.Div([
                    html.Label("Select Category:", className="me-2"),
                    dbc.ButtonGroup(
                        [
                            dbc.Button("Geopolitical Distance", id="btn-distance", n_clicks=0, color="primary", outline=True),
                            dbc.Button("Trade Surplus",           id="btn-surplus",  n_clicks=0, color="secondary", outline=True),
                            dbc.Button("Trade Deficit",           id="btn-deficit",  n_clicks=0, color="secondary", outline=True),
                        ],
                        id="metric-btn-group",
                        className="me-2"
                    ),
                ], className="d-flex align-items-center"),

                # note moved below, with top margin
                html.Small(
                    "Category is fixed to 'Geopolitical Distance' when order is 'Smallest'",
                    className="d-block text-muted fst-italic mt-2 ms-2"
                )
            ]),
            width=6
        ),
    ]),

    # Hidden Stores & Tabs & Placeholder graph
    dcc.Store(id='order-selector', data='largest'),
    dcc.Store(id='metric-selector', data='Geopolitical Distance'),

    html.Div(id="tab-warning4a", className="text-danger mb-2 text-center"),

    dcc.Tabs(
        id="module4a-tabs",
        value="historical",
        children=[
            dcc.Tab(label="Historical", value="historical"),
            dcc.Tab(label="Prediction",  value="prediction", id="prediction-tab4a", disabled=True),
        ]
    ),

    html.Div(id="module4a-tabs-container"),
    html.Div(id="module4a-tab-content", className="mt-3"),

    # Dummy Div to satisfy hidden callbacks
    html.Div([
        html.Div(id='sector-title4a', style={'display': 'none'}),
        dcc.Graph(id='trade-graph',    style={'display': 'none'}),
    ], style={'display': 'none'})

])


### Callback to fix trade metric to Geopolitical Distance when smallest is chosen
@app.callback(
    Output("order-selector", "data"),
    Output("btn-smallest", "color"),
    Output("btn-largest", "color"),
    Output("metric-selector", "data"),
    Output("btn-distance", "color"),
    Output("btn-surplus", "color"),
    Output("btn-deficit", "color"),
    Output("btn-distance", "disabled"),
    Output("btn-surplus", "disabled"),
    Output("btn-deficit", "disabled"),
    Input("btn-smallest", "n_clicks"),
    Input("btn-largest", "n_clicks"),
    Input("btn-distance", "n_clicks"),
    Input("btn-surplus", "n_clicks"),
    Input("btn-deficit", "n_clicks"),
)
def update_order_and_metric(n_smallest, n_largest, n_distance, n_surplus, n_deficit):
    ctx = dash.callback_context.triggered_id

    if ctx == "btn-smallest":
        return (
            "smallest", "primary", "secondary", 
            "Geopolitical Distance",
            "primary", "secondary", "secondary",  # button colors
            True, True, True  # all metric buttons disabled
        )
    elif ctx == "btn-largest":
        return (
            "largest", "secondary", "primary", 
            dash.no_update,
            dash.no_update, dash.no_update, dash.no_update,
            False, False, False  # enable buttons
        )

    # Metric button interactions only apply when order is "largest"
    if ctx == "btn-distance":
        return dash.no_update, dash.no_update, dash.no_update, "Geopolitical Distance", "primary", "secondary", "secondary", dash.no_update, dash.no_update, dash.no_update
    elif ctx == "btn-surplus":
        return dash.no_update, dash.no_update, dash.no_update, "Trade Surplus", "secondary", "primary", "secondary", dash.no_update, dash.no_update, dash.no_update
    elif ctx == "btn-deficit":
        return dash.no_update, dash.no_update, dash.no_update, "Trade Deficit", "secondary", "secondary", "primary", dash.no_update, dash.no_update, dash.no_update

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('trade-graph', 'figure'),
    Input('reporter-selector', 'value'),
    Input('country-selector', 'value'),
    Input('num-countries', 'value'),
    Input('order-selector', 'data'),
    Input('metric-selector', 'data'),
    Input('year-dropdown', 'value')
)

def update_graph(reporter_country, selected_countries, num_countries, order, metric, selected_year):
    global df_pred
    selected_countries = set(selected_countries or [])
    filtered_countries = set(get_filtered_countries(df, reporter_country, num_countries, order, metric, selected_year))
    countries_to_display = selected_countries.union(filtered_countries)

    # If 2026 involved and df_pred exists → merge both
    current_df = pd.concat([df, df_pred]) if df_pred is not None else df

    # Filter by reporter country
    filtered_df = current_df[current_df["CountryA"] == reporter_country]

    # Then filter by selected partner countries
    filtered_df = filtered_df[filtered_df["CountryB"].isin(countries_to_display)]
    year_df = filtered_df[filtered_df['Year'] == selected_year]
    year_df["Trade Balance"] = year_df["Trade Balance"].round(2)

    # Dynamic Y-Axis (Geopolitical Distance)
    geo_min = min(year_df["Geopolitical Distance"].min(), filtered_df["Geopolitical Distance"].min())
    geo_max = max(year_df["Geopolitical Distance"].max(), filtered_df["Geopolitical Distance"].max())
    geo_padding = (geo_max - geo_min) * 0.2 if geo_max > geo_min else 0.5  # fallback padding

    y_range = [geo_min - geo_padding, geo_max + geo_padding]

    # Dynamic X-Axis (Trade Balance or Share)
    x_min = year_df["Trade Balance"].min()
    x_max = year_df["Trade Balance"].max()
    x_padding = (x_max - x_min) * 0.2 if x_max > x_min else abs(x_max) * 0.2 or 1  # fallback padding

    x_range = [x_min - x_padding, x_max + x_padding]

    # Convert values to billions and round to 2 decimal places
    year_df["Total Trade (S$ Bil)"] = (year_df["Total Trade"] / 1e9).round(2)
    year_df["Exports (S$ Bil)"] = (year_df["Exports"] / 1e9).round(2)
    year_df["Imports (S$ Bil)"] = (year_df["Imports"] / 1e9).round(2)


    fig = px.scatter(
        year_df,
        x="Trade Balance",
        y="Geopolitical Distance",
        size="Total Trade",
        color="CountryB",
        hover_data={
            "CountryB": False,
            "Total Trade" : False,
            "Total Trade (S$ Bil)": ":.2f",
            "Exports (S$ Bil)": ":.2f",
            "Imports (S$ Bil)": ":.2f",
            "Balance of Trade": True,
            "Geopolitical Distance": ":.2f"
        },
        text="CountryB",
        labels={
            "Trade Balance": "Trade Balance (S$ Bil)",
            "Geopolitical Distance": "Geopolitical Distance"
        },
        title=f"{reporter_country}'s Trade vs. Geopolitical Distance in {selected_year}",
        height=600,
        size_max=50
    )

    # Second scatter plot: Bubble size independent of total trade to show trade balance more clearly
    fig.add_trace(
        go.Scatter(
            x=year_df["Trade Balance"],
            y=year_df["Geopolitical Distance"],
            mode="markers",
            marker=dict(
                size=10,  # Set fixed size
                color="white",
                opacity=0.8,
            ),
            showlegend= False,
        )
    )

    # Add a vertical reference line at x = 0 to separate surplus/deficit regions
    fig.add_vline(x=0, line_dash="dash", line_color="gray")

    # Add a horizontal reference line at the average geopolitical distance
    fig.add_hline(y=filtered_df["Geopolitical Distance"].mean(), line_dash="dot", line_color="gray", 
              annotation_text=f"{reporter_country}'s Average Geopolitical Distance", annotation_position="top right")

    # Add annotation for Trade Deficit
    fig.add_annotation(
        showarrow=False,
        text="Trade Deficit",
        font=dict(size=13, color="red"),
        textangle=0,
        xref='paper',
        x=0.01,
        yref='paper',
        y=-0.06
    )

    # Add annotation for Trade Surplus
    fig.add_annotation(
        showarrow=False,
        text="Trade Surplus",
        font=dict(size=13, color="green"),
        textangle=0,
        xref='paper',
        x=0.99,
        yref='paper',
        y=-0.06
    )

    fig.add_annotation(
        xref = 'paper',
        x = .1,
        yref = 'paper',
        y = 1.05,
        text = "Bubble size: Reporter’s total trade value with trading partner. " \
        "White circle: Reporter’s trade balance with the trading partner.",
        showarrow=False,
        font=dict(size=14),
        bgcolor="white"
    )

    # Add background color for Trade Deficit region (x < 0)
    fig.add_shape(
        type="rect",
        x0=x_range[0], x1=0,
        y0=0, y1=1,
        yref="paper",  # use full height of plot
        # x0=min(0,year_df["Trade Balance"].min()*1.25), x1=0,
        # y0=0, y1=year_df["Geopolitical Distance"].max()+ 0.5,
        fillcolor="rgba(255, 102, 102, 0.2)",  # Light red with transparency
        layer="below",
        line_width=0
    )

    # Add background color for Trade Surplus region (x > 0)
    fig.add_shape(
        type="rect",
        x0=0, x1=x_range[1],
        y0=0, y1=1,
        yref="paper",
        # x0=0, x1=max(0,year_df["Trade Balance"].max()*1.35),
        # y0=0, y1=year_df["Geopolitical Distance"].max()+0.5,
        fillcolor="rgba(102, 204, 102, 0.2)",  # Light green with transparency
        layer="below",
        line_width=0
    )

    # Add annotation for "Closer Politically" (below average distance)
    fig.add_annotation(
        showarrow=False,
        text="Closer politically",
        font=dict(size=13),
        textangle=-90,
        xref='paper',
        x=-0.045,
        yref='paper',
        y=.02
    )
    
    # Add annotation for "Further Politically" (above average distance)
    fig.add_annotation(
        showarrow=False,
        text="Further politically",
        font=dict(size=13),
        textangle=-90,
        xref='paper',
        x=-0.045,
        yref='paper',
        y=1.01
    )
    
    # Customize layout
    fig.update_traces(
        textposition="top center",
    )
    
    fig.update_layout(
    width=1250,
    height=700,
    xaxis=dict(
        title=dict(text="Trade Balance (S$ Bil)", font=dict(size=18)),
        range=x_range
    ),
    yaxis=dict(
        title=dict(text="Geopolitical Distance", font=dict(size=18)),
        range=y_range
    ),
    plot_bgcolor="white",
    showlegend=False
    )

    return fig

@app.callback(
    Output("prediction-tab4a", "disabled"),
    Output("year-dropdown", "options"),
    Output("year-dropdown", "value"),
    Input("forecast-data", "data"),  # Changed from "input-uploaded" to "forecast-data"
    prevent_initial_call=True
)
def handle_prediction_upload(forecast_data):
    global df_pred, years
    
    # Return early if no forecast data
    if not forecast_data:
        return True, [{"label": str(year), "value": year} for year in years], max(years)
        
    try:
        # Process the API response data instead of reading from CSV
        prediction_df = pd.DataFrame(forecast_data)
        
        # Keep only postshock scenario if that field exists
        if "scenario" in prediction_df.columns:
            prediction_df = prediction_df[prediction_df["scenario"] == "postshock"].drop(columns=["scenario"])
        
        # Ensure year is numeric
        if "year" in prediction_df.columns:
            prediction_df['year'] = pd.to_numeric(prediction_df['year'], errors='coerce')
        
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

        # Rename columns to match historical data format
        column_mapping = {
            "country_a": "CountryA",
            "country_b": "CountryB",
            "year": "Year",
            "total_import_of_A_from_B": "Imports",
            "trade_volume": "Total Trade",
            "total_export_of_A_to_B": "Exports"
        }
        
        # Only rename columns that exist
        cols_to_rename = {k: v for k, v in column_mapping.items() if k in prediction_df.columns}
        prediction_df.rename(columns=cols_to_rename, inplace=True)
        
        # Map country codes to full names
        if "CountryA" in prediction_df.columns:
            prediction_df['CountryA'] = prediction_df['CountryA'].map(COUNTRY_LABELS)
        if "CountryB" in prediction_df.columns:
            prediction_df['CountryB'] = prediction_df['CountryB'].map(COUNTRY_LABELS)
        
        # Calculate trade balance
        if "Exports" in prediction_df.columns and "Imports" in prediction_df.columns:
            prediction_df["Trade Balance"] = prediction_df["Exports"] - prediction_df["Imports"]
            prediction_df["Balance of Trade"] = prediction_df["Trade Balance"].apply(lambda x: "Surplus" if x > 0 else "Deficit")
        
        # Get 2023 geopolitical distance from historical data
        geo_2023 = df[df['Year'] == 2023][['CountryA', 'CountryB', 'Geopolitical Distance']]
        
        # Merge predicted data with 2023 geo distance
        df_pred = prediction_df.merge(geo_2023, on=['CountryA', 'CountryB'], how='left')
        
        # Update dropdown options with new year(s)
        updated_years = sorted(set(df['Year'].unique()).union(df_pred['Year'].unique()))
        options = [{'label': str(y), 'value': y} for y in updated_years]
        
        return False, options, max(updated_years)
        
    except Exception as e:
        print(f"Error processing forecast data: {e}")
        return True, [{"label": str(year), "value": year} for year in years], max(years)


@app.callback(
    Output("module4a-tabs", "value"),
    Input("forecast-data", "data"),  
    prevent_initial_call=True
)
def switch_to_prediction_tab(forecast_data):
    if forecast_data:
        return "prediction"
    return dash.no_update
@app.callback(
    Output("module4a-tab-content", "children"),
    Input("module4a-tabs", "value")
)
def render_tab_content(tab):
    global df_pred

    if tab == "historical":
        return html.Div([
            html.Div(style={'marginTop': '20px'}),
            html.H5(id="sector-title4a", className="text-center mb-2"),
            dcc.Graph(id='trade-graph', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
        ])
    elif tab == "prediction":
        return html.Div([
            html.Div(style={'marginTop': '20px'}),
            html.H5(id="sector-title4a", className="text-center mb-2"),
            dcc.Graph(id='trade-graph', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
            # html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
            # html.P("This will show trade predictions based on uploaded news input.", className="text-center")
        ])

# # Load prediction data
# prediction_df = pd.read_csv("sample_2026.csv")
# prediction_df = prediction_df[prediction_df["scenario"] == "postshock"].drop(columns=["scenario"])
# prediction_df['year'] = pd.to_numeric(prediction_df['year'], errors='coerce')

# @app.callback(
#     Output("prediction-tab4a", "disabled"),
#     Input("input-uploaded", "data")
# )
# def toggle_prediction_tab(uploaded):
#     return not uploaded

# @app.callback(
#     Output("module4a-subtabs7abc", "children"),
#     Output("module4a-subtabs7abc", "value"),
#     Input("module4a-tabs", "value")
# )
# def toggle_subtab_visibility(main_tab):
#     if main_tab == "historical":
#         return "historical-bar7abc"
#     else:
#         return "prediction-bar7abc"

# @app.callback(
#     Output("module4a-tabs", "value"),
#     Input("input-uploaded", "data"),
#     prevent_initial_call=True
# )
# def switch_to_prediction_tab(uploaded):
#     if uploaded:
#         return "prediction"
#     return dash.no_update

# Merge historical and prediction data
# df_combined_all = pd.concat([df_raw, prediction_df], ignore_index=True)
# df_raw['year'] = pd.to_numeric(df_raw['year'], errors='coerce')

# layout = html.Div([
#     html.H1("Singapore's Trade Balance vs Geopolitical Distance in 2022"),
    
#     dcc.Dropdown(
#         id='country-selector',
#         options=[{'label': country, 'value': country} for country in sorted(df["Country"].unique())],
#         multi=True,
#         placeholder="Select countries to display",
#         value=["China", "Malaysia", "United States", "Indonesia", "South Korea", "Japan", "Thailand", "Australia", "Vietnam", "India"]  # Default countries
#     ),

#     html.Div([
#         html.Span("View the"),
#         dcc.Dropdown(
#             id='num-countries',
#             options=[{'label': str(i), 'value': i} for i in [5, 10]],
#             value='-',
#             clearable=True,
#             style={"width": "80px", "display": "inline-block", "vertical-align": "middle"}
#         ),
#         html.Span("countries that Singapore has the"),
#         dcc.Dropdown(
#             id='order-selector',
#             options=[
#             {'label': "smallest", 'value': "smallest"},
#             {'label': "largest", 'value': "largest"}],
#             value='-',
#             clearable=True,
#             style={"width": "120px", "display": "inline-block", "vertical-align": "middle"}
#         ),
#         dcc.Dropdown(
#             id='metric-selector',
#             options=[
#                 {'label': "geopolitical distance", 'value': "Absolute_ideal_point_distance"},
#                 {'label': "trade deficit", 'value': "Trade Deficit"},
#                 {'label': "trade surplus", 'value': "Trade Surplus"}],
#             value='-',
#             clearable=True,
#             style={"width": "180px", "display": "inline-block", "vertical-align": "middle"}
#         ),
#         html.Span(" with", style={"font-size": "18px"})
#     ], style={"display": "flex", "align-items": "center", "gap": "5px"}),

#     dcc.Graph(id='trade-graph')
# ])

# === Sidebar Controls for Module 3 ===
sidebar_controls = html.Div([
    # html.H5("Trade Distance Filters", className="text-muted mb-3"),

    # html.Label("Select Year:"),
    # dcc.Dropdown(
    #     id='year-dropdown',
    #     options=[{"label": str(year), "value": year} for year in years],
    #     value=max(years),  # Default to the most recent year
    #     clearable=False,
    #     style={"width": "100%"},
    #     className="mb-3"
    # ),

    # html.Label("Select Countries:"),
    # dcc.Dropdown(
    #     id='country-selector',
    #     options=[{'label': country, 'value': country} for country in sorted(df["Country"].unique())],
    #     multi=True,
    #     style={"color": "black", "backgroundColor": "white"},
    #     value=["China", "USA", "Indonesia", "Germany", "India"],
    #     className="mb-3"
    # ),

    # html.Label("View Top N Countries:"),
    # dcc.Dropdown(
    #     id='num-countries',
    #     options=[{'label': str(i), 'value': i} for i in [5, 10]],
    #     style={"color": "black", "backgroundColor": "white"},
    #     clearable=True,
    #     className="mb-3"
    # ),

    # html.Label("Trade Order Criterion:"),
    # dcc.Dropdown(
    #     id='order-selector',
    #     options=[
    #         {'label': "smallest", 'value': "smallest"},
    #         {'label': "largest", 'value': "largest"}
    #     ],
    #     style={"color": "black", "backgroundColor": "white"},
    #     clearable=True,
    #     className="mb-3"
    # ),

    # html.Label("Trade Metric:"),
    # dcc.Dropdown(
    #     id='metric-selector',
    #     options=[
    #         {'label': "geopolitical distance", 'value': "Absolute_ideal_point_distance"},
    #         {'label': "trade deficit", 'value': "Trade Deficit"},
    #         {'label': "trade surplus", 'value': "Trade Surplus"}
    #     ],
    #     style={"color": "black", "backgroundColor": "white"},
    #     clearable=True,
    #     className="mb-3"
    # )
])

# def render_tab_content(tab):
#     if tab == "historical":
#         return html.Div([
#             html.Div(style={'marginTop': '20px'}),
#             html.H5(id='sector-title1b', className="text-center mb-2"),
#             dcc.Graph(id='sector-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
#             html.H5(id='country-title1b', className="text-center mb-2"),
#             dcc.Graph(id='country-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white"})
#         ])
#     elif tab == "prediction":
#         return html.Div([
#             html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
#             html.P("This will show trade predictions based on uploaded news input.", className="text-center")
#         ])
