from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.fo.models import Usuario, SolicitacaoResetSenha
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.fo.permissions import militar_bloqueado_por_posto, tem_permissao


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

        # Usuário ADMIN é uma conta de manutenção do sistema e pode não possuir identidade militar vinculada.
        # Por isso, não deve ficar preso na tela de primeiro acesso por ausência de identidade.
        if not tem_permissao(usuario, "ADMIN"):
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
    # ADMIN sem militar vinculado não deve passar pelo fluxo de identidade militar.
    if tem_permissao(current_user, "ADMIN") and not current_user.militar:
        current_user.primeiro_acesso = False
        current_user.aceitou_termos = True
        current_user.data_aceite_termos = datetime.utcnow()
        db.session.commit()
        flash("Conta administrativa liberada.", "success")
        return redirect(url_for("index"))

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


@auth_bp.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    """Cria solicitação de redefinição de senha para análise do administrador.

    O sistema não redefine a senha automaticamente para evitar que alguém que conheça
    uma identidade militar consiga assumir a conta de outro usuário.
    """
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        identidade = (request.form.get("identidade") or "").strip()
        observacao = (request.form.get("observacao") or "").strip()

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.militar and usuario.militar.identidade_militar == identidade:
            pendente = SolicitacaoResetSenha.query.filter_by(
                usuario_id=usuario.id,
                status="PENDENTE"
            ).first()

            if not pendente:
                solicitacao = SolicitacaoResetSenha(
                    usuario_id=usuario.id,
                    identidade_informada=identidade,
                    observacao=observacao,
                    ip=request.remote_addr
                )
                db.session.add(solicitacao)
                db.session.commit()

        # Mensagem genérica para não revelar se usuário/identidade existem.
        flash(
            "Se os dados informados estiverem corretos, a solicitação será enviada ao administrador.",
            "info"
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/esqueci_senha.html")


@auth_bp.route("/admin/solicitacoes-senha")
@login_required
def admin_solicitacoes_senha():
    if not tem_permissao(current_user, "ADMIN"):
        abort(403)

    solicitacoes = SolicitacaoResetSenha.query.order_by(
        SolicitacaoResetSenha.solicitado_em.desc()
    ).all()

    return render_template(
        "auth/admin_solicitacoes_senha.html",
        solicitacoes=solicitacoes
    )


@auth_bp.route("/admin/solicitacoes-senha/<int:solicitacao_id>/aprovar", methods=["POST"])
@login_required
def aprovar_solicitacao_senha(solicitacao_id):
    if not tem_permissao(current_user, "ADMIN"):
        abort(403)

    solicitacao = SolicitacaoResetSenha.query.get_or_404(solicitacao_id)

    if solicitacao.status != "PENDENTE":
        flash("Esta solicitação já foi analisada.", "warning")
        return redirect(url_for("auth.admin_solicitacoes_senha"))

    usuario = solicitacao.usuario

    if not usuario or not usuario.militar:
        flash("Não foi possível resetar a senha: usuário sem militar vinculado.", "danger")
        return redirect(url_for("auth.admin_solicitacoes_senha"))

    usuario.senha_hash = generate_password_hash(usuario.militar.identidade_militar)
    usuario.primeiro_acesso = True
    usuario.aceitou_termos = False
    usuario.data_aceite_termos = None

    solicitacao.status = "APROVADA"
    solicitacao.analisado_em = datetime.utcnow()
    solicitacao.analisado_por_id = current_user.id

    db.session.commit()

    flash("Solicitação aprovada. A senha foi resetada para a identidade militar do usuário.", "success")
    return redirect(url_for("auth.admin_solicitacoes_senha"))


@auth_bp.route("/admin/solicitacoes-senha/<int:solicitacao_id>/recusar", methods=["POST"])
@login_required
def recusar_solicitacao_senha(solicitacao_id):
    if not tem_permissao(current_user, "ADMIN"):
        abort(403)

    solicitacao = SolicitacaoResetSenha.query.get_or_404(solicitacao_id)

    if solicitacao.status != "PENDENTE":
        flash("Esta solicitação já foi analisada.", "warning")
        return redirect(url_for("auth.admin_solicitacoes_senha"))

    solicitacao.status = "RECUSADA"
    solicitacao.analisado_em = datetime.utcnow()
    solicitacao.analisado_por_id = current_user.id

    db.session.commit()

    flash("Solicitação recusada.", "warning")
    return redirect(url_for("auth.admin_solicitacoes_senha"))
