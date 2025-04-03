# Module3.py Bubble Chart 

from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Retrieve data
data = pd.read_csv('GeopoliticalTrade2022_cleaned.csv') 

# Convert to DataFrame
df = pd.DataFrame(data)

# Compute the average geopolitical distance
avg_geopolitical_distance = df["Absolute_ideal_point_distance"].mean()

# Generate Surplus/Deficit Label
df["Balance of Trade"] = df["Trade Balance"].apply(lambda x: "Surplus" if x > 0 else "Deficit")

# CHANGED
app = get_app()

# Continue


def get_filtered_countries(df, num_countries, order, metric):
    """Returns a list of countries based on the filter selection."""
    if order == "smallest":
        return df.nsmallest(num_countries, "Absolute_ideal_point_distance")["Country"].tolist()
    elif order == "largest":
        if metric == "Absolute_ideal_point_distance":
            return df.nlargest(num_countries, "Absolute_ideal_point_distance")["Country"].tolist()
        elif metric == "Trade Deficit":
            return df.nsmallest(num_countries, "Trade Balance")["Country"].tolist()
        elif metric == "Trade Surplus":
            return df.nlargest(num_countries, "Trade Balance")["Country"].tolist()
    return []

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

# === Main Layout (Graph only) ===
layout = html.Div([
    html.H1("Singapore's Trade Balance vs Geopolitical Distance in 2022"),
    dcc.Graph(id='trade-graph')
])

@app.callback(
    Output('metric-selector', 'disabled'),
    Output('metric-selector', 'value'),
    Input('order-selector', 'value')
)
def update_metric_dropdown(order):
    if order == "smallest":
        return True, "Absolute_ideal_point_distance"
    return False, "-"


@app.callback(
    Output('trade-graph', 'figure'),
    Input('country-selector', 'value'),
    Input('num-countries', 'value'),
    Input('order-selector', 'value'),
    Input('metric-selector', 'value')
)

def update_graph(selected_countries, num_countries, order, metric):
    selected_countries = set(selected_countries or [])
    filtered_countries = set(get_filtered_countries(df, num_countries, order, metric))
    countries_to_display = selected_countries.union(filtered_countries)
    
    filtered_df = df[df["Country"].isin(countries_to_display)]
    
    fig = px.scatter(
        filtered_df,
        x="Trade Balance",
        y="Absolute_ideal_point_distance",
        size="Total Trade",
        color="Country",
        hover_data={"Country": True, "Exports": True, "Imports": True, "Balance of Trade": True},
        text="Country",
        labels={
            "Trade Balance": "Trade Balance (S$ Bil)",
            "Absolute_ideal_point_distance": "Geopolitical Distance"
        },
        size_max=50
    )

    # Second scatter plot: Bubble size independent of total trade to show trade balance more clearly
    fig.add_trace(
        go.Scatter(
            x=filtered_df["Trade Balance"],
            y=filtered_df["Absolute_ideal_point_distance"],
            mode="markers",
            marker=dict(
                size=10,  # Set fixed size
                color="white",
                opacity=0.8,
            ),
            showlegend= False,
        )
    )

    # Add a bubble size legend at the top-right corner
    fig.add_annotation(
        x=max(df["Trade Balance"]) + 12,  # Move it to the rightmost part
        y=max(df["Absolute_ideal_point_distance"]) + 10,  # Position at the top
        text="Circle Size: Total Trade Value",
        showarrow=False,
        font=dict(size=14, color="black"),
        bgcolor="white",
        bordercolor="black",
        borderwidth=1
    )

    # Add a vertical reference line at x = 0 to separate surplus/deficit regions
    fig.add_vline(x=0, line_dash="dash", line_color="gray")

    # Add a horizontal reference line at the average geopolitical distance
    fig.add_hline(y=avg_geopolitical_distance, line_dash="dot", line_color="gray", 
              annotation_text="Average Geopolitical Distance", annotation_position="top right")

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

    # Add background color for Trade Deficit region (x < 0)
    fig.add_shape(
        type="rect",
        x0=min(0,filtered_df["Trade Balance"].min()*1.25), x1=0,
        y0=0, y1=filtered_df["Absolute_ideal_point_distance"].max()+ 0.5,
        fillcolor="rgba(255, 102, 102, 0.2)",  # Light red with transparency
        layer="below",
        line_width=0
    )

    # Add background color for Trade Surplus region (x > 0)
    fig.add_shape(
        type="rect",
        x0=0, x1=max(0,filtered_df["Trade Balance"].max()*1.35),
        y0=0, y1=filtered_df["Absolute_ideal_point_distance"].max()+0.5,
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
        x=-0.04,
        yref='paper',
        y=.025
    )
    
    # Add annotation for "Further Politically" (above average distance)
    fig.add_annotation(
        showarrow=False,
        text="Further politically",
        font=dict(size=13),
        textangle=-90,
        xref='paper',
        x=-0.04,
        yref='paper',
        y=1.03
    )
    
    # Customize layout
    fig.update_traces(textposition="top center")
    
    fig.update_layout(
    width=1250,
    height=700,
    xaxis=dict(
        title=dict(text="Trade Balance (S$ Bil)", font=dict(size=18)),
        range=(filtered_df["Trade Balance"].min() * 1.25 , filtered_df["Trade Balance"].max()*1.25)
    ),
    yaxis=dict(
        title=dict(text="Geopolitical Distance", font=dict(size=18)),
        range=[0, filtered_df["Absolute_ideal_point_distance"].max() + 0.5]
    ),
    plot_bgcolor="white",
    showlegend=True
    )

    
    return fig

# === Sidebar Controls for Module 3 ===
sidebar_controls = html.Div([
    html.H5("Trade Distance Filters", className="text-muted mb-3"),

    html.Label("Select Countries:"),
    dcc.Dropdown(
        id='country-selector',
        options=[{'label': country, 'value': country} for country in sorted(df["Country"].unique())],
        multi=True,
        placeholder="Select countries to display",
        value=["China", "Malaysia", "United States", "Indonesia", "South Korea", "Japan", "Thailand", "Australia", "Vietnam", "India"],
        className="mb-3"
    ),

    html.Label("View Top N Countries:"),
    dcc.Dropdown(
        id='num-countries',
        options=[{'label': str(i), 'value': i} for i in [5, 10]],
        value='-',
        clearable=True,
        className="mb-3"
    ),

    html.Label("Trade Order Criterion:"),
    dcc.Dropdown(
        id='order-selector',
        options=[
            {'label': "smallest", 'value': "smallest"},
            {'label': "largest", 'value': "largest"}
        ],
        value='-',
        clearable=True,
        className="mb-3"
    ),

    html.Label("Trade Metric:"),
    dcc.Dropdown(
        id='metric-selector',
        options=[
            {'label': "geopolitical distance", 'value': "Absolute_ideal_point_distance"},
            {'label': "trade deficit", 'value': "Trade Deficit"},
            {'label': "trade surplus", 'value': "Trade Surplus"}
        ],
        value='-',
        clearable=True,
        className="mb-3"
    )
])
