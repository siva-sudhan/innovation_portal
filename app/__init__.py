from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    csrf.init_app(app)

    from app.views import views_bp
    from app.views.auth import auth_bp
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp)
    
    from app.views.gamification import gamification_bp
    app.register_blueprint(gamification_bp)

    # ✅ Late import to avoid circular import
    from app.utils import generate_teams_link
    app.jinja_env.globals.update(generate_teams_link=generate_teams_link)

    # ✅ Create tables
    with app.app_context():
        db.create_all()

    return app
