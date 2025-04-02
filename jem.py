### Run something ### 
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State

# === Load Data ===
df = pd.read_csv("trade_data_realistic_changes.csv")
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
df['previous_volume'] = pd.to_numeric(df['previous_volume'], errors='coerce')

# === Constants ===
TOP_N = 10
COUNTRY_LIST = sorted(df['country'].unique())

# === App Init ===
app = Dash(__name__)
app.title = "Trade Treemap Explorer"

# === Layout ===
app.layout = html.Div([
    # === TOP SECTION: Interactive Treemap ===
    html.Div([
        html.H3("Original Interactive Treemaps (Click to Filter)"),

        html.Div([
            dcc.Dropdown(
                id='country-select',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value=COUNTRY_LIST[0],
                placeholder='Select a country'
            ),
            dcc.RadioItems(
                id='trade-type-select',
                options=[
                    {'label': 'Export', 'value': 'export'},
                    {'label': 'Import', 'value': 'import'}
                ],
                value='export',
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
            )
        ], style={'marginBottom': '20px'}),

        html.Div([
            dcc.Graph(id='sector-treemap'),
            dcc.Graph(id='country-treemap')
        ]),

        dcc.Store(id='last-sector-click'),
        dcc.Store(id='last-country-click'),
    ], style={'padding': '20px', 'borderBottom': '2px solid #ccc'}),

    # === BOTTOM SECTION: Dropdown-Based Treemap ===
    html.Div([
        html.H3("Alternative Treemaps (Dropdown-Based Filtering)"),

        html.Div([
            html.Div([
                html.Label("Country:"),
                dcc.Dropdown(
                    id='country-select-alt',
                    options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                    value=COUNTRY_LIST[0]
                ),

                html.Label("Trade Type:", style={'marginTop': '10px'}),
                dcc.RadioItems(
                    id='trade-type-select-alt',
                    options=[
                        {'label': 'Export', 'value': 'export'},
                        {'label': 'Import', 'value': 'import'}
                    ],
                    value='export',
                    labelStyle={'display': 'inline-block', 'marginRight': '10px'}
                ),

                html.Label("Filter by Sector:", style={'marginTop': '10px'}),
                dcc.Dropdown(id='sector-select-alt'),

                html.Label("Filter by Partner Country:", style={'marginTop': '10px'}),
                dcc.Dropdown(id='country-select-alt2'),
            ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingRight': '20px'}),

            html.Div([
                dcc.Graph(id='sector-treemap-alt'),
                dcc.Graph(id='country-treemap-alt')
            ], style={'width': '70%', 'display': 'inline-block'}),
        ])
    ], style={'padding': '20px'})
])

# === Helpers ===
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
    return grouped

# === Callback: Top Treemaps (Click to filter) ===
@app.callback(
    [Output('sector-treemap', 'figure'),
     Output('country-treemap', 'figure'),
     Output('last-sector-click', 'data'),
     Output('last-country-click', 'data')],
    [Input('country-select', 'value'),
     Input('trade-type-select', 'value'),
     Input('sector-treemap', 'clickData'),
     Input('country-treemap', 'clickData')],
    [State('last-sector-click', 'data'),
     State('last-country-click', 'data'),
     State('country-select', 'value'),
     State('trade-type-select', 'value')]
)
def update_treemaps(selected_country, trade_type, sector_click, country_click,
                    last_sector, last_country, last_country_selected, last_trade_selected):
    filtered = df[(df['country'] == selected_country) & (df['trade_type'] == trade_type)].copy()
    reset = (selected_country != last_country_selected) or (trade_type != last_trade_selected)

    if reset:
        sector_clicked = None
        country_clicked = None
    else:
        sector_clicked = sector_click['points'][0]['label'] if sector_click else None
        country_clicked = country_click['points'][0]['label'] if country_click else None
        if sector_clicked == last_sector:
            sector_clicked = None
        if country_clicked == last_country:
            country_clicked = None

    sector_view = filtered[filtered['partner_country'] == country_clicked] if country_clicked and country_clicked != 'Others' else filtered
    sector_agg = calculate_percentages(sector_view, 'sector')
    sector_agg = group_top_n(sector_agg, 'sector')
    sector_agg['percentage'] = sector_agg['percentage'].round(1)
    sector_agg['change'] = sector_agg['change'].round(2)
    sector_agg['change_str'] = sector_agg['change'].apply(lambda x: f"{x:+.2f}%")
    sector_title = f"{trade_type.capitalize()} of {country_clicked} by Sector" if country_clicked else f"Overall {trade_type.capitalize()} by Sector"

    fig_sector = px.treemap(sector_agg, path=['sector'], values='percentage',
                            custom_data=['percentage', 'change_str'], title=sector_title, maxdepth=2)
    fig_sector.update_traces(
        hovertemplate='%{label}<br>%{customdata[0]:.1f}% (%{customdata[1]})',
        texttemplate='%{label}<br>%{customdata[0]:.1f}% (%{customdata[1]})',
        root_color="lightgrey"
    )
    if sector_clicked and sector_clicked in sector_agg['sector'].values:
        fig_sector.update_traces(textfont=dict(size=18), marker=dict(line=dict(width=3, color='black')))

    country_view = filtered[filtered['sector'] == sector_clicked] if sector_clicked and sector_clicked != 'Others' else filtered
    country_agg = calculate_percentages(country_view, 'partner_country')
    country_agg = group_top_n(country_agg, 'partner_country')
    country_agg['percentage'] = country_agg['percentage'].round(1)
    country_agg['change'] = country_agg['change'].round(2)
    country_agg['change_str'] = country_agg['change'].apply(lambda x: f"{x:+.2f}%")
    country_title = f"{trade_type.capitalize()} of {sector_clicked} by Country" if sector_clicked else f"Overall {trade_type.capitalize()} by Country"

    fig_country = px.treemap(country_agg, path=['partner_country'], values='percentage',
                             custom_data=['percentage', 'change_str'], title=country_title, maxdepth=2)
    fig_country.update_traces(
        hovertemplate='%{label}<br>%{customdata[0]:.1f}% (%{customdata[1]})',
        texttemplate='%{label}<br>%{customdata[0]:.1f}% (%{customdata[1]})',
        root_color="lightgrey"
    )
    if country_clicked and country_clicked in country_agg['partner_country'].values:
        fig_country.update_traces(textfont=dict(size=18), marker=dict(line=dict(width=3, color='black')))

    return fig_sector, fig_country, sector_clicked, country_clicked

# === Callback: Bottom Treemaps (Dropdown-based) ===
@app.callback(
    [Output('sector-treemap-alt', 'figure'),
     Output('country-treemap-alt', 'figure'),
     Output('sector-select-alt', 'options'),
     Output('country-select-alt2', 'options')],
    [Input('country-select-alt', 'value'),
     Input('trade-type-select-alt', 'value'),
     Input('sector-select-alt', 'value'),
     Input('country-select-alt2', 'value')]
)
def update_alt_treemaps(selected_country, trade_type, selected_sector, selected_partner):
    filtered = df[(df['country'] == selected_country) & (df['trade_type'] == trade_type)].copy()
    sector_options = [{'label': s, 'value': s} for s in sorted(filtered['sector'].unique())]
    partner_options = [{'label': p, 'value': p} for p in sorted(filtered['partner_country'].unique())]

    # Sector
    sector_view = filtered[filtered['partner_country'] == selected_partner] if selected_partner else filtered
    sector_agg = calculate_percentages(sector_view, 'sector')
    sector_agg = group_top_n(sector_agg, 'sector')
    sector_agg['percentage'] = sector_agg['percentage'].round(1)
    sector_agg['change'] = sector_agg['change'].round(2)
    sector_agg['change_str'] = sector_agg['change'].apply(lambda x: f"{x:+.2f}%")
    sector_agg['volume_fmt'] = sector_agg['volume'].apply(lambda x: f"{x:,.0f}")
    sector_agg['previous_volume_fmt'] = sector_agg['previous_volume'].apply(lambda x: f"{x:,.0f}")
    sector_title = f"{trade_type.capitalize()} of {selected_partner} by Sector" if selected_partner else f"Overall {trade_type.capitalize()} by Sector"

    fig_sector = px.treemap(sector_agg, path=['sector'], values='percentage',
                            custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'],
                            title=sector_title, maxdepth=2)
    fig_sector.update_traces(
        hovertemplate='%{label}<br>'
                      'Share: %{customdata[0]:.1f}%<br>'
                      'Change: %{customdata[1]}<br>'
                      'Volume: %{customdata[2]}<br>'
                      'Prev Volume: %{customdata[3]}',
        texttemplate='%{label}<br>%{customdata[0]:.1f}% (%{customdata[1]})',
        root_color="lightgrey"
    )

    # Country
    country_view = filtered[filtered['sector'] == selected_sector] if selected_sector else filtered
    country_agg = calculate_percentages(country_view, 'partner_country')
    country_agg = group_top_n(country_agg, 'partner_country')
    country_agg['percentage'] = country_agg['percentage'].round(1)
    country_agg['change'] = country_agg['change'].round(2)
    country_agg['change_str'] = country_agg['change'].apply(lambda x: f"{x:+.2f}%")
    country_agg['volume_fmt'] = country_agg['volume'].apply(lambda x: f"{x:,.0f}")
    country_agg['previous_volume_fmt'] = country_agg['previous_volume'].apply(lambda x: f"{x:,.0f}")
    country_title = f"{trade_type.capitalize()} of {selected_sector} by Country" if selected_sector else f"Overall {trade_type.capitalize()} by Country"

    fig_country = px.treemap(country_agg, path=['partner_country'], values='percentage',
                             custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'],
                             title=country_title, maxdepth=2)
    fig_country.update_traces(
        hovertemplate='%{label}<br>'
                      'Share: %{customdata[0]:.1f}%<br>'
                      'Change: %{customdata[1]}<br>'
                      'Volume: %{customdata[2]}<br>'
                      'Prev Volume: %{customdata[3]}',
        texttemplate='%{label}<br>%{customdata[0]:.1f}% (%{customdata[1]})',
        root_color="lightgrey"
    )

    return fig_sector, fig_country, sector_options, partner_options

# === Run ===
if __name__ == '__main__':
    app.run(debug=True)



