from flask import render_template, request, jsonify, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, func, case
from app.extensions import db
from app.fo.models import Militar
from . import fo_bp
from .models import TipoDeFato, FatoObservado
from .permissions import (
    requer_homologador,
    requer_admin,
    perfil_permitido
)
from .services import criar_fato_observado, aprovar_fato, recusar_fato, editar_fato
from flask import Response
from werkzeug.security import generate_password_hash
from .models import Usuario, Militar, PostoGraduacao, Secao, TipoDeFato
from datetime import datetime

@fo_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo_fo():
    if request.method == "POST":
        militar_id = request.form.get("militar_id", type=int)
        tipo_fato_id = request.form.get("tipo_fato_id", type=int)
        descricao = request.form.get("descricao", "")
        arquivos = request.files.getlist("evidencias")

        militar = Militar.query.get_or_404(militar_id)
        tipo_fato = TipoDeFato.query.filter_by(id=tipo_fato_id, ativo=True).first_or_404()
        
        criar_fato_observado(
            usuario_logado=current_user,
            militar_alvo=militar,
            tipo_fato=tipo_fato,
            descricao=descricao,
            arquivos=arquivos
        )

        flash("FO registrado com sucesso e enviado para homologação.", "success")
        return redirect(url_for("fo.novo_fo"))

    tipos = TipoDeFato.query.filter_by(ativo=True).order_by(TipoDeFato.nome).all()
    return render_template("fo/lancar_fo.html", tipos=tipos)

@fo_bp.route("/api/militares")
@login_required
def api_buscar_militares():
    termo = request.args.get("q", "").strip()

    if len(termo) < 2:
        return jsonify([])

    militares = Militar.query.filter(
        or_(
            Militar.nome_guerra.ilike(f"%{termo}%"),
            Militar.identidade_militar.ilike(f"%{termo}%")
        )
    ).limit(10).all()

    return jsonify([
        {
            "id": militar.id,
            "nome_guerra": militar.nome_guerra,
            "posto_graduacao": militar.posto_graduacao.nome if militar.posto_graduacao else "",
            "identidade_militar": militar.identidade_militar,
            "secao": militar.secao.nome if militar.secao else "",
            "foto_url": militar.foto_url if hasattr(militar, "foto_url") else None
        }
        for militar in militares
    ])

@fo_bp.route("/api/tipos/<int:tipo_id>")
@login_required
def api_tipo_fato(tipo_id):
    tipo = TipoDeFato.query.filter_by(id=tipo_id, ativo=True).first_or_404()
    
    return jsonify({
        "id": tipo.id,
        "nome": tipo.nome,
        "sinal": tipo.sinal,
        "pontos": tipo.pontos
    })

@fo_bp.route("/homologacao")
@login_required
@requer_homologador
def homologacao():
    fatos = FatoObservado.query.filter_by(status="Pendente")\
        .order_by(FatoObservado.data_registro.desc())\
        .all()

    total_pendente = len(fatos)

    return render_template(
        "fo/homologacao.html",
        fatos=fatos,
        total_pendente=total_pendente
    )

@fo_bp.route("/homologacao/<int:fato_id>/aprovar", methods=["POST"])
@login_required
@requer_homologador
def aprovar(fato_id):
    fato = FatoObservado.query.get_or_404(fato_id)

    if fato.status != "Pendente":
        abort(400, description="Apenas FOs pendentes podem ser aprovados.")

    aprovar_fato(fato, homologador=current_user)
    flash("FO aprovado e publicado com sucesso.", "success")
    return redirect(url_for("fo.homologacao"))

@fo_bp.route("/homologacao/<int:fato_id>/recusar", methods=["POST"])
@login_required
@requer_homologador
def recusar(fato_id):
    fato = FatoObservado.query.get_or_404(fato_id)

    if fato.status != "Pendente":
        abort(400, description="Apenas FOs pendentes podem ser recusados.")

    justificativa = request.form.get("justificativa", "")

    recusar_fato(fato, homologador=current_user, justificativa=justificativa)
    flash("FO recusado/anulado com sucesso.", "warning")
    return redirect(url_for("fo.homologacao"))

@fo_bp.route("/homologacao/<int:fato_id>/editar", methods=["GET", "POST"])
@login_required
@requer_homologador
def editar(fato_id):
    fato = FatoObservado.query.get_or_404(fato_id)

    if request.method == "POST":
        nova_descricao = request.form.get("descricao", "")
        editar_fato(fato, editor=current_user, nova_descricao=nova_descricao)
        flash("FO editado com sucesso.", "success")
        return redirect(url_for("fo.homologacao"))
    
    return render_template("fo/editar_fo.html", fato=fato)

@fo_bp.route("/ranking")
@login_required
def ranking():
    periodo = request.args.get("periodo", "mes")
    secao_id = request.args.get("secao_id", type=int)

    query = db.session.query(
        Militar.id.label("militar_id"),
        Militar.nome_guerra.label("nome_guerra"),
        Militar.id_posto_graduacao.label("id_posto_graduacao"),
        PostoGraduacao.nome.label("posto_grad"),
        Militar.data_de_praca.label("data_de_praca"),
        func.sum(
            case(
                (FatoObservado.sinal == "POSITIVO", FatoObservado.pontos),
                else_=0
            )
        ).label("pontos_positivos"),
        func.sum(
            case(
                (FatoObservado.sinal == "NEGATIVO", FatoObservado.pontos),
                else_=0
            )
        ).label("pontos_negativos")
    ).join(
        FatoObservado,
        FatoObservado.militar_id == Militar.id
    ).join(
        PostoGraduacao,
        Militar.id_posto_graduacao == PostoGraduacao.id
    ).filter(
        FatoObservado.status == "Publicado"
    )

    if secao_id:
        query = query.filter(Militar.id_secao == secao_id)
    
    query = query.group_by(
        Militar.id,
        Militar.nome_guerra,
        Militar.id_posto_graduacao,
        Militar.data_de_praca,
        PostoGraduacao.nome
    )

    resultados = query.all()

    ranking_lista = []

    for item in resultados:
        positivos = item.pontos_positivos or 0
        negativos = item.pontos_negativos or 0
        saldo = positivos - negativos

        if saldo > 100:
            conceito = "Excelente"
            badge = "primary"
        elif 51 <= saldo <= 100:
            conceito = "Muito Bom"
            badge = "success"
        elif 0 <= saldo <= 50:
            conceito = "Bom"
            badge = "warning"
        else:
            conceito = "Insuficiente"
            badge = "danger"

        ranking_lista.append({
            "militar_id": item.militar_id,
            "nome_guerra": item.nome_guerra,
            "posto_grad": item.posto_grad,
            "qtd_positivo": positivos,
            "qtd_negativo": negativos,
            "saldo": saldo,
            "conceito": conceito,
            "badge": badge,
            "id_posto_graduacao": item.id_posto_graduacao,
            "data_de_praca": item.data_de_praca
        })

    ranking_lista.sort(
        key=lambda x: (
            -x["saldo"],
            x["id_posto_graduacao"],
            x["data_de_praca"]
        )
    )

    secoes = Secao.query.order_by(Secao.nome.asc()).all()
    return render_template(
        "fo/ranking.html",
        ranking=ranking_lista,
        periodo=periodo,
        secoes=secoes
        )

@fo_bp.route("/exportar-bi", methods=["POST"])
@login_required
@perfil_permitido("BOLETIM")
def exportar_bi():
    ids = request.form.getlist("fo_ids")

    if not ids:
        flash("Nenhum FO selecionado para exportação.", "warning")
        return redirect(url_for("fo.exportacao"))

    fatos = FatoObservado.query.filter(
        FatoObservado.id.in_(ids),
        FatoObservado.status == "Publicado"
    ).order_by(FatoObservado.data_registro.asc()).all()

    linhas = []

    for fato in fatos:
        texto = (
            f"O {fato.cadastrador.militar.posto_graduacao.nome} "
            f"{fato.cadastrador.militar.nome_guerra} observa que o "
            f"{fato.militar.posto_graduacao.nome} "
            f"{fato.militar.nome_guerra} "
            f"{fato.descricao.strip()}"
        )

        linhas.append(texto)

    conteudo = "\n\n".join(linhas)

    return Response(
        conteudo,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=boletim_fo.txt"
        }
    )

@fo_bp.route("/exportacao")
@login_required
@perfil_permitido("BOLETIM")
def exportacao():

    fatos = FatoObservado.query.filter_by(
        status="Publicado"
    ).order_by(
        FatoObservado.data_registro.desc()
    ).all()

    return render_template(
        "fo/exportacao.html",
        fatos=fatos
    )

# =========================
# ADMIN - MILITARES
# =========================

@fo_bp.route("/admin/militares")
@login_required
@perfil_permitido("CADASTRADOR")
def admin_militares():
    militares = Militar.query.order_by(Militar.nome_guerra.asc()).all()
    return render_template("fo/admin_militares.html", militares=militares)


@fo_bp.route("/admin/militares/novo", methods=["GET", "POST"])
@login_required
@perfil_permitido("CADASTRADOR")
def admin_militar_novo():
    postos = PostoGraduacao.query.order_by(PostoGraduacao.id.asc()).all()
    secoes = Secao.query.order_by(Secao.nome.asc()).all()

    if request.method == "POST":
        militar = Militar(
            nome_guerra=request.form.get("nome_guerra"),
            identidade_militar=request.form.get("identidade_militar"),
            id_posto_graduacao=request.form.get("id_posto_graduacao", type=int),

            data_de_praca=datetime.strptime(
                request.form.get("data_de_praca"),
                "%Y-%m-%d"
            ).date(),

            id_secao=request.form.get("id_secao", type=int),
        )

        db.session.add(militar)
        db.session.commit()

        flash("Militar cadastrado com sucesso.", "success")
        return redirect(url_for("fo.admin_militares"))

    return render_template(
        "fo/admin_militar_form.html",
        militar=None,
        postos=postos,
        secoes=secoes
    )


@fo_bp.route("/admin/militares/<int:militar_id>/editar", methods=["GET", "POST"])
@login_required
@perfil_permitido("CADASTRADOR")
def admin_militar_editar(militar_id):
    militar = Militar.query.get_or_404(militar_id)
    postos = PostoGraduacao.query.order_by(PostoGraduacao.id.asc()).all()
    secoes = Secao.query.order_by(Secao.nome.asc()).all()

    if request.method == "POST":
        militar.nome_guerra = request.form.get("nome_guerra")
        militar.identidade_militar = request.form.get("identidade_militar")
        militar.id_posto_graduacao = request.form.get("id_posto_graduacao", type=int)

        militar.data_de_praca = datetime.strptime(
            request.form.get("data_de_praca"),
            "%Y-%m-%d"
        ).date()

        militar.id_secao = request.form.get("id_secao", type=int)

        db.session.commit()

        flash("Militar atualizado com sucesso.", "success")
        return redirect(url_for("fo.admin_militares"))

    return render_template(
        "fo/admin_militar_form.html",
        militar=militar,
        postos=postos,
        secoes=secoes
    )


# =========================
# ADMIN - TIPOS DE FO
# =========================

@fo_bp.route("/admin/tipos")
@login_required
@requer_admin
def admin_tipos():
    tipos = TipoDeFato.query.order_by(TipoDeFato.nome.asc()).all()
    return render_template("fo/admin_tipos.html", tipos=tipos)


@fo_bp.route("/admin/tipos/novo", methods=["GET", "POST"])
@login_required
@requer_admin
def admin_tipo_novo():
    if request.method == "POST":
        tipo = TipoDeFato(
            nome=request.form.get("nome"),
            sinal=request.form.get("sinal"),
            pontos=request.form.get("pontos", type=int),
            ativo=True if request.form.get("ativo") == "on" else False
        )

        db.session.add(tipo)
        db.session.commit()

        flash("Tipo de FO cadastrado com sucesso.", "success")
        return redirect(url_for("fo.admin_tipos"))

    return render_template("fo/admin_tipo_form.html", tipo=None)


@fo_bp.route("/admin/tipos/<int:tipo_id>/editar", methods=["GET", "POST"])
@login_required
@requer_admin
def admin_tipo_editar(tipo_id):
    tipo = TipoDeFato.query.get_or_404(tipo_id)

    if request.method == "POST":
        tipo.nome = request.form.get("nome")
        tipo.sinal = request.form.get("sinal")
        tipo.pontos = request.form.get("pontos", type=int)
        tipo.ativo = True if request.form.get("ativo") == "on" else False

        db.session.commit()

        flash("Tipo de FO atualizado com sucesso.", "success")
        return redirect(url_for("fo.admin_tipos"))

    return render_template("fo/admin_tipo_form.html", tipo=tipo)


# =========================
# ADMIN - USUÁRIOS
# =========================

@fo_bp.route("/admin/usuarios")
@login_required
@requer_admin
def admin_usuarios():
    usuarios = Usuario.query.order_by(Usuario.username.asc()).all()
    return render_template("fo/admin_usuarios.html", usuarios=usuarios)


@fo_bp.route("/admin/usuarios/novo", methods=["GET", "POST"])
@login_required
@requer_admin
def admin_usuario_novo():
    militares = Militar.query.order_by(Militar.nome_guerra.asc()).all()

    if request.method == "POST":
        usuario = Usuario(
            username=request.form.get("username"),
            senha_hash=generate_password_hash(request.form.get("senha")),
            perfil=request.form.get("perfil"),
            militar_id=request.form.get("militar_id", type=int)
        )

        db.session.add(usuario)
        db.session.commit()

        flash("Usuário cadastrado com sucesso.", "success")
        return redirect(url_for("fo.admin_usuarios"))

    return render_template(
        "fo/admin_usuario_form.html",
        usuario=None,
        militares=militares
    )


@fo_bp.route("/admin/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@requer_admin
def admin_usuario_editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    militares = Militar.query.order_by(Militar.nome_guerra.asc()).all()

    if request.method == "POST":
        usuario.username = request.form.get("username")
        usuario.perfil = request.form.get("perfil")
        usuario.militar_id = request.form.get("militar_id", type=int)

        nova_senha = request.form.get("senha")

        if nova_senha:
            usuario.senha_hash = generate_password_hash(nova_senha)

        db.session.commit()

        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for("fo.admin_usuarios"))

    return render_template(
        "fo/admin_usuario_form.html",
        usuario=usuario,
        militares=militares
    )