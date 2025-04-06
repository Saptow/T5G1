from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import plotly.graph_objects as go
import dash_daq as daq

# === Load dataset ===
df_2026 = pd.read_csv("bilateral_trade_data_2026.csv")

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

# === Layout ===
layout = html.Div([
    html.H2("Module 4C: Impact of Shock on Forecasted Trade", className="mb-4"),

    html.Div([
        # Country dropdown
        dcc.Dropdown(
            id='module4c-country-dropdown',
            options=[{'label': r, 'value': r} for r in sorted(df_2026['Reporter'].unique())],
            value='Australia',
            placeholder="Select a country",
            style={'minWidth': '250px'},
            className="me-3"
        ),

        # Grouping switch
        daq.ToggleSwitch(
            id='module4c-groupby-switch',
            label=['Sector', 'Partner'],
            value=False,  # False = Sector
            style={'marginTop': '5px', 'marginRight': '20px'}
        ),

        # Dynamic multi-select filter
        dcc.Dropdown(
            id='module4c-group-filter',
            options=[],  # Filled dynamically
            multi=True,
            placeholder="Filter specific sectors or partners",
            style={'minWidth': '300px'}
        )
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '15px', 'marginBottom': '20px'}),

    dcc.Graph(id='module4c-graph')
])


# === Utility ===
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


# === Dynamic Filter Options ===
@callback(
    Output('module4c-group-filter', 'options'),
    Input('module4c-country-dropdown', 'value'),
    Input('module4c-groupby-switch', 'value')
)
def update_filter_options(selected_country, is_partner):
    groupby_field = "Partner" if is_partner else "Sector Group"
    filtered = df_2026[df_2026["Reporter"] == selected_country]
    unique_values = sorted(filtered[groupby_field].unique())

    if groupby_field == "Sector Group":
        return [{'label': sector_labels.get(val, val), 'value': val} for val in unique_values]
    return [{'label': val, 'value': val} for val in unique_values]


# === Main Graph Callback ===
@callback(
    Output('module4c-graph', 'figure'),
    Input('module4c-country-dropdown', 'value'),
    Input('module4c-groupby-switch', 'value'),
    Input('module4c-group-filter', 'value')
)
def update_module4c_graph(selected_country, is_partner, selected_filters):
    if not selected_country:
        return go.Figure()

    groupby_field = "Partner" if is_partner else "Sector Group"
    df = df_2026[df_2026["Reporter"] == selected_country]

    # Filter by sector/partner if specified
    if selected_filters:
        df = df[df[groupby_field].isin(selected_filters)]

    df_a = df[df["Time Period"] == "2026a"].copy()
    df_b = df[df["Time Period"] == "2026b"].copy()

    df_a = df_a.rename(columns={"Total Trade Volume": "previous_volume"})
    df_b = df_b.rename(columns={"Total Trade Volume": "volume"})

    merged = pd.merge(
        df_a[["Reporter", groupby_field, "previous_volume"]],
        df_b[["Reporter", groupby_field, "volume"]],
        on=["Reporter", groupby_field],
        how="inner"
    )

    if merged.empty:
        return go.Figure()

    agg = calculate_percentages(merged, groupby_field)

    # Apply label map for sectors
    agg["label"] = agg[groupby_field]
    if groupby_field == "Sector Group":
        agg["label"] = agg["label"].map(sector_labels)

    # === Main bubble plot ===
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
        ),
        showlegend=False  # ✅ Hide unwanted legend entry
    ))

    # === Dot centers for clarity ===
    fig.add_trace(go.Scatter(
        x=agg["percentage"],
        y=agg["change"],
        mode='markers',
        marker=dict(size=6, color='black', symbol='circle'),
        hoverinfo='skip',
        showlegend=False
    ))

    # === Average line ===
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
        title=f"Shock Impact on Forecasted Trade by {'Partner' if is_partner else 'Sector'} for {selected_country}",
        xaxis_title="% Share of Trade in 2026a (No Shock)",
        yaxis_title="Shock Impact (% Share Change: a - b)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600
    )

    return fig

sidebar_controls = html.Div([])