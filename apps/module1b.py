from dash import html, dcc, Input, Output, State, callback, ALL, ctx
import dash
import pandas as pd
import plotly.graph_objects as go

# === Load data ===
df = pd.read_csv("sample_trade_data_2015_2024_2026_FIXED.csv")

# === Define sectors and readable labels ===
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

sectors = sorted(df["Sector Group"].unique())
default_sector = "Sector_1"

# === Dash Layout ===
layout = html.Div([
    dcc.Store(id='selected-sector', data=default_sector),

    html.H2("Module 1B: Yearly percentage share of sectors", className="mb-4"),

    html.Div([
        html.Div([
            html.Label("Select a Country", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df['Reporter'].unique())],
                value=sorted(df['Reporter'].unique())[0],
                placeholder="Select a country",
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6"),
        html.Div([
            html.Label("Select a Partner", className="form-label fw-semibold mb-1"),
            dcc.Dropdown(
                id='partner-dropdown',
                options=[
                    {'label': 'All', 'value': 'All'},
                    {'label': 'Top 3', 'value': 'Top 3'},
                    {'label': 'Top 5', 'value': 'Top 5'}
                ] + [{'label': p, 'value': p} for p in sorted(df['Partner'].unique())],
                value='All',
                placeholder="Select a partner country",
                className="mb-3",
                style={"width": "100%"}
            )
        ], className="col-md-6")
    ], className="row mb-4"),

    html.Div([
        html.Div([
            html.Button(
                sector_labels.get(sector, sector),
                id={'type': 'sector-btn', 'index': sector},
                n_clicks=0,
                className="btn me-2 mb-2"
            )
            for sector in sectors
        ], className="d-flex flex-wrap")
    ], className="mb-4"),

    dcc.Tabs(id='module1b-tabs', value='percent-tab', children=[
        dcc.Tab(label='Sector Percentage Share', value='percent-tab'),
        dcc.Tab(label='Year on Year Changes', value='change-tab')
    ]),

    html.Div(id='module1b-tab-content')
])

# === Sector Selection Callback ===
@callback(
    Output('selected-sector', 'data'),
    Input({'type': 'sector-btn', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_selected_sector(n_clicks):
    triggered = ctx.triggered_id
    if isinstance(triggered, dict) and triggered.get('type') == 'sector-btn':
        return triggered['index']
    return dash.no_update

# === Style Buttons Based on Active Sector ===
@callback(
    Output({'type': 'sector-btn', 'index': ALL}, 'className'),
    Input('selected-sector', 'data'),
    [State({'type': 'sector-btn', 'index': ALL}, 'id')]
)
def highlight_active_button(selected_sector, all_ids):
    return [
        "btn btn-primary me-2 mb-2" if btn_id['index'] == selected_sector else "btn btn-outline-primary me-2 mb-2"
        for btn_id in all_ids
    ]

# === Graph + Title + Partner Info Callback ===
# @callback(
#     Output('module1b-tab-content', 'children'),
#     Input('country-dropdown', 'value'),
#     Input('partner-dropdown', 'value'),
#     Input('selected-sector', 'data'),
#     Input('module1b-tabs', 'value')
# )
# def update_graph(selected_country, selected_partner, selected_sector, active_tab):
#     filtered = df[(df['Reporter'] == selected_country) & (df['Sector Group'] == selected_sector)]
#     top_countries_list = []
#     partner_text = ""
#     ranked_list_items = []
#     top_n = 0  # default in case not Top 3/5

#     if selected_partner in ['Top 3', 'Top 5']:
#         top_n = int(selected_partner.split()[-1])
#         top_group = (
#             filtered.groupby('Partner', as_index=False)['Total Trade Volume']
#             .sum().sort_values(by='Total Trade Volume', ascending=False)
#         )
#         total_top = top_group['Total Trade Volume'].sum()
#         top_partners = top_group.head(top_n)

#         top_countries_list = top_partners['Partner'].tolist()
#         filtered = filtered[filtered['Partner'].isin(top_countries_list)]
#         partner_text = f" with Top {top_n} Partners"

#         # Ranked list with percentages
#         for i, row in enumerate(top_partners.itertuples(), 1):
#             pct = (row._2 / total_top) * 100 if total_top else 0
#             item_text = f"{i}. {row.Partner} ({pct:.2f}%)"
#             tooltip = f"{row.Partner}: {row._2:,.0f}"
#             ranked_list_items.append(html.Li(item_text, title=tooltip))

#     elif selected_partner != 'All':
#         filtered = filtered[filtered['Partner'] == selected_partner]
#         partner_text = f" with {selected_partner}"

#     filtered = filtered[filtered['Year'].between(2015, 2024)]

#     grouped = filtered.groupby('Year', as_index=False).agg({'Total Trade Volume': 'sum'})
#     total_trade = filtered['Total Trade Volume'].sum()
#     grouped['percentage'] = 100 * grouped['Total Trade Volume'] / total_trade if total_trade else 0
#     grouped['gap'] = 100 - grouped['percentage']
#     grouped['change'] = grouped['percentage'].diff().fillna(0).round(1)

#     max_y = min(100, grouped['percentage'].max() * 2)

#     # === Bar Graph
#     fig = go.Figure()
#     fig.add_trace(go.Bar(
#         x=grouped['Year'],
#         y=grouped['percentage'],
#         marker_color='#00BFC4',
#         width=0.3,
#         name='',
#         text=grouped['percentage'].round(1).astype(str) + '%',
#         textposition='outside',
#         textangle=0,
#         textfont=dict(color='black', size=12),
#         hovertemplate='%{y:.1f}%<br>Change: %{customdata[0]:+.1f}%',
#         customdata=grouped[['change']].values,
#         showlegend=False
#     ))

#     fig.add_trace(go.Bar(
#         x=grouped['Year'],
#         y=max_y - grouped['percentage'],
#         marker_color='lightgrey',
#         width=0.3,
#         name='',
#         hoverinfo='skip',
#         showlegend=False
#     ))

#     fig.update_layout(
#         xaxis=dict(tickmode='linear', tick0=2015, dtick=1, showgrid=False),
#         yaxis=dict(range=[0, max_y], showgrid=False, zeroline=False),
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         template='plotly_white',
#         barmode='stack',
#         bargap=0.5,
#         showlegend=False
#     )

#     # === Line Graph
#     line_fig = go.Figure()
#     line_fig.add_trace(go.Scatter(
#         x=grouped['Year'],
#         y=grouped['change'],
#         mode='lines+markers',
#         line=dict(color='#636EFA'),
#         marker=dict(size=12, color='#636EFA'),
#         text=grouped['change'].astype(str) + '%',
#         hovertemplate='%{x}: %{y:+.1f}%',
#         showlegend=False
#     ))

#     line_fig.update_layout(
#         xaxis=dict(tickmode='linear', tick0=2015, dtick=1),
#         yaxis_title="% Change from Previous Period",
#         plot_bgcolor='white',
#         paper_bgcolor='white',
#         template='plotly_white'
#     )

#     # === Title + Top Partner List (Right-Aligned)
#     title_text = f"{sector_labels.get(selected_sector, selected_sector)} Trade for {selected_country}{partner_text} (2015–2024)"
#     spacer = html.Div(style={"height": "20px"})

#     title_row = html.Div([
#         html.H5(title_text, className="mb-0 me-auto")
#     ], className="d-flex justify-content-between align-items-center mb-2")

#     separator = html.Hr(className="mb-3 mt-2")

#     # Right side list (vertically centered now)
#     right_side_list = html.Div([
#         html.H6(f"Top {top_n} Partners", className="fw-semibold mb-2") if top_n else None,
#         html.Ul(ranked_list_items, style={"fontSize": "1rem", "paddingLeft": "1rem", "margin": 0})
#     ], style={"minWidth": "260px", "marginLeft": "32px", "flexShrink": 0}) if ranked_list_items else None

#     # Graph block
#     graph_block = html.Div([
#         dcc.Graph(figure=fig if active_tab == 'percent-tab' else line_fig)
#     ], style={"flex": "1 1 auto", "minWidth": 0})

#     return html.Div([
#         spacer,
#         title_row,
#         separator,
#         html.Div([
#             graph_block,
#             right_side_list
#         ], className="d-flex flex-row align-items-center")
#     ])

# @callback(
#     Output('module1b-tab-content', 'children'),
#     Input('country-dropdown', 'value'),
#     Input('partner-dropdown', 'value'),
#     Input('selected-sector', 'data'),
#     Input('module1b-tabs', 'value')
# )
# def update_graph(selected_country, selected_partner, selected_sector, active_tab):
    filtered = df[(df['Reporter'] == selected_country) & (df['Sector Group'] == selected_sector)]
    top_countries_list = []
    partner_text = ""
    ranked_list_items = []
    top_n = 0

    if selected_partner in ['Top 3', 'Top 5']:
        top_n = int(selected_partner.split()[-1])
        top_group = (
            filtered.groupby('Partner', as_index=False)['Total Trade Volume']
            .sum().sort_values(by='Total Trade Volume', ascending=False)
        )
        total_top = top_group['Total Trade Volume'].sum()
        top_partners = top_group.head(top_n)

        top_countries_list = top_partners['Partner'].tolist()
        filtered = filtered[filtered['Partner'].isin(top_countries_list)]
        partner_text = f" with Top {top_n} Partners"

        for i, row in enumerate(top_partners.itertuples(), 1):
            pct = (row._2 / total_top) * 100 if total_top else 0
            item_text = f"{i}. {row.Partner} ({pct:.2f}%)"
            tooltip = f"{row.Partner}: {row._2:,.0f}"
            ranked_list_items.append(html.Li(item_text, title=tooltip))

    elif selected_partner != 'All':
        filtered = filtered[filtered['Partner'] == selected_partner]
        partner_text = f" with {selected_partner}"

    # Only include years 2015–2023 and 2026 (skip 2024–2025)
    filtered = filtered[filtered['Year'].isin([y for y in range(2015, 2024)] + [2026])]

    grouped = filtered.groupby('Year', as_index=False).agg({'Total Trade Volume': 'sum'})
    total_trade = filtered['Total Trade Volume'].sum()
    grouped['percentage'] = 100 * grouped['Total Trade Volume'] / total_trade if total_trade else 0
    grouped['gap'] = 100 - grouped['percentage']
    grouped['change'] = grouped['percentage'].diff().fillna(0).round(1)

    max_y = min(100, grouped['percentage'].max() * 2)

    # === Bar Graph
    bar_years = [y for y in range(2015, 2024)] + [2026]
    grouped_bar = grouped[grouped['Year'].isin(bar_years)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped_bar['Year'],
        y=grouped_bar['percentage'],
        marker_color='#00BFC4',
        width=0.3,
        name='',
        text=grouped_bar['percentage'].round(1).astype(str) + '%',
        textposition='outside',
        textangle=0,
        textfont=dict(color='black', size=12),
        hovertemplate='%{y:.1f}%<br>Change: %{customdata[0]:+.1f}%',
        customdata=grouped_bar[['change']].values,
        showlegend=False
    ))

    fig.add_trace(go.Bar(
        x=grouped_bar['Year'],
        y=max_y - grouped_bar['percentage'],
        marker_color='lightgrey',
        width=0.3,
        name='',
        hoverinfo='skip',
        showlegend=False
    ))

    fig.update_layout(
        #xaxis=dict(tickmode='linear', tick0=2015, dtick=1, showgrid=False),
        xaxis=dict(tickmode='array', tickvals=grouped_bar['Year'],  # or grouped_bar['Year'] depending on chart
        showgrid=False),

        yaxis=dict(range=[0, max_y], showgrid=False, zeroline=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly_white',
        barmode='stack',
        bargap=0.5,
        showlegend=False
    )

    # === Line Graph
    line_years = [y for y in range(2015, 2024)] + [2026]
    grouped_line = grouped[grouped['Year'].isin(line_years)]

    default_years = grouped_line[~grouped_line['Year'].isin([2026])]
    future_year = grouped_line[grouped_line['Year'] == 2026]

    line_fig = go.Figure()

    line_fig.add_trace(go.Scatter(
        x=default_years['Year'],
        y=default_years['change'],
        mode='lines+markers',
        line=dict(color='#636EFA'),
        marker=dict(size=12, color='#636EFA'),
        text=default_years['change'].astype(str) + '%',
        hovertemplate='%{x}: %{y:+.1f}%',
        showlegend=False
    ))
    # Add annotation for forecast
    line_fig.add_annotation(
        x=2026,
        y=future_year['change'].values[0],
        text="Forecast",
        showarrow=False,
        font=dict(color="red", size=12),
        yshift=30
    )  


    if not default_years.empty and not future_year.empty:
        last_year = default_years['Year'].max()
        last_val = default_years[default_years['Year'] == last_year]['change'].values[0]
        future_val = future_year['change'].values[0]
        line_fig.add_trace(go.Scatter(
            x=[last_year, 2026],
            y=[last_val, future_val],
            mode='lines',
            line=dict(color='red', dash='dot'),
            hoverinfo='skip',
            showlegend=False
        ))

    if not future_year.empty:
        line_fig.add_trace(go.Scatter(
            x=future_year['Year'],
            y=future_year['change'],
            mode='markers+text',
            marker=dict(size=12, color='red'),
            text=future_year['change'].astype(str) + '%',
            textposition='top center',
            hovertemplate='%{x}: %{y:+.1f}%',
            showlegend=False
        ))

    # === Title + Top Partner List
    title_text = f"{sector_labels.get(selected_sector, selected_sector)} Trade for {selected_country}{partner_text} (2015–2026)"
    spacer = html.Div(style={"height": "20px"})

    title_row = html.Div([
        html.H5(title_text, className="mb-0 me-auto")
    ], className="d-flex justify-content-between align-items-center mb-2")

    separator = html.Hr(className="mb-3 mt-2")

    right_side_list = html.Div([
        html.H6(f"Top {top_n} Partners", className="fw-semibold mb-2") if top_n else None,
        html.Ul(ranked_list_items, style={"fontSize": "1rem", "paddingLeft": "1rem", "margin": 0})
    ], style={"minWidth": "260px", "marginLeft": "32px", "flexShrink": 0}) if ranked_list_items else None

    graph_block = html.Div([
        dcc.Graph(figure=fig if active_tab == 'percent-tab' else line_fig)
    ], style={"flex": "1 1 auto", "minWidth": 0})

    return html.Div([
        spacer,
        title_row,
        separator,
        html.Div([
            graph_block,
            right_side_list
        ], className="d-flex flex-row align-items-center")
    ])

@callback(
    Output('module1b-tab-content', 'children'),
    Input('country-dropdown', 'value'),
    Input('partner-dropdown', 'value'),
    Input('selected-sector', 'data'),
    Input('module1b-tabs', 'value')
)
def update_graph(selected_country, selected_partner, selected_sector, active_tab):
    filtered = df[(df['Reporter'] == selected_country) & (df['Sector Group'] == selected_sector)]
    top_countries_list = []
    partner_text = ""
    ranked_list_items = []
    top_n = 0

    if selected_partner in ['Top 3', 'Top 5']:
        top_n = int(selected_partner.split()[-1])
        top_group = (
            filtered.groupby('Partner', as_index=False)['Total Trade Volume']
            .sum().sort_values(by='Total Trade Volume', ascending=False)
        )
        total_top = top_group['Total Trade Volume'].sum()
        top_partners = top_group.head(top_n)

        top_countries_list = top_partners['Partner'].tolist()
        filtered = filtered[filtered['Partner'].isin(top_countries_list)]
        partner_text = f" with Top {top_n} Partners"

        for i, row in enumerate(top_partners.itertuples(), 1):
            pct = (row._2 / total_top) * 100 if total_top else 0
            item_text = f"{i}. {row.Partner} ({pct:.2f}%)"
            tooltip = f"{row.Partner}: {row._2:,.0f}"
            ranked_list_items.append(html.Li(item_text, title=tooltip))

    elif selected_partner != 'All':
        filtered = filtered[filtered['Partner'] == selected_partner]
        partner_text = f" with {selected_partner}"

    # Only include years 2015–2023 and 2026 (skip 2024–2025)
    included_years = [y for y in range(2015, 2024)] + [2026]
    filtered = filtered[filtered['Year'].isin(included_years)]

    grouped = filtered.groupby('Year', as_index=False).agg({'Total Trade Volume': 'sum'})
    total_trade = filtered['Total Trade Volume'].sum()
    grouped['percentage'] = 100 * grouped['Total Trade Volume'] / total_trade if total_trade else 0
    grouped['gap'] = 100 - grouped['percentage']
    grouped['change'] = grouped['percentage'].diff().fillna(0).round(1)

    # Convert year to string to treat x-axis as categorical
    grouped['Year'] = grouped['Year'].astype(str)

    max_y = min(100, grouped['percentage'].max() * 2)

    # === Bar Graph
    grouped_bar = grouped[grouped['Year'].isin([str(y) for y in included_years])]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped_bar['Year'],
        y=grouped_bar['percentage'],
        marker_color='#00BFC4',
        width=0.3,
        name='',
        text=grouped_bar['percentage'].round(1).astype(str) + '%',
        textposition='outside',
        textangle=0,
        textfont=dict(color='black', size=12),
        hovertemplate='%{y:.1f}%<br>Change: %{customdata[0]:+.1f}%',
        customdata=grouped_bar[['change']].values,
        showlegend=False
    ))

    fig.add_trace(go.Bar(
        x=grouped_bar['Year'],
        y=max_y - grouped_bar['percentage'],
        marker_color='lightgrey',
        width=0.3,
        name='',
        hoverinfo='skip',
        showlegend=False
    ))

    fig.update_layout(
        xaxis=dict(type='category', showgrid=False),
        yaxis=dict(range=[0, max_y], showgrid=False, zeroline=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly_white',
        barmode='stack',
        bargap=0.5,
        showlegend=False
    )

    # === Line Graph
    grouped_line = grouped[grouped['Year'].astype(int).isin(included_years)].sort_values(by='Year')
    grouped_line['Year'] = grouped_line['Year'].astype(str)

    default_years = grouped_line[~grouped_line['Year'].isin(["2026"])]
    future_year = grouped_line[grouped_line['Year'] == "2026"]

    line_fig = go.Figure()

    line_fig.add_trace(go.Scatter(
        x=default_years['Year'],
        y=default_years['change'],
        mode='lines+markers',
        line=dict(color='#636EFA'),
        marker=dict(size=12, color='#636EFA'),
        text=default_years['change'].astype(str) + '%',
        hovertemplate='%{x}: %{y:+.1f}%',
        showlegend=False
    ))

    # Add forecast annotation and dotted line
    if not default_years.empty and not future_year.empty:
        last_year = default_years['Year'].max()
        last_val = default_years[default_years['Year'] == last_year]['change'].values[0]
        future_val = future_year['change'].values[0]
        line_fig.add_trace(go.Scatter(
            x=[last_year, "2026"],
            y=[last_val, future_val],
            mode='lines',
            line=dict(color='red', dash='dot'),
            hoverinfo='skip',
            showlegend=False
        ))

        line_fig.add_trace(go.Scatter(
            x=["2026"],
            y=[future_val],
            mode='markers+text',
            marker=dict(size=12, color='red'),
            text=[f"{future_val:+.1f}%"],
            textposition='top center',
            hovertemplate='%{x}: %{y:+.1f}%',
            showlegend=False
        ))

        line_fig.add_annotation(
            x="2026",
            y=future_val,
            text="Forecast",
            showarrow=False,
            font=dict(color="red", size=12),
            yshift=30
        )

    line_fig.update_layout(
        xaxis=dict(type='category', categoryorder='array', categoryarray=[2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2026],
        showgrid=False),
        yaxis_title="% Change from Previous Period",
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly_white'
    )

    # === Title + Top Partner List
    title_text = f"{sector_labels.get(selected_sector, selected_sector)} Trade for {selected_country}{partner_text} (2015–2026)"
    spacer = html.Div(style={"height": "20px"})

    title_row = html.Div([
        html.H5(title_text, className="mb-0 me-auto")
    ], className="d-flex justify-content-between align-items-center mb-2")

    separator = html.Hr(className="mb-3 mt-2")

    right_side_list = html.Div([
        html.H6(f"Top {top_n} Partners", className="fw-semibold mb-2") if top_n else None,
        html.Ul(ranked_list_items, style={"fontSize": "1rem", "paddingLeft": "1rem", "margin": 0})
    ], style={"minWidth": "260px", "marginLeft": "32px", "flexShrink": 0}) if ranked_list_items else None

    graph_block = html.Div([
        dcc.Graph(figure=fig if active_tab == 'percent-tab' else line_fig)
    ], style={"flex": "1 1 auto", "minWidth": 0})

    return html.Div([
        spacer,
        title_row,
        separator,
        html.Div([
            graph_block,
            right_side_list
        ], className="d-flex flex-row align-items-center")
    ])


sidebar_controls = html.Div([])