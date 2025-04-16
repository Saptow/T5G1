from dash import dcc, html, Input, Output, State, callback_context, get_app, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go

data = pd.read_csv('FBIC_sentiment_comtrade_un.csv') 

# Convert to DataFrame
df = pd.DataFrame(data)
df= df.rename(columns= {"exportsallgoodatob_alldata": "Exports", "importsallgoodafromb_alldata": 
                        "Imports", "totaltradeawithb": "Total Trade", "year": "Year", "iso3a": "CountryA", 
                        "iso3b": "CountryB", "IdealPointDistance": "Geopolitical Distance"})
df = df[["CountryA","CountryB", "Year", "Exports", "Imports", "Total Trade", "Geopolitical Distance"]]
df.drop(df[df['Year'] == 2024].index, inplace=True)

# List of years
years = sorted(df['Year'].unique())

# Compute the average geopolitical distance
#avg_geopolitical_distance = df["Geopolitical Distance"].mean()

df["Trade Balance"] = df["Exports"] - df["Imports"]

# Generate Surplus/Deficit Label
df["Balance of Trade"] = df["Trade Balance"].apply(lambda x: "Surplus" if x > 0 else "Deficit")

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

# Get unique list of countries from both A and B
COUNTRY_LIST = sorted(set(df['CountryA'].unique()) | set(df['CountryB'].unique()))
COUNTRY_LIST = sorted(COUNTRY_LABELS.values())

df['CountryA'] = df['CountryA'].map(COUNTRY_LABELS)
df['CountryB'] = df['CountryB'].map(COUNTRY_LABELS)

# Generate Surplus/Deficit Label
df["Balance of Trade"] = df["Trade Balance"].apply(lambda x: "Surplus" if x > 0 else "Deficit")

app = get_app()

# Layout
layout = html.Div([
    html.H2("How have geopolitical relations and trade dependence between economies evolved over time?"),

    html.H5("Explore how an economy's trade flow with its trading partner has changed with respect to their geopolitical distance."),

    html.Div([

    dbc.Row([
    dbc.Col([
        html.Label("Select Economy:", className="fw-semibold mb-1"),
        dcc.Dropdown(
            id="reporter-selector",
            options=[{"label": c, "value": c} for c in COUNTRY_LIST],
            value="Singapore",
            className="mb-3",
            clearable=False
        )
    ], width=6),  # Adjust width if needed

    dbc.Col([
        html.Label("Select Trading Partner:", className="fw-semibold mb-1"),
        dcc.Dropdown(
            id="partner-selector",
            options=[{"label": c, "value": c} for c in COUNTRY_LIST],
            value="Hong Kong",
            className="mb-3",
            clearable=False
        )
    ], width=6)], 
    className="mb-3"),


    # html.Label("Select Reporter Country:", className="fw-bold"),
    # dcc.Dropdown(
    #     id="reporter-selector",
    #     options=[{"label": c, "value": c} for c in COUNTRY_LIST],
    #     value="Singapore",
    #     style={"width": "300px"}
    # ),

    # html.Label("Select a Country:", className="fw-bold mt-3"),
    # dcc.Dropdown(
    #     id="partner-selector",
    #     options=[{"label": c, "value": c} for c in COUNTRY_LIST],
    #     value="China",  # default
    #     style={"width": "300px"}
    #     ),

    html.Label("Select Direction of Trade:", className="mb-3"),
    dbc.ButtonGroup([
        dbc.Button("Total Trade", id="btn-total4b", n_clicks=0, color="primary", outline=True),
        dbc.Button("Exports", id="btn-export4b", n_clicks=0, outline=True),
        dbc.Button("Imports", id="btn-import4b", n_clicks=0, outline=True)
    ], className="mb-3"),

    dcc.Store(id="selected-trade-type", data="total")
    ]),

    html.Div(id="tab-warning4a", className="text-danger mb-2 text-center"),

    dcc.Tabs(id="module4b-tabs", value="historical", children=[
         dcc.Tab(label="Historical", value="historical"),
         dcc.Tab(label="Prediction", value="prediction", id="prediction-tab4b", disabled=True),
     ]),
    
    html.Div(id="module4b-tabs-container"),

    html.Div(id="module4b-tab-content", className="mt-3"),
    # === Hidden dummy components to make Dash recognize outputs ===
    html.Div([
        html.Div(id='sector-title4b', style={'display': 'none'}),
        dcc.Graph(id='geo-trade-chart', style={'display': 'none'}),
    ], style={'display': 'none'})

])

    #dcc.Graph(id="geo-trade-chart", style={"height": "600px"}),
# , className="p-4")

# Callback
@app.callback(
    Output("selected-trade-type", "data"),
    Output("btn-total4b", "color"),
    Output("btn-export4b", "color"),
    Output("btn-import4b", "color"),
    Input("btn-total4b", "n_clicks"),
    Input("btn-export4b", "n_clicks"),
    Input("btn-import4b", "n_clicks")
)
def update_trade_type(n_total, n_export, n_import):
    triggered = ctx.triggered_id
    if triggered == "btn-export4b":
        return "export", "secondary", "primary", "secondary"
    elif triggered == "btn-import4b":
        return "import", "secondary", "secondary", "primary"
    else:
        return "total", "primary", "secondary", "secondary"

# Callback
@app.callback(
    Output("geo-trade-chart", "figure"),
    Input("reporter-selector", "value"),
    Input("partner-selector", "value"),
    Input("selected-trade-type", "data")
)
def update_geo_trade_chart(reporter, partner, trade_type):
    filtered_df = df[(df["CountryA"] == reporter)].copy()

    # Determine correct column to use
    if trade_type == "export":
        trade_col = "Exports"
    elif trade_type == "import":
        trade_col = "Imports"
    else:
        trade_col = "Total Trade"

    # Total trade for reporter across all partners by year
    total_trade_by_year = (
        filtered_df.groupby("Year")[trade_col].sum()
        .rename("total")
        .reset_index()
    )

    # Trade with specific partner
    partner_df = filtered_df[filtered_df["CountryB"] == partner]
    trade_by_partner = partner_df.groupby("Year")[trade_col].sum().rename("partner").reset_index()

    # Merge for percentage
    combined = pd.merge(trade_by_partner, total_trade_by_year, on="Year", how="left")
    combined["percentage"] = 100 * combined["partner"] / combined["total"].replace(0, 1)

    # Compute avg geopolitical distance over time
    geo_avg_df = filtered_df.groupby("Year")["Geopolitical Distance"].mean().reset_index()
    geo_partner_df = partner_df.groupby("Year")["Geopolitical Distance"].mean().reset_index()

    # filtered_df = df[(df["CountryA"] == reporter) & (df["CountryB"] == partner)]

    # # Compute reporter's average geopolitical distance with all partners for each year
    # avg_geo_df = df[df["CountryA"] == reporter].groupby("Year")["Geopolitical Distance"].mean().reset_index()

    # Dynamic Y-axis ranges
    geo_min = min(geo_avg_df["Geopolitical Distance"].min(), geo_partner_df["Geopolitical Distance"].min())
    geo_max = max(geo_avg_df["Geopolitical Distance"].max(), geo_partner_df["Geopolitical Distance"].max())

    trade_min = combined["percentage"].min()
    trade_max = combined["percentage"].max()

    # Padding Y-axis
    geo_range = [geo_min - 0.1, geo_max + 0.1]
    trade_range = [trade_min * 0.9, trade_max * 1.1]

    if filtered_df.empty:
        return go.Figure().update_layout(
            title="No data available for the selected country pair.",
            template="plotly_white"
        )

    # Prepare custom data for hover text
    #customdata = combined[["Geopolitical Distance","Exports", "Imports", "Trade Balance"]].values

    fig = go.Figure()

    # Bar for Total Trade (right Y-axis)
    fig.add_trace(go.Bar(
        x=combined["Year"],
        y=combined["percentage"],
        name=f"{partner}'s Share of {reporter}'s {trade_col}",
        marker_color="blue",
        opacity=0.5,
        yaxis="y2",
        hovertemplate=(
        "Trade Share: %{y:.2f}%<extra></extra>"
        )
        #customdata=customdata,
        # hovertemplate=(
        #     "Geopolitical Distance: %{customdata[0]}<br>" +
        #     "Total Trade: %{y}<br>" +
        #     "Exports: %{customdata[1]}<br>" +
        #     "Imports: %{customdata[2]}<br>" +
        #     "Trade Balance: %{customdata[3]}<extra></extra>"
        # )
    ))

    # Line for Geopolitical Distance (left Y-axis)
    fig.add_trace(go.Scatter(
        x=geo_partner_df["Year"],
        y=geo_partner_df["Geopolitical Distance"],
        name=f"Geopolitical Distance with {partner}",
        mode="lines+markers",
        marker=dict(color="black"),
        line=dict(width=3, color="black"),
        yaxis="y1",
        hovertemplate="Geopolitical Distance with Partner: %{y:.2f}<extra></extra>"
        # hovertemplate=(
        #     "Geopolitical Distance: %{customdata[0]}<br>" +
        #     "Total Trade: %{y}<br>" +
        #     "Exports: %{customdata[1]}<br>" +
        #     "Imports: %{customdata[2]}<br>" +
        #     "Trade Balance: %{customdata[3]}<extra></extra>"
        # )
    ))

    # Add average geopolitical distance line for reporter
    fig.add_trace(go.Scatter(
        x=geo_avg_df["Year"],
        y=geo_avg_df["Geopolitical Distance"],
        name=f"{reporter}'s Average Geopolitical Distance",
        mode="lines",
        line=dict(width=2, color="gray", dash="dash"),
        yaxis="y1",
        hovertemplate="Reporter's Average Geopolitical Distance: %{y:.2f}<extra></extra>"
        # hovertemplate=(
        # f"{reporter}'s Avg Geo Distance: " + "%{y:.3f} (All Partners)<extra></extra>"
        # )
    ))

    # Layout
    fig.update_layout(
        hovermode='x unified',
        barmode="overlay",
        template="plotly_white",
        title=f"{partner}'s Share of {reporter}'s {trade_col} and Geopolitical Distance Over Time",
        xaxis=dict(title="Year", dtick = 1),
        yaxis=dict(
            title="Geopolitical Distance",
            range=geo_range
        ),
        yaxis2=dict(
            title="Percentage Share of Trade (%)",
            overlaying="y",
            side="right",
            range=trade_range
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100, b=60, l=60, r=60)
    )

    return fig


@app.callback(
    Output("prediction-tab4b", "disabled"),
    Input("input-uploaded", "data"),
    #prevent_initial_call=True
)
def toggle_prediction_tab(uploaded):
    return not uploaded

@app.callback(
    Output("module4b-tabs", "value"),
    Input("input-uploaded", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(uploaded):
    if uploaded:
        return "prediction"
    return dash.no_update

@app.callback(
    Output("module4b-tab-content", "children"),
    Input("module4b-tabs", "value")
)
def render_tab_content(tab):
    if tab == "historical":
        return html.Div([
            html.Div(style={'marginTop': '20px'}),
            html.H5(id="sector-title4b", className="text-center mb-2"),
            dcc.Graph(id='geo-trade-chart', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
        ])
    elif tab == "prediction":
        return html.Div([
            html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
            html.P("This will show trade predictions based on uploaded news input.", className="text-center")
        ])
    

# Topbar Controls (should only be visible when module is selected) 

sidebar_controls = html.Div([
    # html.Label("Select a Country:", className="fw-bold"),
    #     dcc.Dropdown(
    #         id="country-selector",
    #         options=[{"label": c, "value": c} for c in sorted(df["Country"].unique())],
    #         value="Germany",  # default
    #         style={"width": "300px"}
    #     ),
    ], className="mb-4"),
    
        