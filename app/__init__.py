from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate
from app.fo.models import Militar, PostoGraduacao, Secao, Usuario, TipoDeFato


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.fo import fo_bp
    app.register_blueprint(fo_bp)

    return app