from dash import html, dcc, Input, Output, callback, ALL, ctx
import dash
import pandas as pd
import plotly.graph_objects as go

# === Load data ===
df = pd.read_csv("sample_trade_data_2015_2024_2026_FIXED.csv")

# === Define sectors ===
sectors = sorted(df["Sector Group"].unique())

# === Percentage calculation helper ===
def calculate_percentages(data, group_by):
    grouped = data.groupby(group_by, as_index=False).agg({
        'Total Trade Volume': 'sum'
    })
    total = grouped['Total Trade Volume'].sum()
    grouped['percentage'] = 100 * grouped['Total Trade Volume'] / total if total else 0
    return grouped

# === Placeholder Sidebar Controls ===
sidebar_controls = html.Div([])

# === Dash Layout ===
layout = html.Div([
    html.H2("Module 1B: Yearly percentage share of sectors", className="mb-4"),

    html.Div([
        html.Label("Select a Country", className="form-label fw-semibold mb-1"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': c, 'value': c} for c in sorted(df['Reporter'].unique())],
            value=sorted(df['Reporter'].unique())[0],
            placeholder="Select a country",
            className="mb-3",
            style={"maxWidth": "400px"}
        )
    ], className="mb-4"),

    html.Div([
        html.Div([
            html.Button(sector, id={'type': 'sector-btn', 'index': sector},
                        n_clicks=0, className='btn btn-outline-primary m-1')
            for sector in sectors
        ], className="d-flex flex-wrap justify-content-center")
    ], className="mb-4"),

    dcc.Graph(id='module1b-graph')
])

# === Callback ===
@callback(
    Output('module1b-graph', 'figure'),
    Input('country-dropdown', 'value'),
    Input({'type': 'sector-btn', 'index': ALL}, 'n_clicks')
)
def update_graph(selected_country, n_clicks_list):
    # Determine selected sector
    triggered_id = ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'sector-btn':
        selected_sector = triggered_id['index']
    else:
        selected_sector = sectors[0]

    # Filter dataset
    filtered = df[(df['Reporter'] == selected_country) & (df['Sector Group'] == selected_sector)]
    filtered = filtered[filtered['Year'].between(2015, 2024)]

    # Calculate percentages for each year
    grouped = filtered.groupby('Year', as_index=False).agg({'Total Trade Volume': 'sum'})
    total_trade = filtered['Total Trade Volume'].sum()
    grouped['percentage'] = 100 * grouped['Total Trade Volume'] / total_trade if total_trade else 0
    grouped['gap'] = 100 - grouped['percentage']

    # Calculate year-over-year change in percentage
    grouped['change'] = grouped['percentage'].diff().fillna(0).round(1)

    max_y = min(100, grouped['percentage'].max() * 2)

    # Create stacked bars: grey gap first, blue actual percentage on top
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=grouped['Year'],
        y=grouped['percentage'],
        marker_color='#00BFC4',
        width=0.3,
        name='',
        text=grouped['percentage'].round(1).astype(str) + '%',
        textposition='outside',
        textangle=0,
        textfont=dict(color='black', size=12),
        hovertemplate='%{y:.1f}%<br>Change: %{customdata[0]:+.1f}%',
        customdata=grouped[['change']].values,
        showlegend=False
    ))

    fig.add_trace(go.Bar(
        x=grouped['Year'],
        y=max_y - grouped['percentage'],
        marker_color='lightgrey',
        width=0.3,
        name='',
        hoverinfo='skip',
        showlegend=False
    ))

    fig.update_layout(
        title=f"% of Total Trade in {selected_sector} for {selected_country} 2015-2024",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(
            range=[0, max_y],
            showgrid=False,
            zeroline=False
        ),
        xaxis=dict(
            tickmode='linear',
            tick0=2015,
            dtick=1,
            showgrid=False
        ),
        barmode='stack',
        bargap=0.5,
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly_white',
        showlegend=False
    )

    return fig
