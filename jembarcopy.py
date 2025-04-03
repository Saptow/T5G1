### Run something ### 

# Updated Input Controls and Layout (Volume = Bar Graph, Percentage = Treemap)

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Switch

# === Load Data ===
df = pd.read_csv("trade_data_realistic_changes.csv")
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
df['previous_volume'] = pd.to_numeric(df['previous_volume'], errors='coerce')

COUNTRY_LIST = sorted(df['country'].unique())
MAX_TOP_N = 20

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Trade Treemap Explorer"

# === Layout ===
app.layout = html.Div([
    html.Div([
        html.H1("Trade Explorer Dashboard", className="text-center mb-4", style={'color': '#2c3e50'}),

        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label([html.B("Country:"), html.I(className="bi bi-info-circle ms-1", id="tooltip-country")]),
                    dcc.Dropdown(
                        id='country-select',
                        options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                        value=COUNTRY_LIST[0],
                        placeholder='Select a country',
                        searchable=True,
                        className='input-dropdown'
                    ),
                ], xs=12, sm=12, md=4),
            ], className='mb-3', justify='center'),

            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Exports", id='btn-export', n_clicks=0, color='primary', outline=True, size='sm'),
                        dbc.Button("Imports", id='btn-import', n_clicks=0, color='secondary', outline=True, size='sm')
                    ], className='w-100')
                ], width=4, className='mb-2')
            ], justify='center', className='mb-2'),

            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Volume", id='btn-volume', n_clicks=0, color='primary', outline=True, size='sm'),
                        dbc.Button("Percentage", id='btn-percentage', n_clicks=0, color='secondary', outline=True, size='sm')
                    ], className='w-100')
                ], width=4, className='mb-2')
            ], justify='center', className='mb-2'),

            dbc.Row([
                dbc.Col([
                    html.Label(html.B("Partner Country:")),
                    dcc.Dropdown(id='country-select-alt2', searchable=True, className='input-dropdown'),
                ], xs=12, sm=12, md=4),

                dbc.Col([
                    html.Label(html.B("Sector:")),
                    dcc.Dropdown(id='sector-select-alt', searchable=True, className='input-dropdown'),
                ], xs=12, sm=12, md=4),
            ], className='mb-3', justify='center'),

            dbc.Row([
                dbc.Col([
                    html.Label(html.B("View Top N:")),
                    dcc.Slider(id='top-n-slider', min=1, max=MAX_TOP_N, step=1, value=10,
                               tooltip={"placement": "bottom", "always_visible": True})
                ], width=8)
            ], justify='center')
        ]),

        dcc.Loading([
            html.Div([
                html.Div(style={'marginTop': '20px'}),
                html.H5(id='sector-title', className="text-center mb-2"),
                dcc.Graph(id='sector-treemap', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
            ], className='mb-4'),

            html.Div([
                html.H5(id='country-title', className="text-center mb-2"),
                dcc.Graph(id='country-treemap', config={'displayModeBar': False}, style={"backgroundColor": "white"})
            ])
        ])
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '30px',
        'fontFamily': 'Open Sans, sans-serif',
        'borderRadius': '12px',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
        'margin': '20px'
    }),

    dcc.Store(id='trade-type-select', data='export'),
    dcc.Store(id='display-type', data='volume'),
    dbc.Tooltip("Select the reporting country", target="tooltip-country")
])




# Full Combined Dash App (Part 2 - Middle: Helper Functions)

# === Helper Functions ===
def group_top_n(data, group_col, top_n):
    top = data.nlargest(top_n, 'percentage')
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
    dynamic_range = max(1, round(max_abs_change * 5, 2))
    grouped['change_clipped'] = grouped['change'].clip(lower=-dynamic_range, upper=dynamic_range)
    grouped['dynamic_range'] = dynamic_range
    return grouped

# Final Updated Callbacks with User Corrections

# Professional Bar Chart (Only Volume)
def generate_bar_chart(df, x_col, y_col, previous_col):
    df_sorted = df.sort_values(y_col, ascending=False)
    fig = px.bar(df_sorted, x=x_col, y=y_col, text=df_sorted[y_col].apply(lambda x: f"{x:,.0f}"),
                 labels={x_col: x_col.title(), y_col: y_col.title()}, color_discrete_sequence=['#2c7bb6'])
    fig.add_bar(x=df_sorted[x_col], y=df_sorted[previous_col], opacity=0.5, name="Previous Period",
                marker_color='#a6bddb')
    fig.update_layout(barmode='overlay', font=dict(family='Open Sans, sans-serif'),
                      legend=dict(x=0.99, y=0.99, xanchor='right', yanchor='top'),
                      plot_bgcolor='white', paper_bgcolor='white',
                      margin=dict(t=30, l=10, r=10, b=10))
    return fig

@app.callback(
    [Output('sector-treemap', 'figure'),
     Output('country-treemap', 'figure'),
     Output('sector-select-alt', 'options'),
     Output('country-select-alt2', 'options'),
     Output('sector-title', 'children'),
     Output('country-title', 'children')],
    [Input('country-select', 'value'),
     Input('trade-type-select', 'data'),
     Input('sector-select-alt', 'value'),
     Input('country-select-alt2', 'value'),
     Input('top-n-slider', 'value'),
     Input('view-toggle', 'value')]
)
def update_treemaps(selected_country, trade_type, selected_sector, selected_partner, top_n, bar_graph_view):
    filtered = df[(df['country'] == selected_country) & (df['trade_type'] == trade_type)].copy()
    sector_options = [{'label': s, 'value': s} for s in sorted(filtered['sector'].unique())]
    partner_options = [{'label': p, 'value': p} for p in sorted(filtered['partner_country'].unique())]

    sector_view = filtered[filtered['partner_country'] == selected_partner] if selected_partner else filtered
    sector_agg = calculate_percentages(sector_view, 'sector')
    sector_agg = group_top_n(sector_agg, 'sector', top_n)

    country_view = filtered[filtered['sector'] == selected_sector] if selected_sector else filtered
    country_agg = calculate_percentages(country_view, 'partner_country')
    country_agg = group_top_n(country_agg, 'partner_country', top_n)

    title_sector = f"Top {top_n} {trade_type.capitalize()}s by Sector"
    title_country = f"Top {top_n} {trade_type.capitalize()}s by Country"
    if selected_partner:
        title_sector = f"Top {top_n} {trade_type.capitalize()}s from {selected_country} to {selected_partner} by Sector"
    if selected_sector:
        title_country = f"Top {top_n} {selected_country}'s {trade_type.capitalize()}s in {selected_sector} by Country"

    if bar_graph_view:
        fig_sector = generate_bar_chart(sector_agg, 'sector', 'volume', 'previous_volume')
        fig_country = generate_bar_chart(country_agg, 'partner_country', 'volume', 'previous_volume')
    else:
        max_sector_change = sector_agg['change'].abs().max() * 5
        max_country_change = country_agg['change'].abs().max() * 5

        hover_template = '<b>%{label}</b><br>Share: %{customdata[0]}%<br>Change: %{customdata[1]}<br>Volume: %{customdata[2]}<br>Prev Volume: %{customdata[3]}'

        for df_agg in [sector_agg, country_agg]:
            df_agg['percentage'] = df_agg['percentage'].round(1)
            df_agg['change_str'] = df_agg['change'].apply(lambda x: f"{x:+.2f}%")
            df_agg['volume_fmt'] = df_agg['volume'].apply(lambda x: f"{x:,.0f}")
            df_agg['previous_volume_fmt'] = df_agg['previous_volume'].apply(lambda x: f"{x:,.0f}")

        fig_sector = px.treemap(sector_agg, path=['sector'], values='percentage', color='change_clipped',
                                color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
                                range_color=[-max_sector_change, max_sector_change], color_continuous_midpoint=0,
                                custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'])
        fig_sector.update_traces(hovertemplate=hover_template, texttemplate='<b>%{label}</b><br>%{customdata[0]}% (%{customdata[1]})')
        fig_sector.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

        fig_country = px.treemap(country_agg, path=['partner_country'], values='percentage', color='change_clipped',
                                 color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
                                 range_color=[-max_country_change, max_country_change], color_continuous_midpoint=0,
                                 custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'])
        fig_country.update_traces(hovertemplate=hover_template, texttemplate='<b>%{label}</b><br>%{customdata[0]}% (%{customdata[1]})')
        fig_country.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

    return fig_sector, fig_country, sector_options, partner_options, title_sector, title_country

if __name__ == '__main__':
    app.run(debug=True, port=8052)







