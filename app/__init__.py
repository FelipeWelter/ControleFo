from flask import Flask, redirect, url_for, render_template, request
from config import Config
from app.extensions import db, login_manager, migrate
from flask_login import current_user
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.fo.models import Usuario
    from app.fo.permissions import tem_acesso_oficial, usuario_tem_historico_pessoal

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    login_manager.login_view = "auth.login"

    @app.before_request
    def exigir_primeiro_acesso():
        if not current_user.is_authenticated:
            return None

        endpoints_liberados = {
            "auth.login",
            "auth.logout",
            "auth.primeiro_acesso",
            "static",
        }

        if request.endpoint in endpoints_liberados or (request.endpoint or "").startswith("static"):
            return None

        if getattr(current_user, "primeiro_acesso", False) or not getattr(current_user, "aceitou_termos", False):
            return redirect(url_for("auth.primeiro_acesso"))

        return None

    @app.context_processor
    def inject_permissions_helpers():
        return {
            "tem_acesso_oficial": tem_acesso_oficial,
            "usuario_tem_historico_pessoal": usuario_tem_historico_pessoal,
            "current_year": datetime.now().year
        }

    from app.fo import fo_bp
    app.register_blueprint(fo_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("fo.dashboard"))

        return redirect(url_for("auth.login"))


    @app.errorhandler(403)
    def erro_403(error):
        return render_template(
            "error.html",
            codigo=403,
            titulo="Acesso negado",
            mensagem="Você não possui permissão para acessar este recurso."
        ), 403


    @app.errorhandler(404)
    def erro_404(error):
        return render_template(
            "error.html",
            codigo=404,
            titulo="Página não encontrada",
            mensagem="A página solicitada não existe ou foi movida."
        ), 404


    @app.errorhandler(500)
    def erro_500(error):
        return render_template(
            "error.html",
            codigo=500,
            titulo="Erro interno do sistema",
            mensagem="Ocorreu uma falha inesperada. Tente novamente ou informe o administrador."
        ), 500

    return app