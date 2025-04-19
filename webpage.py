import warnings
import pandas as pd
import requests
warnings.filterwarnings("ignore", message="A nonexistent object was used in an `Input` of a Dash callback.")
from urllib.parse import urlparse

import dash
from dash import dcc, html, Output, Input, callback_context, State
import dash_bootstrap_components as dbc
from dash import ctx, callback_context


# Initialize
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Import layouts
from index import layout as index_layout
from apps import module1a, module1b, module2, module3a, module3b, module4a, module4b, module5


navbar = dbc.Navbar(
    dbc.Container(fluid=True, children=[
         # LEFT: Brand
        dbc.Row([
            dbc.Col(
                dbc.NavbarBrand("T5G1", href = "/", className="text-white", style={"fontSize": "3rem", "marginLeft": "2rem"}),
                width="auto"
            )
        ], align="center", className="g-0"),

        # CENTER: Navbar Links (in Collapse)
        dbc.NavbarToggler(id="navbar-toggler", className = "ms-3"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Trade Map", href="/module2", className="mx-3", active="exact")),
                # dbc.NavItem(dbc.NavLink("Home", href="/", className="mx-2 fs-5", active="exact")),
                dbc.DropdownMenu(label="Countries", children=[
                    dbc.DropdownMenuItem("Country Share Breakdown", href="/module1a"),
                    dbc.DropdownMenuItem("Country Share Trend", href="/module3b"),
                ], nav=True, in_navbar=True, className="mx-3"),
                dbc.DropdownMenu(label="Sectors", children=[
                    dbc.DropdownMenuItem("Sector Share Breakdown", href="/module3a"),
                    dbc.DropdownMenuItem("Sector Share Trend", href="/module1b"),
                ], nav=True, in_navbar=True, className="mx-3"),
                dbc.DropdownMenu(label="Geopolitical Relations", children=[
                    dbc.DropdownMenuItem("Trade Balance by Year", href="/module4a"),
                    dbc.DropdownMenuItem("Trade Dependence over Time", href="/module4b"),
                ], nav=True, in_navbar=True, className="mx-3"),
                dbc.NavItem(dbc.NavLink("News Impact on Forecast", href="/module5", className="mx-3", active="exact")),
            ], className="ms-auto", navbar=True),
            id="navbar-collapse",
            navbar=True
        ),

        # RIGHT-ALIGNED PREDICT BUTTON (not inside the Collapse/nav)
        dbc.Button("Predict", id="open-predict", color="light", className="ms-3", style={"fontSize": "1.2rem"}),

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

            html.Img(src="/assets/news1.png", id="article-img-11", n_clicks=0,
             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),

            html.Img(src="/assets/news2.png", id="article-img-21", n_clicks=0,
             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),

            html.Img(src="/assets/news3.png", id="article-img-31", n_clicks=0,
             style={"cursor": "pointer", "width": "100%", "marginBottom": "1rem"}),
        ]), 
        #html.Div(id="predict-confirmation", className="text-success mt-3 fw-semibold")
        # html.Div(id="predict-confirmation", className="mt-3 fw-semibold"),
        # html.Div(id="input-status-message", className="mt-2"),
        html.Div(id="predict-confirmation", className="mt-3 fw-semibold"),
        html.Div(id="input-status-message", className="mt-2 text-muted"),

    ], style={"maxWidth": "1800px"}
),
    ]),
    color="#2C3E50",
    # dark=True,
    fixed="top",
    style={
        "height": "125px",  # Slightly taller navbar
        "padding": "0.5rem 1rem"  # Adjusted padding
    },
    className="mb-4 px-4"
)



# === App Layout Function ===
def serve_layout():
    return html.Div([
        # Core routing and state management
        dcc.Location(id="url"),
        dcc.Store(id="uploaded-url"),
        dcc.Store(id="input-uploaded", data=False, storage_type="session"),
        dcc.Store(id="forecast-data", storage_type="memory"),
        dcc.Store(id="input-status", data=None, storage_type="memory"),

        # Main UI components
        navbar,
        html.Div(id="sidebar-dynamic", style={"margin": "1rem 2rem"}),
        html.Div(id="page-content", style={"padding": "2rem 2rem 2rem 2rem", "marginTop": "5rem"})
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


@app.callback(
    Output("input-uploaded", "data", allow_duplicate=True),
    Output("uploaded-url", "data"),
    Output("predict-confirmation", "children"),
    Output('forecast-data', 'data'),
    Output("input-status", "data"), 
    Input("submit-url", "n_clicks"),
    Input("article-img-11", "n_clicks"),
    Input("article-img-21", "n_clicks"),
    Input("article-img-31", "n_clicks"),
    State("news-url-input", "value"),
    prevent_initial_call=True
)
def handle_input_submission(n_go, n1, n2, n3, url_value):

    # Define a static whitelist of approved domains for helper function
    APPROVED_DOMAINS = {
        "bbc.com", "edition.cnn.com", "theguardian.com", "cbsnews.com",  "apnews.com", 
        "channelnewsasia.com", "straitstimes.com","nbcnews.com","foxnews.com","abcnews.go.com"
    }
    def validate_url_domain(url: str):
        """
        Checks whether the domain of a given URL is within the approved list.
        Returns True if valid, False if not.
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            # Match subdomains if needed using endswith
            return any(domain == approved or domain.endswith("." + approved) for approved in APPROVED_DOMAINS)
        except:
            return False
        
    def is_url(str):
        """
        Check if the string is a valid URL.
        """
        try:
            result = urlparse(str)
            return all([result.scheme, result.netloc])
        except:
            return False
        
    ctx_id = callback_context.triggered_id
    if ctx_id == "submit-url" and url_value and url_value.strip():

        if not is_url(url_value.strip()):
            message = "❌ Invalid URL format. Please enter a valid URL."
            return dash.no_update, dash.no_update, message, dash.no_update, "error"
        
        if not validate_url_domain(url_value.strip()):
            message = "❌ URL domain not supported. Please use articles from approved sources only."
            return dash.no_update, dash.no_update, message, dash.no_update, "error"
        
        url_to_post = url_value.strip()
        try:
            response = requests.post("http://127.0.0.1:5000/predict", json={"url": url_to_post}, headers={"Content-Type": "application/json"})
            response.raise_for_status()  # Raise an error for bad responses (status codes 4xx, 5xx)

            response_data = response.json() #if response.content else {} # Returns the dictionary 
            # response=pd.read_csv("sample_2026.csv",header=0).to_dict() # For testing purposes, replace with the actual API call
            message = f"✅ Input successfully registered."
            return True, url_to_post, message, response_data,'success'  # Return the response data as well
        except Exception as e:
            # In case of an error, log or use a custom error message.
            message = f"❌ Failed to register input, Please try again."
            return dash.no_update, dash.no_update, message, dash.no_update,'error'

    elif ctx_id == "article-img-11":
        return True, "https://sample-article1.com", "✅ Sample article 1 selected.", {'sample':'data1'},'success'
    elif ctx_id == "article-img-21":
        return True, "https://sample-article2.com", "✅ Sample article 2 selected.", {'sample':'data2'},'success'
    elif ctx_id == "article-img-31":
        return True, "https://sample-article3.com", "✅ Sample article 3 selected.", {'sample':'data3'},'success'
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output("input-status-message", "children"),
    Input("submit-url", "n_clicks"),
    Input("input-uploaded", "data"),
    Input("input-status", "data"),
)
def update_status(n_clicks, uploaded, status):
    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if status == "error":
        return "⚠️ There was an issue with your input. Please try again."
    
    if uploaded:
        return "✅ Input already registered"
    
    if triggered_id == "submit-url" and n_clicks:
        return "⏳ The page is now loading. Please wait until input is registered to toggle through the visualisations."

    # Default message
    return "ℹ️ No article uploaded yet"

# === Run App ===
if __name__ == '__main__':
    app.run(debug=False)
