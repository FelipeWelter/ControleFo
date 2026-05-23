from datetime import datetime
from app.extensions import db
from .models import FatoObservado, HistoricoEdicaoFO
from .permissions import pode_lancar_fo_para
from flask import abort

def criar_fato_observado(usuario_logado, militar_alvo, tipo_fato, descricao):
    if not pode_lancar_fo_para(usuario_logado, militar_alvo):
        abort(403, description="Você não possui permissão hierárquica para lançar FO para este militar.")
    
    if not descricao or not descricao.strip():
        abort(400, description="A descrição do fato observado é obrigatória.")

    fato = FatoObservado(
        militar_id=militar_alvo.id,
        cadastrador_id=usuario_logado.id,
        tipo_de_fato_id=tipo_fato.id,
        sinal=tipo_fato.sinal,
        pontos=tipo_fato.pontos,
        descricao=descricao.strip(),
        status="Pendente",
        data_registro=datetime.utcnow()
    )

    db.session.add(fato)
    db.session.flush()  # Para obter o ID do fato antes de salvar as evidências
    db.session.commit()
    return fato

def aprovar_fato(fato, homologador):
    fato.status = "Publicado"
    fato.homologador_id = homologador.id
    fato.data_homologacao = datetime.utcnow()
    db.session.commit()
    return fato

def recusar_fato(fato, homologador, justificativa):
    if not justificativa or not justificativa.strip():
        abort(400, description="A justificativa para recusa é obrigatória.")

    fato.status = "Anulado"
    fato.homologador_id = homologador.id
    fato.justificativa_recusa = justificativa.strip()
    fato.data_homologacao = datetime.utcnow()
    db.session.commit()
    return fato

def editar_fato(fato, editor, nova_descricao):
    if not nova_descricao or not nova_descricao.strip():
        abort(400, description="A nova descrição do fato observado é obrigatória.")
    
    nova_descricao = nova_descricao.strip()

    if fato.descricao != nova_descricao:
        historico = HistoricoEdicaoFO(
            fato_id=fato.id,
            editor_id=editor.id,
            descricao_antiga=fato.descricao,
            descricao_nova=nova_descricao
        )
        db.session.add(historico)
        fato.descricao = nova_descricao
    
    db.session.commit()
    return fato
