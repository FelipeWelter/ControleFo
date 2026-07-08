from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.fo.models import Usuario
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.fo.permissions import militar_bloqueado_por_posto

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

        if usuario.militar and militar_bloqueado_por_posto(usuario):
            flash(
                "Militares com posto/graduação Cabo ou Soldado não possuem acesso ao sistema.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        login_user(usuario)

        if getattr(usuario, "primeiro_acesso", False) or not getattr(usuario, "aceitou_termos", False):
            flash("Primeiro acesso: altere sua senha e aceite os termos de uso para continuar.", "warning")
            return redirect(url_for("auth.primeiro_acesso"))

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

    
@auth_bp.route("/primeiro-acesso", methods=["GET", "POST"])
@login_required
def primeiro_acesso():
    if request.method == "POST":
        identidade = (request.form.get("identidade") or "").strip()
        nova_senha = request.form.get("nova_senha")
        confirmar_senha = request.form.get("confirmar_senha")
        aceite = request.form.get("aceite_termos")

        identidade_esperada = ""
        if current_user.militar:
            identidade_esperada = current_user.militar.identidade_militar or ""
        else:
            identidade_esperada = current_user.username or ""

        if identidade != identidade_esperada:
            flash("Identidade militar incorreta.", "danger")
            return redirect(url_for("auth.primeiro_acesso"))

        if nova_senha != confirmar_senha:
            flash("A nova senha e a confirmação não conferem.", "danger")
            return redirect(url_for("auth.primeiro_acesso"))

        if len(nova_senha) < 6:
            flash("A nova senha deve ter pelo menos 6 caracteres.", "warning")
            return redirect(url_for("auth.primeiro_acesso"))

        if check_password_hash(current_user.senha_hash, nova_senha):
            flash("A nova senha deve ser diferente da senha inicial.", "warning")
            return redirect(url_for("auth.primeiro_acesso"))

        if not aceite:
            flash("É obrigatório aceitar os termos de uso para acessar o sistema.", "warning")
            return redirect(url_for("auth.primeiro_acesso"))

        current_user.senha_hash = generate_password_hash(nova_senha)
        current_user.primeiro_acesso = False
        current_user.aceitou_termos = True
        current_user.data_aceite_termos = datetime.utcnow()
        db.session.commit()

        flash("Senha alterada e termos aceitos com sucesso.", "success")
        return redirect(url_for("index"))

    return render_template("auth/primeiro_acesso.html")
