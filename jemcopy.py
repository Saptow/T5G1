### Run something ### 

# Full Dash App with All Styling and UI Enhancements Applied

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash
import dash_bootstrap_components as dbc

# === Load Data ===
df = pd.read_csv("trade_data_realistic_changes.csv")
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
df['previous_volume'] = pd.to_numeric(df['previous_volume'], errors='coerce')

TOP_N = 10
COUNTRY_LIST = sorted(df['country'].unique())

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Trade Treemap Explorer"

# === Layout ===
app.layout = html.Div([
    html.Div([
        html.H1("Trade Explorer Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),

        # Line 1: Country selection
        html.Div([
            html.Label("Country:"),
            dcc.Dropdown(
                id='country-select',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value=COUNTRY_LIST[0],
                placeholder='Select a country',
                searchable=True,
                style={'width': '300px', 'margin': '0 auto'}
            ),
        ], style={'textAlign': 'center', 'marginBottom': '10px'}),

        # Line 2: Trade type buttons
        html.Div([
            dbc.ButtonGroup([
                dbc.Button("Export", id='btn-export', n_clicks=0, color='primary', outline=True, className='trade-btn'),
                dbc.Button("Import", id='btn-import', n_clicks=0, color='secondary', outline=True, className='trade-btn')
            ], size='md')
        ], style={'textAlign': 'center', 'marginBottom': '15px'}),

        # Line 3: Filter dropdowns
        html.Div([
            html.Div([
                html.Label("Filter by Partner Country:"),
                dcc.Dropdown(id='country-select-alt2', searchable=True)
            ], style={'width': '40%', 'display': 'inline-block', 'textAlign': 'left'}),

            html.Div([
                html.Label("Filter by Sector:"),
                dcc.Dropdown(id='sector-select-alt', searchable=True)
            ], style={'width': '40%', 'display': 'inline-block', 'marginLeft': '20px', 'textAlign': 'left'}),
        ], style={'textAlign': 'center', 'justifyContent': 'center', 'marginBottom': '30px'})
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '30px',
        'fontFamily': 'Open Sans, sans-serif',
        'borderRadius': '12px',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
        'margin': '20px'
    }),

    html.Div([
        dcc.Graph(id='sector-treemap', config={'displayModeBar': False}),
        dcc.Graph(id='country-treemap', config={'displayModeBar': False})
    ], style={
        'backgroundColor': '#f5f5f5',
        'padding': '20px',
        'borderRadius': '10px',
        'margin': '0 20px 20px 20px'
    }),

    dcc.Store(id='trade-type-select', data='export')
])

# === Helper Functions ===
def group_top_n(data, group_col):
    top = data.nlargest(TOP_N, 'percentage')
    others = data[~data[group_col].isin(top[group_col])]
    if not others.empty:
        others_agg = pd.DataFrame({
            group_col: ['Others'],
            'percentage': [others['percentage'].sum()],
            'change': [others['change'].mean()],
            'volume': [others['volume'].sum()],
            'previous_volume': [others['previous_volume'].sum()]
        })
        return pd.concat([top, others_agg], ignore_index=True)
    return top

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
    dynamic_range = max(1, round(max_abs_change * 5, 2))  # Avoid zero and too-small range
    grouped['change_clipped'] = grouped['change'].clip(lower=-dynamic_range, upper=dynamic_range)
    grouped['dynamic_range'] = dynamic_range  # For use in plotting
    return grouped

# === Interactivity ===
@app.callback(
    Output('trade-type-select', 'data'),
    Output('btn-export', 'color'),
    Output('btn-import', 'color'),
    [Input('btn-export', 'n_clicks'), Input('btn-import', 'n_clicks')],
    prevent_initial_call=True
)
def update_trade_type(n_export, n_import):
    ctx = dash.callback_context.triggered_id
    if ctx == 'btn-export':
        return 'export', 'primary', 'secondary'
    elif ctx == 'btn-import':
        return 'import', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    [Output('sector-treemap', 'figure'),
     Output('country-treemap', 'figure'),
     Output('sector-select-alt', 'options'),
     Output('country-select-alt2', 'options')],
    [Input('country-select', 'value'),
     Input('trade-type-select', 'data'),
     Input('sector-select-alt', 'value'),
     Input('country-select-alt2', 'value')]
)
def update_treemaps(selected_country, trade_type, selected_sector, selected_partner):
    filtered = df[(df['country'] == selected_country) & (df['trade_type'] == trade_type)].copy()
    sector_options = [{'label': s, 'value': s} for s in sorted(filtered['sector'].unique())]
    partner_options = [{'label': p, 'value': p} for p in sorted(filtered['partner_country'].unique())]

    # Sector Treemap
    sector_view = filtered[filtered['partner_country'] == selected_partner] if selected_partner else filtered
    sector_agg = calculate_percentages(sector_view, 'sector')
    sector_agg = group_top_n(sector_agg, 'sector')
    sector_agg['percentage'] = sector_agg['percentage'].round(1)
    sector_agg['change'] = sector_agg['change'].round(2)
    sector_agg['change_clipped'] = sector_agg['change_clipped'].round(2)
    sector_agg['change_str'] = sector_agg['change'].apply(lambda x: f"{x:+.2f}%")
    sector_agg['volume_fmt'] = sector_agg['volume'].apply(lambda x: f"{x:,.0f}")
    sector_agg['previous_volume_fmt'] = sector_agg['previous_volume'].apply(lambda x: f"{x:,.0f}")

    title_sector = f"{trade_type.capitalize()} Breakdown by Sector"
    if selected_partner:
        title_sector = f"{trade_type.capitalize()} from {selected_country} to {selected_partner}, by Sector"

    fig_sector = px.treemap(
        sector_agg,
        path=['sector'],
        values='percentage',
        color='change_clipped',
        color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
        range_color=[-sector_agg['dynamic_range'].iloc[0], sector_agg['dynamic_range'].iloc[0]],
        color_continuous_midpoint=0,
        custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'],
        title=title_sector
    )
    fig_sector.update_traces(
        hovertemplate='<b>%{label}</b><br>'
                      'Share: %{customdata[0]:.1f}%<br>'
                      'Change: %{customdata[1]}<br>'
                      'Volume: %{customdata[2]}<br>'
                      'Prev Volume: %{customdata[3]}',
        texttemplate='<b>%{label}</b><br>%{customdata[0]:.1f}% (%{customdata[1]})',
        root_color='white',
        textfont_size=None
    )
    fig_sector.update_layout(
        font=dict(family='Open Sans, sans-serif', size=14),
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_showscale=False
    )

    # Country Treemap
    country_view = filtered[filtered['sector'] == selected_sector] if selected_sector else filtered
    country_agg = calculate_percentages(country_view, 'partner_country')
    country_agg = group_top_n(country_agg, 'partner_country')
    country_agg['percentage'] = country_agg['percentage'].round(1)
    country_agg['change'] = country_agg['change'].round(2)
    country_agg['change_clipped'] = country_agg['change_clipped'].round(2)
    country_agg['change_str'] = country_agg['change'].apply(lambda x: f"{x:+.2f}%")
    country_agg['volume_fmt'] = country_agg['volume'].apply(lambda x: f"{x:,.0f}")
    country_agg['previous_volume_fmt'] = country_agg['previous_volume'].apply(lambda x: f"{x:,.0f}")

    title_country = f"{trade_type.capitalize()} Breakdown by Country"
    if selected_sector:
        title_country = f"{selected_country}'s {trade_type.capitalize()} of {selected_sector}, by Country"

    fig_country = px.treemap(
        country_agg,
        path=['partner_country'],
        values='percentage',
        color='change_clipped',
        color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
        range_color=[-10, 10],
        color_continuous_midpoint=0,
        custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'],
        title=title_country
    )
    fig_country.update_traces(
        hovertemplate='<b>%{label}</b><br>'
                      'Share: %{customdata[0]:.1f}%<br>'
                      'Change: %{customdata[1]}<br>'
                      'Volume: %{customdata[2]}<br>'
                      'Prev Volume: %{customdata[3]}',
        texttemplate='<b>%{label}</b><br>%{customdata[0]:.1f}% (%{customdata[1]})',
        root_color='white',
        textfont_size=None
    )
    fig_country.update_layout(
        font=dict(family='Open Sans, sans-serif', size=14),
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_showscale=False
    )

    return fig_sector, fig_country, sector_options, partner_options

if __name__ == '__main__':
    app.run(debug=True, port = 8051)





