import dash
from dash import html


def init_dashboard(server):
    app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/css/style.css',
        ]
    )

    # Create Dash Layout
    app.layout = html.Div(id='dash-container')

    init_callbacks(app)

    return app.server

def init_callbacks(app):
    @app.callback(
        
        )
    def update_graph(rows):
            return True

