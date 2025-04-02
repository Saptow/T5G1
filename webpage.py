# === app.py ===
# ✅ This is the MAIN entrypoint for your multi-page Dash app

import dash
from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc



# ✅ Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
server = app.server  # Required for deployment (e.g., Heroku, gunicorn)

# Import layouts from modules
from index import layout as index_layout
from apps import module1  # You can add more later like module2, module3, etc.

# ✅ Sidebar (left side)
sidebar = html.Div([
    html.H2("Dashboard", className="display-6"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Home", href="/", active="exact"),
        dbc.NavLink("Trade Explorer", href="/module1", active="exact"),  # Name as you like
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

# ✅ App layout with dynamic content loading
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div(id="page-content", style={"margin-left": "18rem", "padding": "2rem 1rem"})
])

# ✅ Routing Logic
@app.callback(Output("page-content", "children"),
              Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/module1":
        return module1.layout
    else:
        return index_layout  # Default is the front page

# ✅ Start server
if __name__ == '__main__':
    app.run(debug=True)
