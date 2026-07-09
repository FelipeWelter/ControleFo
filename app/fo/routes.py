from flask import render_template, request, jsonify, abort, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, func, case
from app.extensions import db
from app.fo.models import Militar
from . import fo_bp
from .models import TipoDeFato, FatoObservado
from .models import Auditoria, DispensaMilitar, Companhia
from .auditoria import registrar_auditoria

from .permissions import (
    requer_homologador,
    requer_admin,
    permissao_requerida,
    requer_lancador,
    oficial_requerido,
    aplicar_escopo_militares,
    militar_no_escopo,
    obter_permissoes,
    tem_permissao,
    companhia_escopo_id,
    usuario_eh_admin,
    usuario_tem_historico_pessoal
)
from .services import criar_fato_observado, aprovar_fato, recusar_fato, editar_fato
from flask import Response
from werkzeug.security import generate_password_hash
from .models import Usuario, Militar, PostoGraduacao, Secao, TipoDeFato, Companhia
from datetime import datetime

@fo_bp.route("/novo", methods=["GET", "POST"])
@login_required
@requer_lancador
def novo_fo():
    if request.method == "POST":
        militar_id = request.form.get("militar_id", type=int)
        tipo_fato_id = request.form.get("tipo_fato_id", type=int)
        descricao = request.form.get("descricao", "")

        militar = Militar.query.get_or_404(militar_id)
        if not militar_no_escopo(current_user, militar):
            flash("Militar fora do seu nível de acesso.", "danger")
            return redirect(url_for("fo.novo_fo"))

        tipo_fato = TipoDeFato.query.filter_by(id=tipo_fato_id, ativo=True).first_or_404()

        fato = criar_fato_observado(
            usuario_logado=current_user,
            militar_alvo=militar,
            tipo_fato=tipo_fato,
            descricao=descricao
        )

        if not fato:
            return redirect(url_for("fo.novo_fo"))
        flash("FO registrado com sucesso e enviado para homologação.", "success")
        return redirect(url_for("fo.novo_fo"))

    tipos = TipoDeFato.query.filter_by(ativo=True).order_by(TipoDeFato.nome.asc()).all()
    return render_template("fo/lancar_fo.html", tipos=tipos)

@fo_bp.route("/api/militares")
@login_required
def api_buscar_militares():
    termo = request.args.get("q", "").strip()

    if len(termo) < 2:
        return jsonify([])

    query = Militar.query.filter(
        Militar.ativo == True,
        or_(
            Militar.nome_guerra.ilike(f"%{termo}%"),
            Militar.identidade_militar.ilike(f"%{termo}%")
        )
    )
    query = aplicar_escopo_militares(query, current_user, Militar)
    militares = query.limit(10).all()

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
        "sinal": tipo.sinal
    })

@fo_bp.route("/homologacao")
@login_required
@requer_homologador
def homologacao():
    query = FatoObservado.query.join(Militar, FatoObservado.militar_id == Militar.id).filter(
        FatoObservado.status == "Pendente"
    )
    query = aplicar_escopo_militares(query, current_user, Militar)
    fatos = query.order_by(FatoObservado.data_registro.desc()).all()

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
    if not militar_no_escopo(current_user, fato.militar):
        flash("FO fora do seu nível de acesso.", "danger")
        return redirect(url_for("fo.homologacao"))

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
    if not militar_no_escopo(current_user, fato.militar):
        flash("FO fora do seu nível de acesso.", "danger")
        return redirect(url_for("fo.homologacao"))

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
    if not militar_no_escopo(current_user, fato.militar):
        flash("FO fora do seu nível de acesso.", "danger")
        return redirect(url_for("fo.homologacao"))

    if request.method == "POST":
        nova_descricao = request.form.get("descricao", "")
        editar_fato(fato, editor=current_user, nova_descricao=nova_descricao)
        flash("FO editado com sucesso.", "success")
        return redirect(url_for("fo.homologacao"))
    
    return render_template("fo/editar_fo.html", fato=fato)

@fo_bp.route("/ranking")
@login_required
@oficial_requerido
def ranking():
    periodo = request.args.get("periodo", "mes")
    secao_id = request.args.get("secao_id", type=int)
    companhia_id = request.args.get("companhia_id", type=int)
    posto_id = request.args.get("posto_id", type=int)

    query = db.session.query(
        Militar.id.label("militar_id"),
        Militar.nome_guerra.label("nome_guerra"),
        Militar.id_posto_graduacao.label("id_posto_graduacao"),
        PostoGraduacao.nome.label("posto_grad"),
        Militar.data_de_praca.label("data_de_praca"),
        func.sum(
            case(
                (FatoObservado.sinal == "POSITIVO", 1),
                else_=0
            )
        ).label("fos_positivos"),
        func.sum(
            case(
                (FatoObservado.sinal == "NEGATIVO", 1),
                else_=0
            )
        ).label("fos_negativos")
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
    
    if posto_id:
        query = query.filter(Militar.id_posto_graduacao == posto_id)

    query = aplicar_escopo_militares(query, current_user, Militar)

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
        positivos = item.fos_positivos or 0
        negativos = item.fos_negativos or 0
        saldo = positivos - negativos

        if saldo > 10:
            conceito = "Excelente"
            badge = "primary"
        elif 5 <= saldo <= 10:
            conceito = "Muito Bom"
            badge = "success"
        elif 0 <= saldo <= 5:
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
    companhias = Companhia.query.filter_by(ativa=True).order_by(Companhia.nome.asc()).all()
    postos = PostoGraduacao.query.order_by(PostoGraduacao.id.asc()).all()
    return render_template(
        "fo/ranking.html",
        ranking=ranking_lista,
        periodo=periodo,
        secoes=secoes,
        postos=postos,
        secao_id=secao_id,
        posto_id=posto_id
    )

@fo_bp.route("/exportar-bi", methods=["POST"])
@login_required
def exportar_bi():
    if not tem_permissao(current_user, "BOLETIM"):
        abort(403)

    ids = request.form.getlist("fo_ids")

    if not ids:
        flash("Nenhum FO selecionado para exportação.", "warning")
        return redirect(url_for("fo.exportacao"))

    query = FatoObservado.query.join(Militar, FatoObservado.militar_id == Militar.id).filter(
        FatoObservado.id.in_(ids),
        FatoObservado.status == "Publicado"
    )
    if not usuario_eh_admin(current_user):
        companhia_id = companhia_escopo_id(current_user)
        if companhia_id:
            query = query.filter(Militar.id_companhia == companhia_id)
        else:
            query = query.filter(False)

    fatos = query.order_by(FatoObservado.data_registro.asc()).all()

    linhas = []

    for fato in fatos:
        modelo = fato.tipo_fato.texto_boletim or fato.tipo_fato.nome
        descricao = fato.descricao.strip() if fato.descricao else ""

        if "{descricao}" in modelo:
            complemento = modelo.format(descricao=descricao)
        else:
            complemento = modelo
            if descricao:
                complemento = f"{complemento} {descricao}"

        texto = (
            f"O {fato.cadastrador.militar.posto_graduacao.nome} "
            f"{fato.cadastrador.militar.nome_guerra} observa que o "
            f"{fato.militar.posto_graduacao.nome} "
            f"{fato.militar.nome_guerra} "
            f"{complemento.strip()}"
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
def exportacao():
    if not tem_permissao(current_user, "BOLETIM"):
        abort(403)

    query = FatoObservado.query.join(Militar, FatoObservado.militar_id == Militar.id).filter(
        FatoObservado.status == "Publicado"
    )

    if not usuario_eh_admin(current_user):
        companhia_id = companhia_escopo_id(current_user)
        if companhia_id:
            query = query.filter(Militar.id_companhia == companhia_id)
        else:
            query = query.filter(False)

    fatos = query.order_by(FatoObservado.data_registro.desc()).all()

    return render_template(
        "fo/exportacao.html",
        fatos=fatos
    )

# =========================
# ADMIN - MILITARES
# =========================

@fo_bp.route("/admin/militares")
@login_required
@permissao_requerida("CADASTRADOR")
def admin_militares():
    query = Militar.query.order_by(Militar.nome_guerra.asc())
    query = aplicar_escopo_militares(query, current_user, Militar)
    militares = query.all()
    return render_template("fo/admin_militares.html", militares=militares)


@fo_bp.route("/admin/militares/novo", methods=["GET", "POST"])
@login_required
@permissao_requerida("CADASTRADOR")
def admin_militar_novo():
    postos = PostoGraduacao.query.order_by(PostoGraduacao.id.asc()).all()
    secoes = Secao.query.order_by(Secao.nome.asc()).all()
    companhias = Companhia.query.filter_by(ativa=True).order_by(Companhia.nome.asc()).all()

    if request.method == "POST":
        identidade = request.form.get("identidade_militar")

        militar_existente = Militar.query.filter_by(
            identidade_militar=identidade
        ).first()

        if militar_existente:
            flash("Já existe um militar cadastrado com essa identidade militar.", "danger")
            return redirect(url_for("fo.admin_militar_novo"))


        data_de_praca = None
        if request.form.get("data_de_praca"):
                data_de_praca=datetime.strptime(
                    request.form.get("data_de_praca"),
                    "%Y-%m-%d"
                ).date()

        militar = Militar(
            nome_guerra=request.form.get("nome_guerra"),
            identidade_militar=identidade,
            id_posto_graduacao=request.form.get("id_posto_graduacao", type=int),
            data_de_praca=data_de_praca,
            id_secao=request.form.get("id_secao", type=int),
            id_companhia=request.form.get("id_companhia", type=int),
        )

        if not militar_no_escopo(current_user, militar):
            flash("Você só pode cadastrar militares dentro do seu nível de acesso.", "danger")
            return redirect(url_for("fo.admin_militar_novo"))

        db.session.add(militar)
        db.session.flush()  # Para garantir que o ID seja gerado antes de criar o usuário

        registrar_auditoria(
            usuario=current_user,
            acao="CADASTRAR_MILITAR",
            entidade="Militar",
            entidade_id=militar.id,
            detalhes=f"Militar cadastrado: {militar.nome_guerra}"
        )

        usuario = Usuario(
            username=identidade,
            senha_hash=generate_password_hash(identidade),
            permissoes="USUARIO",
            militar_id=militar.id
        )

        db.session.add(usuario)
        db.session.commit()

        flash("Militar e usuário associados cadastrados com sucesso.", "success")
        return redirect(url_for("fo.admin_militares"))

    return render_template(
        "fo/admin_militar_form.html",
        militar=None,
        postos=postos,
        secoes=secoes,
        companhias=companhias
    )

@fo_bp.route("/admin/militares/<int:militar_id>/editar", methods=["GET", "POST"])
@login_required
@permissao_requerida("CADASTRADOR")
def admin_militar_editar(militar_id):
    militar = Militar.query.get_or_404(militar_id)
    postos = PostoGraduacao.query.order_by(PostoGraduacao.id.asc()).all()
    secoes = Secao.query.order_by(Secao.nome.asc()).all()
    companhias = Companhia.query.filter_by(ativa=True).order_by(Companhia.nome.asc()).all()

    if not militar_no_escopo(current_user, militar):
        flash("Militar fora do seu nível de acesso.", "danger")
        return redirect(url_for("fo.admin_militares"))

    if request.method == "POST":
        
        identidade_antiga = militar.identidade_militar
        nova_identidade = request.form.get("identidade_militar")
        militar.nome_guerra = request.form.get("nome_guerra")
        militar.identidade_militar = nova_identidade
        militar.id_posto_graduacao = request.form.get("id_posto_graduacao", type=int)
        militar.ativo = True if request.form.get("ativo") == "on" else False
        
        militar.data_de_praca = datetime.strptime(
            request.form.get("data_de_praca"),
            "%Y-%m-%d"
        ).date()

        militar.id_secao = request.form.get("id_secao", type=int)
        militar.id_companhia = request.form.get("id_companhia", type=int)

        usuario_vinculado = Usuario.query.filter_by(
            militar_id=militar.id
        ).first()

        if usuario_vinculado and usuario_vinculado.username == identidade_antiga:
            usuario_vinculado.username = nova_identidade

        registrar_auditoria(
            usuario=current_user,
            acao="EDITAR_MILITAR",
            entidade="Militar",
            entidade_id=militar.id,
            detalhes=f"Militar atualizado: {militar.nome_guerra}"
        )

        db.session.commit()

        flash("Militar atualizado com sucesso.", "success")
        return redirect(url_for("fo.admin_militares"))

    return render_template(
        "fo/admin_militar_form.html",
        militar=militar,
        postos=postos,
        secoes=secoes,
        companhias=companhias
    )


@fo_bp.route("/admin/militares/<int:militar_id>/ativar", methods=["POST"])
@login_required
@permissao_requerida("CADASTRADOR")
def admin_militar_ativar(militar_id):
    militar = Militar.query.get_or_404(militar_id)
    if not militar_no_escopo(current_user, militar):
        flash("Militar fora do seu nível de acesso.", "danger")
        return redirect(url_for("fo.admin_militares"))

    militar.ativo = True

    registrar_auditoria(
        usuario=current_user,
        acao="ATIVAR_MILITAR",
        entidade="Militar",
        entidade_id=militar.id,
        detalhes=f"Militar ativado: {militar.nome_guerra}"
    )

    db.session.commit()

    flash("Militar ativado com sucesso.", "success")
    return redirect(url_for("fo.admin_militares"))


@fo_bp.route("/admin/militares/<int:militar_id>/inativar", methods=["POST"])
@login_required
@permissao_requerida("CADASTRADOR")
def admin_militar_inativar(militar_id):
    militar = Militar.query.get_or_404(militar_id)
    if not militar_no_escopo(current_user, militar):
        flash("Militar fora do seu nível de acesso.", "danger")
        return redirect(url_for("fo.admin_militares"))

    militar.ativo = False

    registrar_auditoria(
        usuario=current_user,
        acao="INATIVAR_MILITAR",
        entidade="Militar",
        entidade_id=militar.id,
        detalhes=f"Militar inativado: {militar.nome_guerra}"
    )

    db.session.commit()

    flash("Militar inativado com sucesso.", "warning")
    return redirect(url_for("fo.admin_militares"))


# =========================
# ADMIN - TIPOS DE FO
# =========================

@fo_bp.route("/admin/tipos")
@login_required
@permissao_requerida("ADMIN")
def admin_tipos():
    tipos = TipoDeFato.query.order_by(TipoDeFato.nome.asc()).all()
    return render_template("fo/admin_tipos.html", tipos=tipos)


@fo_bp.route("/admin/tipos/novo", methods=["GET", "POST"])
@login_required
@permissao_requerida("ADMIN")
def admin_tipo_novo():
    if request.method == "POST":
        tipo = TipoDeFato(
            nome=request.form.get("nome"),
            sinal=request.form.get("sinal"),
            pontos=1,
            texto_boletim=request.form.get("texto_boletim"),
            ativo=True if request.form.get("ativo") == "on" else False
        )

        db.session.add(tipo)
        db.session.commit()

        flash("Tipo de FO cadastrado com sucesso.", "success")
        return redirect(url_for("fo.admin_tipos"))

    return render_template("fo/admin_tipo_form.html", tipo=None)


@fo_bp.route("/admin/tipos/<int:tipo_id>/editar", methods=["GET", "POST"])
@login_required
@permissao_requerida("ADMIN")
def admin_tipo_editar(tipo_id):
    tipo = TipoDeFato.query.get_or_404(tipo_id)

    if request.method == "POST":
        tipo.nome = request.form.get("nome")
        tipo.sinal = request.form.get("sinal")
        tipo.pontos = 1
        tipo.texto_boletim = request.form.get("texto_boletim")
        tipo.ativo = True if request.form.get("ativo") == "on" else False

        db.session.commit()

        flash("Tipo de FO atualizado com sucesso.", "success")
        return redirect(url_for("fo.admin_tipos"))

    return render_template("fo/admin_tipo_form.html", tipo=tipo)




# =========================
# ADMIN - COMPANHIAS
# =========================

@fo_bp.route("/admin/companhias")
@login_required
@permissao_requerida("ADMIN")
def admin_companhias():
    companhias = Companhia.query.order_by(Companhia.nome.asc()).all()
    return render_template("fo/admin_companhias.html", companhias=companhias)


@fo_bp.route("/admin/companhias/novo", methods=["GET", "POST"])
@login_required
@permissao_requerida("ADMIN")
def admin_companhia_nova():
    if request.method == "POST":
        companhia = Companhia(
            nome=request.form.get("nome"),
            sigla=request.form.get("sigla"),
            ativa=True if request.form.get("ativa") == "on" else False
        )

        db.session.add(companhia)
        db.session.flush()

        registrar_auditoria(
            usuario=current_user,
            acao="CADASTRAR_COMPANHIA",
            entidade="Companhia",
            entidade_id=companhia.id,
            detalhes=f"Companhia cadastrada: {companhia.nome}"
        )

        db.session.commit()
        flash("Companhia cadastrada com sucesso.", "success")
        return redirect(url_for("fo.admin_companhias"))

    return render_template("fo/admin_companhia_form.html", companhia=None)


@fo_bp.route("/admin/companhias/<int:companhia_id>/editar", methods=["GET", "POST"])
@login_required
@permissao_requerida("ADMIN")
def admin_companhia_editar(companhia_id):
    companhia = Companhia.query.get_or_404(companhia_id)

    if request.method == "POST":
        companhia.nome = request.form.get("nome")
        companhia.sigla = request.form.get("sigla")
        companhia.ativa = True if request.form.get("ativa") == "on" else False

        registrar_auditoria(
            usuario=current_user,
            acao="EDITAR_COMPANHIA",
            entidade="Companhia",
            entidade_id=companhia.id,
            detalhes=f"Companhia atualizada: {companhia.nome}"
        )

        db.session.commit()
        flash("Companhia atualizada com sucesso.", "success")
        return redirect(url_for("fo.admin_companhias"))

    return render_template("fo/admin_companhia_form.html", companhia=companhia)


# =========================
# ADMIN - USUÁRIOS
# =========================

@fo_bp.route("/admin/usuarios")
@login_required
@permissao_requerida("ADMIN")
def admin_usuarios():
    usuarios = Usuario.query.order_by(Usuario.username.asc()).all()
    return render_template("fo/admin_usuarios.html", usuarios=usuarios)


@fo_bp.route("/admin/usuarios/novo", methods=["GET", "POST"])
@login_required
@permissao_requerida("ADMIN")
def admin_usuario_novo():
    militares = Militar.query.order_by(Militar.nome_guerra.asc()).all()
    companhias = Companhia.query.filter_by(ativa=True).order_by(Companhia.nome.asc()).all()
    secoes = Secao.query.order_by(Secao.nome.asc()).all()

    if request.method == "POST":
        usuario = Usuario(
            username=request.form.get("username"),
            senha_hash=generate_password_hash(request.form.get("senha")),
            permissoes=",".join(request.form.getlist("permissoes")),
            militar_id=request.form.get("militar_id", type=int),
            nivel_acesso=request.form.get("nivel_acesso") or "SECAO",
            companhia_id=request.form.get("companhia_id", type=int),
            secao_id=request.form.get("secao_id", type=int)
        )

        db.session.add(usuario)
        db.session.commit()

        flash("Usuário cadastrado com sucesso.", "success")
        return redirect(url_for("fo.admin_usuarios"))

    return render_template(
        "fo/admin_usuario_form.html",
        usuario=None,
        militares=militares,
        companhias=companhias,
        secoes=secoes
    )


@fo_bp.route("/admin/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@permissao_requerida("ADMIN")
def admin_usuario_editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    militares = Militar.query.order_by(Militar.nome_guerra.asc()).all()
    companhias = Companhia.query.filter_by(ativa=True).order_by(Companhia.nome.asc()).all()
    secoes = Secao.query.order_by(Secao.nome.asc()).all()

    if request.method == "POST":
        usuario.username = request.form.get("username")
        usuario.permissoes = ",".join(request.form.getlist("permissoes"))
        usuario.militar_id = request.form.get("militar_id", type=int)
        usuario.nivel_acesso = request.form.get("nivel_acesso") or "SECAO"
        usuario.companhia_id = request.form.get("companhia_id", type=int)
        usuario.secao_id = request.form.get("secao_id", type=int)

        nova_senha = request.form.get("senha")

        if nova_senha:
            usuario.senha_hash = generate_password_hash(nova_senha)

        db.session.commit()

        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for("fo.admin_usuarios"))

    return render_template(
        "fo/admin_usuario_form.html",
        usuario=usuario,
        militares=militares,
        companhias=companhias,
        secoes=secoes
    )

@fo_bp.route("/meu-historico")
@login_required
def meu_historico():
    if not usuario_tem_historico_pessoal(current_user):
        flash("Este usuário não possui histórico pessoal de FO.", "warning")
        return redirect(url_for("fo.dashboard"))

    if not current_user.militar_id:
        flash("Seu usuário não está vinculado a um militar.", "warning")
        return redirect(url_for("auth.logout"))

    fatos = FatoObservado.query.filter_by(
        militar_id=current_user.militar_id,
        status="Publicado"
    ).order_by(
        FatoObservado.data_registro.desc()
    ).all()

    positivos = [f for f in fatos if f.sinal == "POSITIVO"]
    negativos = [f for f in fatos if f.sinal == "NEGATIVO"]

    total_positivo = len(positivos)
    total_negativo = len(negativos)
    saldo = total_positivo - total_negativo

    return render_template(
        "fo/meu_historico.html",
        fatos=fatos,
        positivos=positivos,
        negativos=negativos,
        total_positivo=total_positivo,
        total_negativo=total_negativo,
        saldo=saldo
    )

@fo_bp.route("/admin/usuarios/<int:usuario_id>/resetar-senha", methods=["POST"])
@login_required
@permissao_requerida("ADMIN")
def admin_usuario_resetar_senha(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if not usuario.militar:
        flash("Este usuário não possui militar vinculado.", "warning")
        return redirect(url_for("fo.admin_usuarios"))

    usuario.senha_hash = generate_password_hash(
        usuario.militar.identidade_militar
    )
    usuario.primeiro_acesso = True
    usuario.aceitou_termos = False
    usuario.data_aceite_termos = None

    registrar_auditoria(
        usuario=current_user,
        acao="RESETAR_SENHA",
        entidade="Usuario",
        entidade_id=usuario.id,
        detalhes=f"Senha resetada para: {usuario.username}"
    )

    db.session.commit()

    flash("Senha resetada para a identidade militar.", "success")
    return redirect(url_for("fo.admin_usuarios"))


@fo_bp.route("/admin/usuarios/<int:usuario_id>/excluir", methods=["POST"])
@login_required
@permissao_requerida("ADMIN")
def admin_usuario_excluir(usuario_id):
    flash("A exclusão de usuários foi desativada. Use edição, reset de senha ou inativação do militar vinculado.", "warning")
    return redirect(url_for("fo.admin_usuarios"))


# =========================
# OFICIAIS - HISTÓRICO GERAL DE FO
# =========================

@fo_bp.route("/historico-geral")
@login_required
@oficial_requerido
def historico_geral():
    militar_id = request.args.get("militar_id", type=int)
    secao_id = request.args.get("secao_id", type=int)
    companhia_id = request.args.get("companhia_id", type=int)
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    query = FatoObservado.query.join(Militar, FatoObservado.militar_id == Militar.id).filter(
        FatoObservado.status == "Publicado"
    )

    if militar_id:
        query = query.filter(FatoObservado.militar_id == militar_id)

    if secao_id:
        query = query.filter(Militar.id_secao == secao_id)

    if companhia_id:
        query = query.filter(Militar.id_companhia == companhia_id)

    query = aplicar_escopo_militares(query, current_user, Militar)

    if data_inicio:
        query = query.filter(FatoObservado.data_registro >= datetime.strptime(data_inicio, "%Y-%m-%d"))

    if data_fim:
        fim = datetime.strptime(data_fim, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(FatoObservado.data_registro <= fim)

    fatos = query.order_by(
        Militar.nome_guerra.asc(),
        FatoObservado.data_registro.desc()
    ).all()

    militares_query = Militar.query.filter_by(ativo=True).order_by(Militar.nome_guerra.asc())
    militares_query = aplicar_escopo_militares(militares_query, current_user, Militar)
    militares = militares_query.all()
    secoes = Secao.query.order_by(Secao.nome.asc()).all()
    companhias = Companhia.query.filter_by(ativa=True).order_by(Companhia.nome.asc()).all()

    return render_template(
        "fo/historico_geral.html",
        fatos=fatos,
        militares=militares,
        secoes=secoes,
        companhias=companhias,
        militar_id=militar_id,
        secao_id=secao_id,
        companhia_id=companhia_id,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


# =========================
# OFICIAIS - DISPENSAS
# =========================

@fo_bp.route("/dispensas", methods=["GET", "POST"])
@login_required
@oficial_requerido
def dispensas():
    if request.method == "POST":
        militar_id = request.form.get("militar_id", type=int)
        data_inicio = datetime.strptime(request.form.get("data_inicio"), "%Y-%m-%d").date()
        data_fim = datetime.strptime(request.form.get("data_fim"), "%Y-%m-%d").date()

        if data_fim < data_inicio:
            flash("A data final da dispensa não pode ser anterior à data inicial.", "danger")
            return redirect(url_for("fo.dispensas"))

        militar = Militar.query.get_or_404(militar_id)
        if not militar_no_escopo(current_user, militar):
            flash("Militar fora do seu nível de acesso.", "danger")
            return redirect(url_for("fo.dispensas"))

        dispensa = DispensaMilitar(
            militar_id=militar_id,
            registrado_por_id=current_user.id,
            tipo=request.form.get("tipo"),
            data_inicio=data_inicio,
            data_fim=data_fim,
            observacao=request.form.get("observacao"),
            ativo=True if request.form.get("ativo") == "on" else False
        )

        db.session.add(dispensa)
        db.session.flush()

        registrar_auditoria(
            usuario=current_user,
            acao="CADASTRAR_DISPENSA",
            entidade="DispensaMilitar",
            entidade_id=dispensa.id,
            detalhes=f"Dispensa cadastrada para militar ID {militar_id}"
        )

        db.session.commit()
        flash("Dispensa cadastrada com sucesso.", "success")
        return redirect(url_for("fo.dispensas"))

    militar_id = request.args.get("militar_id", type=int)
    somente_ativas = request.args.get("ativas", "1")

    query = DispensaMilitar.query.join(Militar, DispensaMilitar.militar_id == Militar.id)
    query = aplicar_escopo_militares(query, current_user, Militar)

    if militar_id:
        query = query.filter(DispensaMilitar.militar_id == militar_id)

    if somente_ativas == "1":
        query = query.filter(DispensaMilitar.ativo == True)

    dispensas = query.order_by(DispensaMilitar.data_inicio.desc()).all()
    militares_query = Militar.query.filter_by(ativo=True).order_by(Militar.nome_guerra.asc())
    militares_query = aplicar_escopo_militares(militares_query, current_user, Militar)
    militares = militares_query.all()

    return render_template(
        "fo/dispensas.html",
        dispensas=dispensas,
        militares=militares,
        militar_id=militar_id,
        somente_ativas=somente_ativas
    )


@fo_bp.route("/dispensas/<int:dispensa_id>/inativar", methods=["POST"])
@login_required
@oficial_requerido
def dispensa_inativar(dispensa_id):
    dispensa = DispensaMilitar.query.get_or_404(dispensa_id)
    if not militar_no_escopo(current_user, dispensa.militar):
        flash("Dispensa fora do seu nível de acesso.", "danger")
        return redirect(url_for("fo.dispensas"))

    dispensa.ativo = False

    registrar_auditoria(
        usuario=current_user,
        acao="INATIVAR_DISPENSA",
        entidade="DispensaMilitar",
        entidade_id=dispensa.id,
        detalhes=f"Dispensa inativada para {dispensa.militar.nome_guerra}"
    )

    db.session.commit()
    flash("Dispensa inativada com sucesso.", "warning")
    return redirect(url_for("fo.dispensas"))

@fo_bp.route("/dashboard")
@login_required
def dashboard():

    militares_query = aplicar_escopo_militares(Militar.query, current_user, Militar)
    total_militares = militares_query.count()

    fatos_base = FatoObservado.query.join(Militar, FatoObservado.militar_id == Militar.id)
    fatos_base = aplicar_escopo_militares(fatos_base, current_user, Militar)

    pendentes = fatos_base.filter(
        FatoObservado.status == "Pendente"
    ).count()

    publicados = fatos_base.filter(
        FatoObservado.status == "Publicado"
    ).count()

    total_positivos = fatos_base.filter(
        FatoObservado.status == "Publicado",
        FatoObservado.sinal == "POSITIVO"
    ).count()

    total_negativos = fatos_base.filter(
        FatoObservado.status == "Publicado",
        FatoObservado.sinal == "NEGATIVO"
    ).count()

    ultimos_fos = fatos_base.filter(
        FatoObservado.status != "Recusado"
    ).order_by(
        FatoObservado.data_registro.desc()
    ).limit(5).all()

    meus_fos = []
    saldo_pessoal = 0

    if usuario_tem_historico_pessoal(current_user):
        meus_fos = FatoObservado.query.filter_by(
            militar_id=current_user.militar_id,
            status="Publicado"
        ).order_by(
            FatoObservado.data_registro.desc()
        ).limit(5).all()

        positivos = sum(1 for f in meus_fos if f.sinal == "POSITIVO")
        negativos = sum(1 for f in meus_fos if f.sinal == "NEGATIVO")
        saldo_pessoal = positivos - negativos

    return render_template(
        "fo/dashboard.html",
        total_militares=total_militares,
        pendentes=pendentes,
        publicados=publicados,
        total_positivos=total_positivos,
        total_negativos=total_negativos,
        ultimos_fos=ultimos_fos,
        meus_fos=meus_fos,
        saldo_pessoal=saldo_pessoal
    )

@fo_bp.route("/admin/auditoria")
@login_required
@permissao_requerida("ADMIN")
def admin_auditoria():
    auditorias = Auditoria.query.order_by(
        Auditoria.data_hora.desc()
    ).limit(200).all()

    return render_template(
        "fo/admin_auditoria.html",
        auditorias=auditorias
    )