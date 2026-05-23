from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.auth import auth_bp
from app.fo.models import Usuario

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(username=username).first()

        if not usuario or usuario.senha_hash != senha:
            flash("Usuário ou senha inválidos.", "danger")
            return redirect(url_for("auth.login"))

        login_user(usuario)
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("fo.novo_fo"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for("auth.login"))