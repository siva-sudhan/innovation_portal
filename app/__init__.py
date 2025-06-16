from flask import Flask


def create_app():
    """Application factory."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=True)

    from .views import all_blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp)

    return app
