import warnings
warnings.filterwarnings("ignore", message="A nonexistent object was used in an `Input` of a Dash callback.")

import dash
from dash import dcc, html, Output, Input, callback_context
import dash_bootstrap_components as dbc

# Initialize
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Import layouts
from index import layout as index_layout
from apps import module1a, module1b, module2, module3a, module3b, module4a, module4b, module4c, module5a, module5b, module5c

# Top Navbar with Dropdowns - might need to change dropdown style
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("Dashboard", className="ms-2 text-white", style={"fontSize": "1.6rem"}),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/", className="mx-3 fs-5", active="exact")),
                dbc.DropdownMenu(label="Module 1", children=[
                    dbc.DropdownMenuItem("Module 1A", href="/module1a"),
                    dbc.DropdownMenuItem("Module 1B", href="/module1b"),
                ], nav=True, in_navbar=True, className="mx-3 fs-5"),
                dbc.NavItem(dbc.NavLink("Module 2", href="/module2", className="mx-3 fs-5", active="exact")),
                dbc.DropdownMenu(label="Module 3", children=[
                    dbc.DropdownMenuItem("Module 3A", href="/module3a"),
                    dbc.DropdownMenuItem("Module 3B", href="/module3b"),
                ], nav=True, in_navbar=True, className="mx-3 fs-5"),
                dbc.DropdownMenu(label="Module 4", children=[
                    dbc.DropdownMenuItem("Module 4A", href="/module4a"),
                    dbc.DropdownMenuItem("Module 4B", href="/module4b"),
                    dbc.DropdownMenuItem("Module 4C", href="/module4c"),
                ], nav=True, in_navbar=True, className="mx-3 fs-5"),
                dbc.DropdownMenu(label="Module 5", children=[
                    dbc.DropdownMenuItem("Module 5A", href="/module5a"),
                    dbc.DropdownMenuItem("Module 5B", href="/module5b"),
                    dbc.DropdownMenuItem("Module 5C", href="/module5c"),
                ], nav=True, in_navbar=True, className="mx-3 fs-5"),
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            navbar=True
        )
    ]),
    color="primary",
    dark=True,
    fixed="top",
    className="mb-4 px-4"
)

# === App Layout ===
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    html.Div(id="sidebar-dynamic", style={"margin": "1rem 2rem"}),
    html.Div(id="page-content", style={"padding": "2rem 2rem 2rem 2rem", "marginTop": "5rem"})
])

# === Page Router ===
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/module1a":
        return module1a.layout
    elif pathname == "/module1b":
        return module1b.layout
    elif pathname == "/module2":
        return module2.layout
    elif pathname == "/module3a":
        return module3a.layout
    elif pathname == "/module3b":
        return module3b.layout
    elif pathname == "/module4a":
        return module4a.layout
    elif pathname == "/module4b":
        return module4b.layout
    elif pathname == "/module4c":
        return module4c.layout
    elif pathname == "/module5a":
        return module5a.layout
    elif pathname == "/module5b":
        return module5b.layout
    elif pathname == "/module5c":
        return module5c.layout
    elif pathname == "/" or pathname == "":
        return index_layout
    return html.Div("404 - Page not found")

# === Dynamic Sidebar Callback ===
@app.callback(Output("sidebar-dynamic", "children"), Input("url", "pathname"))
def update_sidebar(pathname):
    if pathname == "/module1a":
        return module1a.sidebar_controls
    elif pathname == "/module1b":
        return module1b.sidebar_controls
    elif pathname == "/module2":
        return module2.sidebar_controls
    elif pathname == "/module3a":
        return module3a.sidebar_controls
    elif pathname == "/module3b":
        return module3b.sidebar_controls
    elif pathname == "/module4a":
        return module4a.sidebar_controls
    elif pathname == "/module4b":
        return module4b.sidebar_controls
    elif pathname == "/module4c":
        return module4c.sidebar_controls
    elif pathname == "/module5a":
        return module5a.sidebar_controls
    elif pathname == "/module5b":
        return module5b.sidebar_controls
    elif pathname == "/module5c":
        return module5c.sidebar_controls
    else:
        return None

# === Navigation from Homepage (e.g., click bar/image) -- include stat boxes clickability here -- 
@app.callback(
    Output("url", "pathname"),
    [Input("go-to-module1", "n_clicks"),
     Input("go-to-module2", "n_clicks")],
    prevent_initial_call=True
)
def navigate(go1, go2):
    ctx = callback_context.triggered_id
    if ctx == "go-to-module1" and go1:
        return "/module1a"
    elif ctx == "go-to-module2" and go2:
        return "/module2"
    return dash.no_update

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True)
