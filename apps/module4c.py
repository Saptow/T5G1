from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go

# Load the dataset
df_2026 = pd.read_csv("bilateral_trade_data_2026.csv")

# Mapping for sectors
sector_labels = {
    "Sector_1": "Food and Agriculture",
    "Sector_2": "Energy and Mining",
    "Sector_3": "Construction and Housing",
    "Sector_4": "Textile and Footwear",
    "Sector_5": "Transport and Travel",
    "Sector_6": "ICT and Business",
    "Sector_7": "Health and Education",
    "Sector_8": "Government and Others"
}

# Sidebar controls
sidebar_controls = html.Div([
    html.H5("Module 4C Controls", className="text-muted mb-3"),

    dcc.Dropdown(
        id='module4c-country-dropdown',
        options=[{'label': r, 'value': r} for r in sorted(df_2026['Reporter'].unique())],
        placeholder="Select a country",
        className="mb-3"
    ),

    dcc.RadioItems(
        id='module4c-groupby-radio',
        options=[
            {'label': 'Group by Sector', 'value': 'Sector Group'},
            {'label': 'Group by Partner', 'value': 'Partner'}
        ],
        value='Sector Group',
        inline=True,
        className="mb-3"
    ),
])

# Main layout
layout = html.Div([
    html.H2("Module 4C: Impact of Shock on Forecasted Trade", className="mb-4"),
    dcc.Graph(id='module4c-graph')
])


# Utility function
def calculate_percentages(data, group_by):
    grouped = data.groupby(group_by, as_index=False).agg({
        'volume': 'sum',
        'previous_volume': 'sum'
    })
    total_current = data['volume'].sum()
    total_previous = data['previous_volume'].sum()
    grouped['percentage'] = 100 * grouped['volume'] / total_current if total_current else 0
    grouped['change'] = (
        100 * (grouped['volume'] / total_current - grouped['previous_volume'] / total_previous)
        if total_current and total_previous else 0
    )
    max_abs_change = grouped['change'].abs().max()
    dynamic_range = max(1, round(max_abs_change * 5, 2))
    grouped['change_clipped'] = grouped['change'].clip(lower=-dynamic_range, upper=dynamic_range)
    grouped['dynamic_range'] = dynamic_range
    return grouped


# Callback logic
@callback(
    Output('module4c-graph', 'figure'),
    Input('module4c-country-dropdown', 'value'),
    Input('module4c-groupby-radio', 'value')
)
def update_module4c_graph(selected_country, groupby_field):
    if not selected_country:
        return go.Figure()

    # Filter to selected country
    df = df_2026[df_2026["Reporter"] == selected_country]

    # Separate time periods
    df_a = df[df["Time Period"] == "2026a"].copy()
    df_b = df[df["Time Period"] == "2026b"].copy()

    # Rename columns for merging
    df_a = df_a.rename(columns={"Total Trade Volume": "previous_volume"})
    df_b = df_b.rename(columns={"Total Trade Volume": "volume"})

    # Merge a & b
    merged = pd.merge(
        df_a[["Reporter", groupby_field, "previous_volume"]],
        df_b[["Reporter", groupby_field, "volume"]],
        on=["Reporter", groupby_field],
        how="inner"
    )

    # Calculate percentages and changes
    agg = calculate_percentages(merged, groupby_field)

    # Labels
    agg["label"] = agg[groupby_field]
    if groupby_field == "Sector Group":
        agg["label"] = agg["label"].map(sector_labels)

    # Build scatter plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=agg["percentage"],
        y=agg["change"],
        text=agg["label"],
        mode='markers+text',
        textposition='top center',
        marker=dict(
            size=agg["percentage"],
            sizemode='area',
            sizeref=2.0 * agg["percentage"].max() / 100**2,
            color=agg["change"],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="% Change from Shock")
        ),
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Predicted Share (2026a): %{x:.2f}%<br>" +
            "Shock Impact (Δ Share): %{y:.2f}%<br>" +
            "<extra></extra>"
        )
    ))

    # Dotted line = avg change
    avg_y = agg["change"].mean()
    fig.add_shape(
        type="line",
        x0=agg["percentage"].min(),
        x1=agg["percentage"].max(),
        y0=avg_y,
        y1=avg_y,
        line=dict(color="black", dash="dot")
    )
    fig.add_annotation(
        x=agg["percentage"].max(),
        y=avg_y,
        text=f"Avg Impact: {avg_y:.2f}%",
        showarrow=False,
        font=dict(size=12),
        yshift=10
    )

    fig.update_layout(
        title=f"Shock Impact on Forecasted Trade by {'Sector' if groupby_field == 'Sector Group' else 'Partner'} for {selected_country}",
        xaxis_title="% Share of Trade in 2026a (No Shock)",
        yaxis_title="Shock Impact (% Share Change: a - b)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600
    )

    return fig
