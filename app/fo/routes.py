from flask import render_template, request, jsonify, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, func, case
from app.extensions import db
from app.fo.models import Militar
from . import fo_bp
from .models import TipoDeFato, FatoObservado
from .permissions import requer_homologador
from .services import criar_fato_observado, aprovar_fato, recusar_fato, editar_fato

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
    ).filter(
        FatoObservado.status == "Publicado"
    )

    if secao_id:
        query = query.filter(Militar.id_secao == secao_id)
    
    query = query.group_by(
        Militar.id,
        Militar.nome_guerra,
        Militar.id_posto_graduacao,
        Militar.data_de_praca
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

    return render_template("fo/ranking.html", ranking=ranking_lista, periodo=periodo)