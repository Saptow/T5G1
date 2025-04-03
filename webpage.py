import dash
from dash import dcc, html, Output, Input, callback_context
import dash_bootstrap_components as dbc

# Initialize
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Import layouts
from index import layout as index_layout
from apps import module1, module2, module3  # Add more modules here

# === Sidebar (static nav + dynamic section below) ===
sidebar = html.Div([
    html.H2("Dashboard", className="display-6"),
    html.Hr(),

    # Static Nav Tabs
    dbc.Nav([
        dbc.NavLink("Home", href="/", active="exact"),
        dbc.NavLink("Trade Explorer", href="/module1", active="exact"),
        dbc.NavLink("WorldMap", href="/module2", active="exact"),
        dbc.NavLink("Bubble Chart", href="/module3", active="exact")
        # Add more tabs here as needed
    ], vertical=True, pills=True),

    html.Hr(),

    # ✅ This is the ONLY sidebar-dynamic block (do NOT duplicate)
    html.Div(id="sidebar-dynamic")
], style={
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflowY": "auto"
})

# === App Layout ===
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,  # includes nav + dynamic
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

# === Dynamic Sidebar Callback ===
@app.callback(
    Output("sidebar-dynamic", "children"),
    Input("url", "pathname")
)
def update_sidebar(pathname):
    if pathname == "/module1":
        return module1.sidebar_controls
    elif pathname == "/module2":
        return module2.sidebar_controls
    elif pathname == "/module3":
        return module3.sidebar_controls
    # Add additional elif blocks for future modules
    else:
        return None  # No sidebar controls on homepage

# === Navigation from Homepage (e.g., click bar/image) ===
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

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True)
