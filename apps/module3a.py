## Module 3a for test

import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc

# === Load Data ===
df = pd.read_csv("trade_data_realistic_changes.csv")
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
df['previous_volume'] = pd.to_numeric(df['previous_volume'], errors='coerce')

COUNTRY_LIST = sorted(df['country'].unique())
MAX_TOP_N = 20

# === Sidebar Controls ===
sidebar_controls = html.Div([])
# sidebar_controls = html.Div([
#     html.H5("Module 1B Filters", className="text-muted mb-3"),

#     html.Label([
#         html.B("Country:"),
#         html.I(className="bi bi-info-circle ms-1", id="tooltip-country1b")
#     ]),
#     dcc.Dropdown(
#         id='country-select1b',
#         options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
#         value=COUNTRY_LIST[0],
#         placeholder='Select a country',
#         style={"color": "black", "backgroundColor": "white"},
#         searchable=True,
#         className='mb-3'
#     ),

#     html.Label("Trade Type:"),
#     dbc.ButtonGroup([
#         dbc.Button("Exports", id='btn-export1b', n_clicks=0, outline=True, size='sm'),
#         dbc.Button("Imports", id='btn-import1b', n_clicks=0, outline=True, size='sm')
#     ], className='w-100 mb-3'),

#     html.Label("Display:"),
#     dbc.ButtonGroup([
#         dbc.Button("Volume", id='btn-volume1b', n_clicks=0, outline=True, size='sm'),
#         dbc.Button("Percentage", id='btn-percentage1b', n_clicks=0, outline=True, size='sm')
#     ], className='w-100 mb-3'),

#     html.Label("Partner Country:"),
#     dcc.Dropdown(id='country-select-alt21b', style={"color": "black", "backgroundColor": "white"}, searchable=True, className='mb-3'),

#     html.Label("Sector:"),
#     dcc.Dropdown(id='sector-select-alt1b', style={"color": "black", "backgroundColor": "white"}, searchable=True, className='mb-3'),

#     html.Label("View Top N:"),
#     dcc.Slider(id='top-n-slider1b', min=1, max=MAX_TOP_N, step=1, value=10,
#                tooltip={"placement": "bottom", "always_visible": True})
# ])


layout = html.Div([
    #dcc.Store(id="input-uploaded"),
    dcc.Store(id="trade-type-select1b", data='export'),
    dcc.Store(id="display-type1b", data='volume'),

    html.H1("Trade Explorer Dashboard (Module 1B)", className="text-center mb-4", style={'color': '#2c3e50'}),

    # === Inputs inline inside layout ===
    html.Div([
        html.Div([
            html.Label("Select a Country", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select1b',
                options=[{'label': c, 'value': c} for c in COUNTRY_LIST],
                value=COUNTRY_LIST[0],
                placeholder='Select a country',
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-4"),

        html.Div([
            html.Label("Partner Country", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select-alt21b',
                style={"color": "black", "backgroundColor": "white", "width": "100%"},
                placeholder="Select partner country",
                searchable=True,
                className="mb-3"
            )
        ], className="col-md-4"),

        html.Div([
            html.Label("Sector", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='sector-select-alt1b',
                style={"color": "black", "backgroundColor": "white", "width": "100%"},
                placeholder="Select sector",
                searchable=True,
                className="mb-3"
            )
        ], className="col-md-4")
    ], className="row mb-3"),

    html.Div([
        html.Div([
            html.Label("Trade Type", className="form-label fw-semibold mb-1"),
            dbc.ButtonGroup([
                dbc.Button("Exports", id='btn-export1b', n_clicks=0, outline=True, size='sm'),
                dbc.Button("Imports", id='btn-import1b', n_clicks=0, outline=True, size='sm')
            ], className='w-100')
        ], className="col-md-4"),

        html.Div([
            html.Label("Display Type", className="form-label fw-semibold mb-1"),
            dbc.ButtonGroup([
                dbc.Button("Volume", id='btn-volume1b', n_clicks=0, outline=True, size='sm'),
                dbc.Button("Percentage", id='btn-percentage1b', n_clicks=0, outline=True, size='sm')
            ], className='w-100')
        ], className="col-md-4"),

        html.Div([
            html.Label("Top N View", className="form-label fw-semibold mb-1"),
            dcc.Slider(
                id='top-n-slider1b',
                min=1, max=MAX_TOP_N, step=1, value=10,
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], className="col-md-4")
    ], className="row mb-4"),

    html.Div(id="tab-warning1b", className="text-danger mb-2 text-center"),

    dcc.Tabs(id="module1b-tabs", value="historical", children=[
         dcc.Tab(label="Historical", value="historical"),
         dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1b", disabled=True),
     ]),
    
    html.Div(id="module1b-tabs-container"),

    html.Div(id="module1b-tab-content", className="mt-3"),
    # === Hidden dummy components to make Dash recognize outputs ===
    html.Div([
        html.Div(id='sector-title1b', style={'display': 'none'}),
        dcc.Graph(id='sector-treemap1b', style={'display': 'none'}),
        html.Div(id='country-title1b', style={'display': 'none'}),
        dcc.Graph(id='country-treemap1b', style={'display': 'none'})
    ], style={'display': 'none'})
])

# layout = html.Div([
#     dcc.Store(id="input-uploaded"),  # global state 

#     html.Div([
#         # module-local stores 
#         dcc.Store(id="trade-type-select1b", data='export'),
#         dcc.Store(id="display-type1b", data='volume'),

#         html.H1("Trade Explorer Dashboard (Module 1B)", className="text-center mb-4", style={'color': '#2c3e50'}),

#         sidebar_controls,

#         html.Div(id="tab-warning1b", className="text-danger mb-2 text-center"),

#         dcc.Tabs(id="module1b-tabs", value="historical", children=[
#             dcc.Tab(label="Historical", value="historical"),
#             dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1b", disabled=True),
#         ]),

#         html.Div(id="module1b-tab-content", className="mt-3"),
#     ], style={
#         'backgroundColor': '#ffffff',
#         'padding': '30px',
#         'fontFamily': 'Open Sans, sans-serif',
#         'borderRadius': '12px',
#         'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
#         'margin': '20px'
#     }),
# ])


app = get_app()

@app.callback(
    Output('trade-type-select1b', 'data'),
    Output('btn-export1b', 'color'),
    Output('btn-import1b', 'color'),
    Input('btn-export1b', 'n_clicks'),
    Input('btn-import1b', 'n_clicks'),
    prevent_initial_call=True
)
def update_trade_type(n_export, n_import):
    ctx = callback_context.triggered_id
    if ctx == 'btn-export1b':
        return 'export', 'primary', 'secondary'
    elif ctx == 'btn-import1b':
        return 'import', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('display-type1b', 'data'),
    Output('btn-volume1b', 'color'),
    Output('btn-percentage1b', 'color'),
    Input('btn-volume1b', 'n_clicks'),
    Input('btn-percentage1b', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_display_type(n_volume, n_percentage):
    ctx = callback_context.triggered_id
    if ctx == 'btn-volume1b':
        return 'volume', 'primary', 'secondary'
    elif ctx == 'btn-percentage1b':
        return 'percentage', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("prediction-tab1b", "disabled"),
    Input("input-uploaded", "data"),
    #prevent_initial_call=True
)
def toggle_prediction_tab(uploaded):
    return not uploaded

@app.callback(
    Output("module1b-tabs", "value"),
    Input("input-uploaded", "data"),
    prevent_initial_call=True
)
def switch_to_prediction_tab(uploaded):
    if uploaded:
        return "prediction"
    return dash.no_update

@app.callback(
    Output("module1b-tab-content", "children"),
    Input("module1b-tabs", "value")
)
def render_tab_content(tab):
    if tab == "historical":
        return html.Div([
            html.Div(style={'marginTop': '20px'}),
            html.H5(id='sector-title1b', className="text-center mb-2"),
            dcc.Graph(id='sector-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white"}),
            html.H5(id='country-title1b', className="text-center mb-2"),
            dcc.Graph(id='country-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white"})
        ])
    elif tab == "prediction":
        return html.Div([
            html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
            html.P("This will show trade predictions based on uploaded news input.", className="text-center")
        ])

# @app.callback(
#     Output('sector-treemap1b', 'figure'),
#     Output('country-treemap1b', 'figure'),
#     Output('sector-select-alt1b', 'options'),
#     Output('country-select-alt21b', 'options'),
#     Output('sector-title1b', 'children'),
#     Output('country-title1b', 'children'),
#     Input('country-select1b', 'value'),
#     Input('trade-type-select1b', 'data'),
#     Input('sector-select-alt1b', 'value'),
#     Input('country-select-alt21b', 'value'),
#     Input('top-n-slider1b', 'value'),
#     Input('display-type1b', 'data')
# )
# def update_visualizations(selected_country, trade_type, selected_sector, selected_partner, top_n, display_type):
#     filtered = df[(df['country'] == selected_country) & (df['trade_type'] == trade_type)].copy()
#     sector_options = [{'label': s, 'value': s} for s in sorted(filtered['sector'].unique())]
#     partner_options = [{'label': p, 'value': p} for p in sorted(filtered['partner_country'].unique())]

#     sector_view = filtered[filtered['partner_country'] == selected_partner] if selected_partner else filtered
#     sector_agg = calculate_percentages(sector_view, 'sector')
#     sector_agg = group_top_n(sector_agg, 'sector', top_n)

#     country_view = filtered[filtered['sector'] == selected_sector] if selected_sector else filtered
#     country_agg = calculate_percentages(country_view, 'partner_country')
#     country_agg = group_top_n(country_agg, 'partner_country', top_n)

#     title_sector = f"Top {top_n} {trade_type.capitalize()}s by Sector"
#     title_country = f"Top {top_n} {trade_type.capitalize()}s by Country"
#     if selected_partner:
#         title_sector = f"Top {top_n} {trade_type.capitalize()}s from {selected_country} to {selected_partner} by Sector"
#     if selected_sector:
#         title_country = f"Top {top_n} {selected_country}'s {trade_type.capitalize()}s in {selected_sector} by Country"

#     if display_type == 'volume':
#         fig_sector = generate_bar_chart(sector_agg, 'sector', 'volume', 'previous_volume')
#         fig_country = generate_bar_chart(country_agg, 'partner_country', 'volume', 'previous_volume')
#     else:
#         max_sector_change = sector_agg['change'].abs().max() * 5
#         max_country_change = country_agg['change'].abs().max() * 5

#         hover_template = '<b>%{label}</b><br>Share: %{customdata[0]}%<br>Change: %{customdata[1]}<br>Volume: %{customdata[2]}<br>Prev Volume: %{customdata[3]}'

#         for df_agg in [sector_agg, country_agg]:
#             df_agg['percentage'] = df_agg['percentage'].round(1)
#             df_agg['change_str'] = df_agg['change'].apply(lambda x: f"{x:+.2f}%")
#             df_agg['volume_fmt'] = df_agg['volume'].apply(lambda x: f"{x:,.0f}")
#             df_agg['previous_volume_fmt'] = df_agg['previous_volume'].apply(lambda x: f"{x:,.0f}")

#         fig_sector = px.treemap(sector_agg, path=['sector'], values='percentage', color='change_clipped',
#                                 color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
#                                 range_color=[-max_sector_change, max_sector_change], color_continuous_midpoint=0,
#                                 custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'])
#         fig_sector.update_traces(hovertemplate=hover_template, texttemplate='<b>%{label}</b><br>%{customdata[0]}% (%{customdata[1]})')
#         fig_sector.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

#         fig_country = px.treemap(country_agg, path=['partner_country'], values='percentage', color='change_clipped',
#                                  color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
#                                  range_color=[-max_country_change, max_country_change], color_continuous_midpoint=0,
#                                  custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'])
#         fig_country.update_traces(hovertemplate=hover_template, texttemplate='<b>%{label}</b><br>%{customdata[0]}% (%{customdata[1]})')
#         fig_country.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

#     return fig_sector, fig_country, sector_options, partner_options, title_sector, title_country
    
@app.callback(
    Output('sector-treemap1b', 'figure'),
    Output('country-treemap1b', 'figure'),
    Output('sector-select-alt1b', 'options'),
    Output('country-select-alt21b', 'options'),
    Output('sector-title1b', 'children'),
    Output('country-title1b', 'children'),
    Input('country-select1b', 'value'),
    Input('trade-type-select1b', 'data'),
    Input('sector-select-alt1b', 'value'),
    Input('country-select-alt21b', 'value'),
    Input('top-n-slider1b', 'value'),
    Input('display-type1b', 'data')
)
def update_visualizations(selected_country, trade_type, selected_sector, selected_partner, top_n, display_type):
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

    if display_type == 'volume':
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


# === Helpers ===

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

# @app.callback(
#     Output("module1b-tabs-container", "children"),
#     Input("input-uploaded", "data")
# )
# def build_tabs(uploaded):
#     return dcc.Tabs(id="module1b-tabs", value="historical", children=[
#         dcc.Tab(label="Historical", value="historical"),
#         dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1b", disabled=not uploaded),
#     ])