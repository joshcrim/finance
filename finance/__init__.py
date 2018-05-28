from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_restless import APIManager
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
migrate = Migrate()
api = APIManager()
login = LoginManager()
login.login_view = 'auth.login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    api.init_app(app, flask_sqlalchemy_db=db)

    from finance.auth.controller import register_api as register_user_api
    from finance.wallet.controller import register_api as register_wallet_api

    register_user_api(app)
    register_wallet_api(app)

    from finance.auth import bp as auth_bp
    from finance.wallet import bp as wallet_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(wallet_bp)

    return app
