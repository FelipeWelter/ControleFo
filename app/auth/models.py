from datetime import datetime

from app.extensions import db


class SolicitacaoResetSenha(db.Model):
    __tablename__ = "solicitacoes_reset_senha"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False
    )
    identidade_informada = db.Column(db.String(30), nullable=False)
    observacao = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default="PENDENTE", nullable=False)
    solicitado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    analisado_em = db.Column(db.DateTime, nullable=True)
    analisado_por_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )

    usuario = db.relationship("Usuario", foreign_keys=[usuario_id])
    analisado_por = db.relationship("Usuario", foreign_keys=[analisado_por_id])
