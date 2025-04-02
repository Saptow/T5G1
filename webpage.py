import dash
from dash import dcc, html, Output, Input, callback_context
import dash_bootstrap_components as dbc

# Initialize
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Import layouts
from index import layout as index_layout
from apps import module1, module2, module3

# === Sidebar ===
sidebar = html.Div([
    html.H2("Dashboard", className="display-6"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Home", href="/", active="exact"),
        dbc.NavLink("Trade Explorer", href="/module1", active="exact"),
        dbc.NavLink("WorldMap", href="/module2", active="exact"),
        dbc.NavLink("Bubble Chart", href="/module3", active="exact")
    ], vertical=True, pills=True),
], style={
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
})

# === App Layout ===
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div(id="page-content", style={"margin-left": "18rem", "padding": "2rem 1rem"})
])

# === Page Router ===
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/module1":
        return module1.layout
    elif pathname == "/module2":
        return module2.layout
    elif pathname == "/module3":
        return module3.layout
    elif pathname == "/" or pathname == "":
        return index_layout
    return index_layout

# === Navigation Trigger from Homepage Elements ===
@app.callback(
    Output("url", "pathname"),
    [Input("go-to-module1", "n_clicks"),
     Input("go-to-module2", "n_clicks")],
    prevent_initial_call=True
)
def navigate(go1, go2):
    ctx = callback_context.triggered_id

    if ctx == "go-to-module1" and go1:
        return "/module1"
    elif ctx == "go-to-module2" and go2:
        return "/module2"

    return dash.no_update


# Run server
if __name__ == '__main__':
    app.run(debug=True)
