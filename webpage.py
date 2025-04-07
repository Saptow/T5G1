import warnings
warnings.filterwarnings("ignore", message="A nonexistent object was used in an `Input` of a Dash callback.")

import dash
from dash import dcc, html, Output, Input, callback_context, State
import dash_bootstrap_components as dbc
from dash import ctx

# Initialize
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Import layouts
from index import layout as index_layout
from apps import module1a, module1b, module2, module3a, module3b, module4a, module4b, module4c, module5a, module5b, module5c, module5

# Top Navbar with Dropdowns - might need to change dropdown style
# navbar = dbc.Navbar(
#     dbc.Container([
#         dbc.NavbarBrand("Dashboard", className="ms-2 text-white", style={"fontSize": "1.6rem"}),
#         dbc.NavbarToggler(id="navbar-toggler"),
#         dbc.Collapse(
#             dbc.Nav([
#                 dbc.NavItem(dbc.NavLink("Home", href="/", className="mx-3 fs-5", active="exact")),
#                 dbc.DropdownMenu(label="Sector Statistics", children=[
#                     dbc.DropdownMenuItem("top N partner country for sector", href="/module1a"),
#                     dbc.DropdownMenuItem("sector share change over time", href="/module1b"),
#                 ], nav=True, in_navbar=True, className="mx-3 fs-5"),
#                 dbc.NavItem(dbc.NavLink("Trade Map", href="/module2", className="mx-3 fs-5", active="exact")),
#                 dbc.DropdownMenu(label="Country Statistics", children=[
#                     dbc.DropdownMenuItem("top N partner country for sector", href="/module3a"),
#                     dbc.DropdownMenuItem("sector share change over time", href="/module3b"),
#                 ], nav=True, in_navbar=True, className="mx-3 fs-5"),
#                 dbc.DropdownMenu(label="Geopolitical Trade Statistics", children=[
#                     dbc.DropdownMenuItem("Trade Balance by Year", href="/module4a"),
#                     dbc.DropdownMenuItem("Trade Volume over Time", href="/module4b"),
#                 ], nav=True, in_navbar=True, className="mx-3 fs-5"),
#                 dbc.NavItem(dbc.NavLink("News Impact on Forecast", href="/module5", className="mx-3 fs-5", active="exact")),
#             ], className="ms-auto", navbar=True),
#             id="navbar-collapse",
#             navbar=True
#         )
#     ]),
#     color="primary",
#     dark=True,
#     fixed="top",
#     className="mb-4 px-4"
# )

### For uncommenting 

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("Dashboard", className="ms-2 text-white", style={"fontSize": "1.6rem"}),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/", className="mx-3 fs-5", active="exact")),
                dbc.DropdownMenu(label="Sector Statistics", children=[
                    dbc.DropdownMenuItem("top N partner country for sector", href="/module1a"),
                    dbc.DropdownMenuItem("sector share change over time", href="/module1b"),
                ], nav=True, in_navbar=True, className="mx-3 fs-5"),
                dbc.NavItem(dbc.NavLink("Trade Map", href="/module2", className="mx-3 fs-5", active="exact")),
                dbc.DropdownMenu(label="Country Statistics", children=[
                    dbc.DropdownMenuItem("top N partner country for sector", href="/module3a"),
                    dbc.DropdownMenuItem("sector share change over time", href="/module3b"),
                ], nav=True, in_navbar=True, className="mx-3 fs-5"),
                dbc.DropdownMenu(label="Geopolitical Trade Statistics", children=[
                    dbc.DropdownMenuItem("Trade Balance by Year", href="/module4a"),
                    dbc.DropdownMenuItem("Trade Volume over Time", href="/module4b"),
                ], nav=True, in_navbar=True, className="mx-3 fs-5"),
                dbc.NavItem(dbc.NavLink("News Impact on Forecast", href="/module5", className="mx-3 fs-5", active="exact")),
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            navbar=True
        ),

        # RIGHT-ALIGNED PREDICT BUTTON (not inside the Collapse/nav)
        dbc.Button("Predict", id="open-predict", color="light", className="ms-3"),

        # Offcanvas that opens from right
        dbc.Offcanvas(
    id="predict-offcanvas",
    title="Prediction Input",
    is_open=False,
    placement="end",
    children=[
        # URL Input
        dbc.InputGroup([
            dbc.Input(id="news-url-input", placeholder="Paste URL here...", type="url"),
            dbc.Button("Go", id="submit-url", n_clicks=0, color="primary"),
        ], className="mb-4"),

        html.Hr(),

        # Clickable article images
        html.Div([
            html.H5("Or choose a sample article:"),

            html.Img(src="/assets/news1.png", id="article-img-1", n_clicks=0,
             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),

            html.Img(src="/assets/news2.png", id="article-img-2", n_clicks=0,
             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),

            html.Img(src="/assets/news3.png", id="article-img-3", n_clicks=0,
             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),
        ]), 
        #html.Div(id="predict-confirmation", className="text-success mt-3 fw-semibold")
        # html.Div(id="predict-confirmation", className="mt-3 fw-semibold"),
        # html.Div(id="input-status-message", className="mt-2"),
        html.Div(id="predict-confirmation", className="mt-3 fw-semibold"),
        html.Div(id="input-status-message", className="mt-2 text-muted"),

    ],
)
,
    ]),
    color="primary",
    dark=True,
    fixed="top",
    className="mb-4 px-4"
)



# # === App Layout ===
# app.layout = html.Div([
#     dcc.Location(id="url"),
#     dcc.Store(id="uploaded-url"),
#     dcc.Store(id="input-uploaded", data=False),  # Initial state: not uploaded
#     #dcc.Store(id="uploaded-url", data=None),     # to track the exact URL or image clicked
#     navbar,
#     dbc.Offcanvas(
#         id="predict-offcanvas",
#         title="Prediction Input",
#         is_open=False,
#         placement="end",
#         children=[
#             dbc.InputGroup([
#                 dbc.Input(id="news-url-input", placeholder="Paste URL here...", type="url"),
#                 dbc.Button("Go", id="submit-url", n_clicks=0, color="primary"),
#             ], className="mb-4"),

#             html.Hr(),

#             html.Div([
#                 html.H5("Or choose a sample article:"),

#                 html.Img(src="/assets/news1.png", id="article-img-1", n_clicks=0,
#                          style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),

#                 html.Img(src="/assets/news2.png", id="article-img-2", n_clicks=0,
#                          style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),

#                 html.Img(src="/assets/news3.png", id="article-img-3", n_clicks=0,
#                          style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),
#             ])
#         ]
#     ),

#     html.Div(id="sidebar-dynamic", style={"margin": "1rem 2rem"}),
#     html.Div(id="page-content", style={"padding": "2rem 2rem 2rem 2rem", "marginTop": "5rem"})
# ])

# === App Layout Function ===
def serve_layout():
    return html.Div([
        dcc.Location(id="url"),
        dcc.Store(id="uploaded-url"),
        dcc.Store(id="input-uploaded", data=False, storage_type = "session"),

        navbar,  # Navbar includes the Predict button

        dbc.Offcanvas(
            #id="predict-offcanvas",
            title="Prediction Input",
            is_open=False,
            placement="end",
            children=[
                # dbc.InputGroup([
                #     dbc.Input(id="news-url-input", placeholder="Paste URL here...", type="url"),
                #     dbc.Button("Go", id="submit-url", n_clicks=0, color="primary"),
                # ], className="mb-4"),

                html.Hr(),

                html.Div([
                    html.H5("Or choose a sample article:"),

                    html.Img(src="/assets/news1.png", id="article-img-1", n_clicks=0,
                             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),

                    html.Img(src="/assets/news2.png", id="article-img-2", n_clicks=0,
                             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),

                    html.Img(src="/assets/news3.png", id="article-img-3", n_clicks=0,
                             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),
                ]),

                #html.Div(id="predict-confirmation", className="text-success mt-3 fw-semibold")
                #html.Div(id="predict-confirmation", className="mt-3 fw-semibold"),
                #html.Div(id="input-status-message", className="mt-2"),

            ]
        ),

        html.Div(id="sidebar-dynamic", style={"margin": "1rem 2rem"}),
        html.Div(id="page-content", style={"padding": "2rem 2rem 2rem 2rem", "marginTop": "5rem"}),
        # Hidden components to prevent "nonexistent object" errors
        html.Div([
            html.Button(id="submit-url", style={"display": "none"}),
            html.Img(id="article-img-1", style={"display": "none"}),
            html.Img(id="article-img-2", style={"display": "none"}),
            html.Img(id="article-img-3", style={"display": "none"}),
        ], style={"display": "none"})
    ])

app.layout = serve_layout  # Set the dynamic layout


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
    elif pathname == "/module5":
        return module5.layout
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
    elif pathname == "/module5":
        return module5.sidebar_controls
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

### Predict Button Callback
@app.callback(
    Output("predict-offcanvas", "is_open"),
    Input("open-predict", "n_clicks"),
    prevent_initial_call=True
)
def toggle_offcanvas(n_clicks):
    if n_clicks:
        return True
    return False

# @app.callback(
#     Output("input-uploaded", "data"),
#     Output("uploaded-url", "data"),
#     Input("submit-url", "n_clicks"),
#     Input("article-img-1", "n_clicks"),
#     Input("article-img-2", "n_clicks"),
#     Input("article-img-3", "n_clicks"),
#     State("news-url-input", "value"),
#     prevent_initial_call=True
# )
# def handle_input_submission(n_go, n1, n2, n3, url_value):
#     ctx_id = callback_context.triggered_id

#     if ctx_id == "submit-url" and url_value and url_value.strip():
#         return True, url_value.strip()
#     elif ctx_id == "article-img-1":
#         return True, "https://sample-article1.com"
#     elif ctx_id == "article-img-2":
#         return True, "https://sample-article2.com"
#     elif ctx_id == "article-img-3":
#         return True, "https://sample-article3.com"
    
#     return dash.no_update, dash.no_update




@app.callback(
    Output("input-uploaded", "data", allow_duplicate=True),
    Output("uploaded-url", "data"),
    Output("predict-confirmation", "children"),
    Input("submit-url", "n_clicks"),
    Input("article-img-1", "n_clicks"),
    Input("article-img-2", "n_clicks"),
    Input("article-img-3", "n_clicks"),
    State("news-url-input", "value"),
    prevent_initial_call=True
)
def handle_input_submission(n_go, n1, n2, n3, url_value):
    ctx_id = callback_context.triggered_id
    if ctx_id == "submit-url" and url_value and url_value.strip():
        return True, url_value.strip(), "✅ Input successfully registered."
    elif ctx_id == "article-img-1":
        return True, "https://sample-article1.com", "✅ Sample article 1 selected."
    elif ctx_id == "article-img-2":
        return True, "https://sample-article2.com", "✅ Sample article 2 selected."
    elif ctx_id == "article-img-3":
        return True, "https://sample-article3.com", "✅ Sample article 3 selected."
    
    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("input-status-message", "children", allow_duplicate=False),
    Input("input-uploaded", "data"),
    prevent_initial_call=False
)
def set_default_status(uploaded):
    if uploaded:
        return "✅ Input already registered"
    else:
        return "ℹ️ No article uploaded yet"


# @app.callback(
#     Output("input-status-message", "children"),
#     Output("input-uploaded", "data", allow_duplicate=True),
#     Output("uploaded-url", "data"),
#     Output("predict-confirmation", "children"),
#     Input("submit-url", "n_clicks"),
#     Input("article-img-1", "n_clicks"),
#     Input("article-img-2", "n_clicks"),
#     Input("article-img-3", "n_clicks"),
#     State("news-url-input", "value"),
#     prevent_initial_call=True
# )
# def handle_input_submission(n_go, n1, n2, n3, url_value):
#     triggered_id = ctx.triggered_id

#     if triggered_id == "submit-url" and url_value and url_value.strip():
#         return html.Span("✅ Input registered", className="text-success"), True, url_value.strip(), "✅ Input successfully registered."
#     elif triggered_id == "article-img-1":
#         return html.Span("✅ Sample article 1 selected", className="text-success"), True, "https://sample-article1.com", "✅ Sample article 1 selected."
#     elif triggered_id == "article-img-2":
#         return html.Span("✅ Sample article 2 selected", className="text-success"), True, "https://sample-article2.com", "✅ Sample article 2 selected."
#     elif triggered_id == "article-img-3":
#         return html.Span("✅ Sample article 3 selected", className="text-success"), True, "https://sample-article3.com", "✅ Sample article 3 selected."

#     return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True)
