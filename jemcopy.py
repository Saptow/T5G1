### Run something ### 
# Dash App: Combined Treemap and Bar Graph Viewer (Updated Layout & Color Scheme)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash

# === Load Data ===
df = pd.read_csv("trade_data_realistic_changes.csv")
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
df['previous_volume'] = pd.to_numeric(df['previous_volume'], errors='coerce')

COUNTRY_LIST = sorted(df['country'].unique())
MAX_TOP_N = 20

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Trade Explorer Dashboard"

# === Layout ===
app.layout = html.Div([
    html.H1("Trade Explorer Dashboard", className="text-center mb-4", style={'color': '#2c3e50'}),

    dbc.Row([
        dbc.Col([
            html.Label([html.B("Country:")]),
            dcc.Dropdown(
                id='country-select',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value=COUNTRY_LIST[0],
                searchable=True
            )
        ], md=4),
    ], className='mb-2 justify-content-center'),

    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Exports", id='btn-export', n_clicks=0, color='primary', outline=True, size='sm'),
                dbc.Button("Imports", id='btn-import', n_clicks=0, color='secondary', outline=True, size='sm')
            ], className='w-100')
        ], md=3),

        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("% Share", id='btn-percentage', n_clicks=0, color='primary', outline=True, size='sm'),
                dbc.Button("Volume", id='btn-volume', n_clicks=0, color='secondary', outline=True, size='sm')
            ], className='w-100')
        ], md=3)
    ], className='mb-2 justify-content-center'),

    dbc.Row([
        dbc.Col([
            html.Label(html.B("Partner Country:")),
            dcc.Dropdown(id='partner-country-select', searchable=True)
        ], md=4),

        dbc.Col([
            html.Label(html.B("Sector:")),
            dcc.Dropdown(id='sector-select', searchable=True)
        ], md=4)
    ], className='mb-3 justify-content-center'),

    dbc.Row([
        dbc.Col([
            html.Label(html.B("View Top N:")),
            dcc.Slider(id='top-n-slider', min=1, max=MAX_TOP_N, step=1, value=10,
                       tooltip={"placement": "bottom", "always_visible": True})
        ], md=8)
    ], className='mb-4 justify-content-center'),

    dbc.Row([
        dbc.Col([
            html.Label("View Type:"),
            dbc.Checklist(
                id='view-type',
                options=[
                    {"label": "Treemap", "value": "treemap"},
                    {"label": "Bar Graph", "value": "bar"}
                ],
                value=['treemap'],
                switch=True,
                inline=True
            )
        ], width='auto')
    ], className='mb-4'),

    html.Div(id='graph-content'),
    dcc.Store(id='trade-type-select', data='export'),
    dcc.Store(id='value-mode', data='percentage')
])

# === Helper ===
def calculate_grouped(data, group_by):
    grouped = data.groupby(group_by, as_index=False).agg({
        'volume': 'sum',
        'previous_volume': 'sum'
    })
    total_volume = grouped['volume'].sum()
    total_prev = grouped['previous_volume'].sum()
    grouped['percentage'] = 100 * grouped['volume'] / total_volume if total_volume else 0
    grouped['prev_percentage'] = 100 * grouped['previous_volume'] / total_prev if total_prev else 0
    grouped['change'] = grouped['percentage'] - grouped['prev_percentage'] if total_prev and total_volume else 0
    grouped['change'] = grouped['change'].round(2)
    grouped['percentage'] = grouped['percentage'].round(1)
    grouped['prev_percentage'] = grouped['prev_percentage'].round(1)
    grouped['volume'] = grouped['volume'].round(0)
    grouped['previous_volume'] = grouped['previous_volume'].round(0)
    grouped['change_str'] = grouped['change'].apply(lambda x: f"{x:+.2f}%")
    max_abs_change = grouped['change'].abs().max()
    dynamic_range = max(1, round(max_abs_change * 5, 2))
    grouped['change_clipped'] = grouped['change'].clip(lower=-dynamic_range, upper=dynamic_range)
    grouped['dynamic_range'] = dynamic_range
    return grouped

# === Callbacks for button logic ===
@app.callback(
    Output('trade-type-select', 'data'),
    Output('btn-export', 'color'),
    Output('btn-import', 'color'),
    Input('btn-export', 'n_clicks'),
    Input('btn-import', 'n_clicks')
)
def toggle_trade_type(n_export, n_import):
    ctx = dash.callback_context.triggered_id
    if ctx == 'btn-export':
        return 'export', 'primary', 'secondary'
    elif ctx == 'btn-import':
        return 'import', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('value-mode', 'data'),
    Output('btn-percentage', 'color'),
    Output('btn-volume', 'color'),
    Input('btn-percentage', 'n_clicks'),
    Input('btn-volume', 'n_clicks')
)
def toggle_value_mode(n_percentage, n_volume):
    ctx = dash.callback_context.triggered_id
    if ctx == 'btn-percentage':
        return 'percentage', 'primary', 'secondary'
    elif ctx == 'btn-volume':
        return 'volume', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update

# === Callback to update graphs ===
@app.callback(
    [Output('graph-content', 'children'),
     Output('partner-country-select', 'options'),
     Output('sector-select', 'options')],
    [Input('country-select', 'value'),
     Input('trade-type-select', 'data'),
     Input('value-mode', 'data'),
     Input('top-n-slider', 'value'),
     Input('partner-country-select', 'value'),
     Input('sector-select', 'value'),
     Input('view-type', 'value')]
)
def update_graphs(country, trade_type, value_mode, top_n, partner_filter, sector_filter, view_type):
    filtered = df[(df['country'] == country) & (df['trade_type'] == trade_type)].copy()
    partner_opts = [{'label': p, 'value': p} for p in sorted(filtered['partner_country'].unique())]
    sector_opts = [{'label': s, 'value': s} for s in sorted(filtered['sector'].unique())]

    sector_view = filtered[filtered['partner_country'] == partner_filter] if partner_filter else filtered
    country_view = filtered[filtered['sector'] == sector_filter] if sector_filter else filtered

    sector_grouped = calculate_grouped(sector_view, 'sector')
    top = sector_grouped.nlargest(top_n, value_mode)
    others = sector_grouped[~sector_grouped['sector'].isin(top['sector'])]
    if not others.empty:
        others_row = pd.DataFrame({
            'sector': ['Others'],
            value_mode: [others[value_mode].sum()],
            'change': [others['change'].mean()],
            'change_clipped': [others['change_clipped'].mean()],
            'percentage': [others['percentage'].sum()],
            'prev_percentage': [others['prev_percentage'].sum()],
            'volume': [others['volume'].sum()],
            'previous_volume': [others['previous_volume'].sum()],
            'change_str': [f"{others['change'].mean():+.2f}%"],
            'dynamic_range': [others['dynamic_range'].mean()]
        })
        sector_grouped = pd.concat([top, others_row], ignore_index=True)
    else:
        sector_grouped = top
    country_grouped = calculate_grouped(country_view, 'partner_country')
    top = country_grouped.nlargest(top_n, value_mode)
    others = country_grouped[~country_grouped['partner_country'].isin(top['partner_country'])]
    if not others.empty:
        others_row = pd.DataFrame({
            'partner_country': ['Others'],
            value_mode: [others[value_mode].sum()],
            'change': [others['change'].mean()],
            'change_clipped': [others['change_clipped'].mean()],
            'percentage': [others['percentage'].sum()],
            'prev_percentage': [others['prev_percentage'].sum()],
            'volume': [others['volume'].sum()],
            'previous_volume': [others['previous_volume'].sum()],
            'change_str': [f"{others['change'].mean():+.2f}%"],
            'dynamic_range': [others['dynamic_range'].mean()]
        })
        country_grouped = pd.concat([top, others_row], ignore_index=True)
    else:
        country_grouped = top

    if view_type == 'bar':
        fig_sector = go.Figure([
            go.Bar(x=sector_grouped['sector'], y=sector_grouped[value_mode], name='Current', marker_color='steelblue'),
            go.Bar(x=sector_grouped['sector'], y=sector_grouped['prev_percentage'] if value_mode == 'percentage' else sector_grouped['previous_volume'], name='Previous', marker_color='lightgrey')
        ])
        fig_sector.update_layout(
            barmode='group',
            title=f"Top {top_n} {trade_type.capitalize()}s by Sector",
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_tickangle=-45,
            font=dict(family='Open Sans', size=14)
        )

        fig_country = go.Figure([
            go.Bar(x=country_grouped['partner_country'], y=country_grouped[value_mode], name='Current', marker_color='seagreen'),
            go.Bar(x=country_grouped['partner_country'], y=country_grouped['prev_percentage'] if value_mode == 'percentage' else country_grouped['previous_volume'], name='Previous', marker_color='lightgrey')
        ])
        fig_country.update_layout(
            barmode='group',
            title=f"Top {top_n} {trade_type.capitalize()}s by Country",
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_tickangle=-45,
            font=dict(family='Open Sans', size=14)
        )
    else:
        def create_treemap(df_grouped, path, title):
            fig = px.treemap(
                df_grouped,
                path=[path],
                values='percentage',
                color='change_clipped',
                color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
                range_color=[-df_grouped['dynamic_range'].iloc[0], df_grouped['dynamic_range'].iloc[0]],
                color_continuous_midpoint=0,
                custom_data=['percentage', 'change', 'volume', 'previous_volume']
            )
            fig.update_traces(
                hovertemplate='<b>%{label}</b><br>'
                              'Share: %{customdata[0]:.1f}%<br>'
                              'Change: %{customdata[1]:+.2f}%<br>'
                              'Volume: %{customdata[2]:,.0f}<br>'
                              'Prev Volume: %{customdata[3]:,.0f}',
                texttemplate='<b>%{label}</b><br>%{customdata[0]:.1f}% (%{customdata[1]:+.2f}%)',
                root_color='white'
            )
            fig.update_layout(
                margin=dict(t=30, l=10, r=10, b=10),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family='Open Sans', size=14),
                coloraxis_showscale=False,
                title=title
            )
            return fig

        title_sector = f"{trade_type.capitalize()}s Breakdown by Sector"
        if partner_filter:
            title_sector = f"{trade_type.capitalize()}s from {country} to {partner_filter}, by Sector"
        fig_sector = create_treemap(sector_grouped, 'sector', title_sector)
        title_country = f"{trade_type.capitalize()}s Breakdown by Country"
        if sector_filter:
            title_country = f"{country}'s {trade_type.capitalize()}s of {sector_filter}, by Country"
        fig_country = create_treemap(country_grouped, 'partner_country', title_country)

    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_sector), md=6),
            dbc.Col(dcc.Graph(figure=fig_country), md=6),
        ])
    ], partner_opts, sector_opts

if __name__ == '__main__':
    app.run(debug=True, port=8051)




