## Module 3a for test

import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State, callback_context, get_app
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq

# === Load Data ===
df = pd.read_csv("trade_data_realistic_changes.csv")
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
df['previous_volume'] = pd.to_numeric(df['previous_volume'], errors='coerce')

COUNTRY_LIST = sorted(df['country'].unique())

layout = html.Div([
    dcc.Store(id="input-uploaded"),
    dcc.Store(id="trade-type-select1b", data='total'),
    dcc.Store(id="display-type1b", data='percentage'),

    html.H1("Trade Explorer Dashboard (Module 1B)", className="text-center mb-4", style={'color': '#2c3e50'}),

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
        ], className="col-md-6"),

        html.Div([
            html.Label("Partner Country", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-select-alt21b',
                style={"color": "black", "backgroundColor": "white", "width": "100%"},
                placeholder="Select partner country",
                searchable=True,
                className="mb-3"
            )
        ], className="col-md-6")
    ], className="row mb-3"),

    html.Div([
        html.Div([
        #     html.Label("Trade Type", className="form-label fw-semibold mb-1"),
        #     dbc.ButtonGroup([
        #         dbc.Button("Total", id='btn-total1b', n_clicks=0, outline=True, size='sm', color='primary'),
        #         dbc.Button("Exports", id='btn-export1b', n_clicks=0, outline=True, size='sm'),
        #         dbc.Button("Imports", id='btn-import1b', n_clicks=0, outline=True, size='sm')
        #     ], className='w-100')
        # ], className="col-md-6"),
        html.Div([
            html.Label("Trade Type", className="form-label fw-semibold mb-1"),
            dbc.ButtonGroup([
                dbc.Button("Total", id='btn-total1b', n_clicks=0, outline=True, size='sm', color='primary'),
                dbc.Button("Exports", id='btn-export1b', n_clicks=0, outline=True, size='sm'),
                dbc.Button("Imports", id='btn-import1b', n_clicks=0, outline=True, size='sm')
            ], className='w-100')
        ], className="col-md-6", style={"border": "1px solid #ccc", "border-radius": "5px", "padding": "10px"}),

        # html.Div([
        #     html.Label("Display Type", className="form-label fw-semibold mb-1"),
        #     daq.ToggleSwitch(
        #         id='toggle-display1b',
        #         label='Percentage / Volume',
        #         value=True,
        #         className="mb-2"
        #     )
        # ], className="col-md-6"),
        html.Div([
            html.Label("Display Type", className="form-label fw-semibold mb-1 text-center w-100"),
            daq.ToggleSwitch(
                id='toggle-display1b',
                label='Volume / Percentage',
                value=True,
                className="mb-2",
                size=60)
        ], className="col-md-6 d-flex flex-column align-items-center"),

    ], className="row mb-4")
    ]),

    html.Div(id="tab-warning1b", className="text-danger mb-2 text-center"),

    dcc.Tabs(id="module1b-tabs", value="historical", children=[
        dcc.Tab(label="Historical", value="historical"),
        dcc.Tab(label="Prediction", value="prediction", id="prediction-tab1b", disabled=True),
    ]),

    html.Div(id="module1b-tab-content", className="mt-3"),

    html.Div([
        html.Div(id='country-title1b', style={'display': 'none'}),
        dcc.Graph(id='country-treemap1b', style={'display': 'none'}),
        dcc.Graph(id='country-bar1b', style={'display': 'none'})
    ], style={'display': 'none'})
])


app = get_app()

@app.callback(
    Output('trade-type-select1b', 'data'),
    Output('btn-total1b', 'color'),
    Output('btn-export1b', 'color'),
    Output('btn-import1b', 'color'),
    Input('btn-total1b', 'n_clicks'),
    Input('btn-export1b', 'n_clicks'),
    Input('btn-import1b', 'n_clicks'),
    prevent_initial_call=True
)
def update_trade_type(n_total, n_export, n_import):
    ctx = callback_context.triggered_id
    if ctx == 'btn-total1b':
        return 'total', 'primary', 'secondary', 'secondary'
    elif ctx == 'btn-export1b':
        return 'export', 'secondary', 'primary', 'secondary'
    elif ctx == 'btn-import1b':
        return 'import', 'secondary', 'secondary', 'primary'
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('display-type1b', 'data'),
    Input('toggle-display1b', 'value')
)
def update_display_type(value):
    return 'percentage' if value else 'volume'

@app.callback(
    Output("prediction-tab1b", "disabled"),
    Input("input-uploaded", "data")
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
    Input("module1b-tabs", "value"),
    State('display-type1b', 'data')
)
def render_tab_content(tab, display_type):
    if tab == "historical":
        return html.Div([
            html.Div(style={'marginTop': '20px'}),
            html.H5(id='country-title1b', className="text-center mb-2"),
            dcc.Graph(id='country-treemap1b', config={'displayModeBar': False}, style={"backgroundColor": "white", 'display': 'block' if display_type == 'percentage' else 'none'}),
            dcc.Graph(id='country-bar1b', config={'displayModeBar': False}, style={"backgroundColor": "white", 'display': 'block' if display_type == 'volume' else 'none'})
        ])
    elif tab == "prediction":
        return html.Div([
            html.H4("Prediction Results Coming Soon!", className="text-center mt-4"),
            html.P("This will show trade predictions based on uploaded news input.", className="text-center")
        ])

@app.callback(
    Output('country-treemap1b', 'figure'),
    Output('country-bar1b', 'figure'),
    Output('country-select-alt21b', 'options'),
    Output('country-title1b', 'children'),
    Input('country-select1b', 'value'),
    Input('trade-type-select1b', 'data'),
    Input('country-select-alt21b', 'value')
)
def update_visualizations(selected_country, trade_type, selected_partner):
    if trade_type == 'total':
        filtered = df[df['country'] == selected_country].copy()
    else:
        filtered = df[(df['country'] == selected_country) & (df['trade_type'] == trade_type)].copy()

    partner_options = [{'label': p, 'value': p} for p in sorted(filtered['partner_country'].unique())]
    view = filtered[filtered['partner_country'] == selected_partner] if selected_partner else filtered

    sector_agg = calculate_percentages(view, 'sector')

    if selected_partner:
        title = f"{trade_type.capitalize()}s from {selected_country} to {selected_partner} by Sector"
    else:
        title = f"{selected_country}'s {trade_type.capitalize()} by Sector"

    # title = f"{trade_type.capitalize()}s by Sector"
    # if selected_partner:
    #     title = f"{trade_type.capitalize()}s from {selected_country} to {selected_partner} by Sector"

    for df_agg in [sector_agg]:
        df_agg['percentage'] = df_agg['percentage'].round(1)
        df_agg['change_str'] = df_agg['change'].apply(lambda x: f"{x:+.2f}%")
        df_agg['volume_fmt'] = df_agg['volume'].apply(lambda x: f"{x:,.0f}")
        df_agg['previous_volume_fmt'] = df_agg['previous_volume'].apply(lambda x: f"{x:,.0f}")

    max_change = sector_agg['change'].abs().max() * 5
    hover_template = '<b>%{label}</b><br>Share: %{customdata[0]}%<br>Change: %{customdata[1]}<br>Volume: %{customdata[2]}<br>Prev Volume: %{customdata[3]}'

    fig_treemap = px.treemap(sector_agg, path=['sector'], values='percentage', color='change_clipped',
                              color_continuous_scale=[[0, '#d73027'], [0.5, '#f7f7f7'], [1, '#1a9850']],
                              range_color=[-max_change, max_change], color_continuous_midpoint=0,
                              custom_data=['percentage', 'change_str', 'volume_fmt', 'previous_volume_fmt'])
    fig_treemap.update_traces(hovertemplate=hover_template, texttemplate='<b>%{label}</b><br>%{customdata[0]}% (%{customdata[1]})')
    fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False)

    fig_bar = generate_bar_chart(sector_agg, 'sector', 'volume', 'previous_volume')

    return fig_treemap, fig_bar, partner_options, title

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

def generate_bar_chart(df, x_col, y_col, previous_col):
    df_sorted = df.sort_values(y_col, ascending=False)
    df_sorted['change'] = 100 * (df_sorted[y_col] - df_sorted[previous_col]) / df_sorted[previous_col].replace(0, 1)
    df_sorted['hover'] = df_sorted.apply(lambda row: f"Current: {row[y_col]:,.0f}<br>Previous: {row[previous_col]:,.0f}<br>Change: {row['change']:+.2f}%", axis=1)

    fig = px.bar(df_sorted, x=x_col, y=y_col, text=df_sorted[y_col].apply(lambda x: f"{x:,.0f}"),
                 labels={x_col: x_col.title(), y_col: y_col.title()}, hover_data={'hover': True}, color_discrete_sequence=['#2c7bb6'])
    fig.add_bar(x=df_sorted[x_col], y=df_sorted[previous_col], opacity=0.5, name="Previous Period",
                marker_color='#a6bddb')
    fig.update_traces(hovertemplate=df_sorted['hover'])
    fig.update_layout(barmode='overlay', font=dict(family='Open Sans, sans-serif'),
                      legend=dict(x=0.99, y=0.99, xanchor='right', yanchor='top'),
                      plot_bgcolor='white', paper_bgcolor='white',
                      margin=dict(t=30, l=10, r=10, b=10))
    return fig


sidebar_controls = html.Div([])