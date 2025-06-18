from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect



# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.views import views_bp
    from app.views.auth import auth_bp
    from app.views.admin import admin_bp
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.views.gamification import gamification_bp
    app.register_blueprint(gamification_bp)

    # Jinja global functions
    from app.utils import generate_teams_link, get_logo_path
    app.jinja_env.globals.update(
        generate_teams_link=generate_teams_link,
        get_logo_path=get_logo_path,
    )

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app
