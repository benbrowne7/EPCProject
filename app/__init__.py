from flask import Flask
from flask_navigation import Navigation


def init_app():
    """Construct core Flask application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes
        nav = Navigation(app)
        nav.Bar('top', [nav.Item('Grid', 'grid'), nav.Item('Individual', 'individual'), nav.Item('LAD', 'lad'), nav.Item('Reset', 'index')])
        from .plotlydash.dashboard import init_dashboard
        app = init_dashboard(app)

        return app
	