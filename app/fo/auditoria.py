from flask import request

from app.extensions import db
from app.fo.models import Auditoria


def registrar_auditoria(
    usuario,
    acao,
    entidade,
    entidade_id=None,
    detalhes=None
):
    try:
        ip = (
            request.headers.get("X-Forwarded-For", request.remote_addr)
            or request.remote_addr
        )

        if ip and "," in ip:
            ip = ip.split(",")[0].strip()

    except RuntimeError:
        ip = None

    if not usuario:
        return

    registro = Auditoria(
        usuario_id=usuario.id,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        ip=ip,
        detalhes=detalhes
    )

    db.session.add(registro)