from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.fo.models import Usuario
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(username=username).first()

        if not usuario or not check_password_hash(
            usuario.senha_hash,
            senha
        ):

            flash("Usuário ou senha inválidos.", "danger")
            return redirect(url_for("auth.login"))

        if usuario.militar and not usuario.militar.ativo:
            flash(
                "Seu acesso está bloqueado porque seu cadastro está inativo.",
                "danger"
            )
            
            return redirect(url_for("auth.login"))



        login_user(usuario)
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("index"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/trocar-senha", methods=["GET", "POST"])
@login_required
def trocar_senha():
    if request.method == "POST":
        senha_atual = request.form.get("senha_atual")
        nova_senha = request.form.get("nova_senha")
        confirmar_senha = request.form.get("confirmar_senha")

        if not check_password_hash(current_user.senha_hash, senha_atual):
            flash("Senha atual incorreta.", "danger")
            return redirect(url_for("auth.trocar_senha"))

        if nova_senha != confirmar_senha:
            flash("A nova senha e a confirmação não conferem.", "danger")
            return redirect(url_for("auth.trocar_senha"))

        if len(nova_senha) < 6:
            flash("A nova senha deve ter pelo menos 6 caracteres.", "warning")
            return redirect(url_for("auth.trocar_senha"))

        current_user.senha_hash = generate_password_hash(nova_senha)
        db.session.commit()

        flash("Senha alterada com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template("auth/trocar_senha.html")

    