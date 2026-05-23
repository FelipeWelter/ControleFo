from flask import Flask, redirect, url_for
from config import Config
from app.extensions import db, login_manager, migrate
from flask_login import current_user



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.fo.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    login_manager.login_view = "auth.login"

    from app.fo import fo_bp
    app.register_blueprint(fo_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated and current_user.perfil == "MILITAR":
            return redirect(url_for("fo.meu_historico"))

        return redirect(url_for("fo.ranking"))

    return app