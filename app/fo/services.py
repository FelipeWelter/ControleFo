from datetime import datetime
from app.extensions import db
from .models import FatoObservado, HistoricoEdicaoFO
from .permissions import pode_lancar_fo_para
from flask import abort, flash
from .auditoria import registrar_auditoria

def criar_fato_observado(usuario_logado, militar_alvo, tipo_fato, descricao):
    if not pode_lancar_fo_para(usuario_logado, militar_alvo):
        flash("Você não possui permissão hierárquica para lançar FO para este militar.", "danger")
        return None

    descricao = descricao.strip() if descricao else ""

    fato = FatoObservado(
        militar_id=militar_alvo.id,
        cadastrador_id=usuario_logado.id,
        tipo_de_fato_id=tipo_fato.id,
        sinal=tipo_fato.sinal,
        pontos=1,
        descricao=descricao,
        status="Pendente",
        data_registro=datetime.utcnow()
    )

    db.session.add(fato)
    db.session.flush()

    registrar_auditoria(
        usuario_logado,
        "CRIAR_FO",
        "FatoObservado",
        fato.id,
        detalhes=f"FO criada para {militar_alvo.nome_guerra}"
    )

    db.session.commit()
    return fato

def aprovar_fato(fato, homologador):
    fato.status = "Publicado"
    fato.homologador_id = homologador.id
    fato.data_homologacao = datetime.utcnow()
    registrar_auditoria(
    usuario=homologador,
    acao="HOMOLOGAR_FO",
    entidade="FatoObservado",
    entidade_id=fato.id,
    detalhes=f"FO homologada"
    )
    db.session.commit()
    return fato

def recusar_fato(fato, homologador, justificativa):
    if not justificativa or not justificativa.strip():
        abort(400, description="A justificativa para recusa é obrigatória.")

    fato.status = "Anulado"
    fato.homologador_id = homologador.id
    fato.justificativa_recusa = justificativa.strip()
    fato.data_homologacao = datetime.utcnow()
    registrar_auditoria(
    usuario=homologador,
    acao="RECUSAR_FO",
    entidade="FatoObservado",
    entidade_id=fato.id,
    detalhes=justificativa
    )
    db.session.commit()
    return fato

def editar_fato(fato, editor, nova_descricao):
    
    nova_descricao = nova_descricao.strip() if nova_descricao else ""

    if fato.descricao != nova_descricao:
        historico = HistoricoEdicaoFO(
            fato_id=fato.id,
            editor_id=editor.id,
            descricao_antiga=fato.descricao,
            descricao_nova=nova_descricao
        )
        db.session.add(historico)
        fato.descricao = nova_descricao
    registrar_auditoria(
        usuario=editor,
        acao="EDITAR_FO",
        entidade="FatoObservado",
        entidade_id=fato.id,
        detalhes="FO editada"
    )
    db.session.commit()
    return fato
