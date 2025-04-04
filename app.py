import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3, 4, 5], 'y': [4, 1, 3, 5, 2], 'type': 'line', 'name': 'SF'},
                {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 5, 1, 3], 'type': 'bar', 'name': 'NYC'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)