import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from .maps import *



def init_dashboard(server):
    app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/css/style.css',
        ]
    )

    # Create Dash Layout
    app.layout = html.Div([dcc.Graph(id='graph')])

    init_callbacks(app)

    return app.server

def init_callbacks(app):
    print("in calls")
    @app.callback(
              Output('graph', 'figure'),
              [
                   Input('my-input', 'value')
              ]
        
        )
    def update_graph(rows):
            return True
    
    def gen(value):
         return ladmap('E07000245',500,500)
    


