from flask import Flask
server =Flask(__name__)
@server.route('/')
def hello_world():
    return 'Hello World with flask'

import dash
import dash_core_components as dcc
import dash_html_components as html


app = dash.Dash(__name__, server=server, routes_pathname_prefix='/')
app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children=''' Dash: A web app framework '''),
    dcc.Graph(
        id='example_graph',
        figure={
            'data': [
                {'x': [1,2,3], 'y': [4,1,2], 'type': 'bar', 'name': 'SF'},
                {'x': [1,2,3], 'y': [2,4,5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data visualization'
            }
        }
    )
])
if __name__ == '__main__':
    app.run_server(debug=True)